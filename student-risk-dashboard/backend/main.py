from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from io import StringIO
import pandas as pd
import os
import uuid
import datetime

from models import Base, Student, Intervention
from ml_model import model_instance
from llm_service import generate_explanation, generate_parent_communication

# DB Setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ensure database schema is always up to date; we aggressively drop+recreate when uploading new CSVs
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="Student Risk Dashboard API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints
@app.get("/api/ping")
def ping():
    return {"status": "ok"}

@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")
        
    # wipe & recreate schema so that any model changes (e.g. new intervention fields) are applied
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Clear any in-memory db session state
    db.expire_all()

    content = await file.read()
    s = str(content, 'utf-8')
    data = StringIO(s)
    df = pd.read_csv(data)
    
    # Required columns basic check
    required_cols = ['Student ID', 'Student Name', 'Class / Grade', 'Attendance Percentage', 
                     'Latest Exam Score', 'Previous Exam Score', 'Distance from School (km)', 
                     'Midday Meal Participation (Yes/No)', 'Midday Meal Participation Rate (%)',
                     'Sibling Dropout History (Yes/No)']
                     
    if not all(col in df.columns for col in required_cols):
        raise HTTPException(status_code=400, detail="Missing required columns in CSV")
        
    for index, row in df.iterrows():
        student_data = {
            'attendance_pct': float(row['Attendance Percentage']),
            'latest_exam_score': float(row['Latest Exam Score']),
            'previous_exam_score': float(row['Previous Exam Score']),
            'distance_km': float(row['Distance from School (km)']),
            'midday_meal': str(row['Midday Meal Participation (Yes/No)']).strip().lower() == 'yes',
            'meal_participation_pct': float(row['Midday Meal Participation Rate (%)']),
            'sibling_dropout': str(row['Sibling Dropout History (Yes/No)']).strip().lower() == 'yes'
        }
        
        # ML Prediction
        pred = model_instance.predict_risk(student_data)
        
        # Calculate current class averages for context
        all_students = db.query(Student).all()
        if all_students:
            avg_att = sum(s.attendance_pct for s in all_students) / len(all_students)
            avg_score = sum(s.latest_exam_score for s in all_students) / len(all_students)
            avg_dist = sum(s.distance_km for s in all_students) / len(all_students)
            avg_meal = sum(s.meal_participation_pct for s in all_students) / len(all_students)
        else:
            avg_att, avg_score, avg_dist, avg_meal = student_data['attendance_pct'], student_data['latest_exam_score'], student_data['distance_km'], student_data['meal_participation_pct']

        class_avg = {
            "attendance": round(avg_att, 1), 
            "score": round(avg_score, 1), 
            "distance": round(avg_dist, 1),
            "meal": round(avg_meal, 1)
        }
        benchmarks = {"attendance": 88, "score": 74, "distance": 2.5, "meal": 85}

        # LLM Explanation
        explanation = generate_explanation(
            student_name=row['Student Name'],
            score=pred['score'],
            level=pred['level'],
            top_factors=pred['top_factors'],
            attendance=student_data['attendance_pct'],
            exams=student_data['latest_exam_score'],
            class_avg=class_avg,
            benchmarks=benchmarks
        )
        
        # Update or create student
        student = db.query(Student).filter(Student.student_id == str(row['Student ID'])).first()
        if not student:
            student = Student(student_id=str(row['Student ID']))
            db.add(student)
            
        student.name = row['Student Name']
        student.grade_class = str(row['Class / Grade'])
        student.attendance_pct = student_data['attendance_pct']
        student.latest_exam_score = student_data['latest_exam_score']
        student.previous_exam_score = student_data['previous_exam_score']
        student.distance_km = student_data['distance_km']
        student.midday_meal = student_data['midday_meal']
        student.meal_participation_pct = student_data['meal_participation_pct']
        student.sibling_dropout = student_data['sibling_dropout']
        
        student.risk_score = pred['score']
        student.risk_level = pred['level']
        student.top_factors = pred['top_factors']
        student.llm_explanation = explanation
        
    db.commit()
    return {"message": "Data processed successfully"}


@app.get("/api/students")
def get_students(risk_level: str = None, grade_class: str = None, attendance: str = None, db: Session = Depends(get_db)):
    query = db.query(Student)
    if risk_level and risk_level.lower() != 'all':
        query = query.filter(Student.risk_level == risk_level)
    if grade_class and grade_class.lower() != 'all':
        query = query.filter(Student.grade_class == grade_class)
    
    students = query.all()
    
    # post process attendance filter since it's an inequality
    if attendance and attendance != 'All':
        if attendance == '< 70%':
            students = [s for s in students if s.attendance_pct < 70]
        elif attendance == '70% - 90%':
            students = [s for s in students if 70 <= s.attendance_pct <= 90]
        elif attendance == '> 90%':
            students = [s for s in students if s.attendance_pct > 90]
            
    return students
    
def evaluate_intervention(inv: Intervention, student: Student):
    """Return a dictionary describing the 30‑day outcome for an intervention.
    If 30 days have not passed yet the dictionary has `evaluated: False` and
    a countdown. Otherwise it contains the change and status for each tracked
    indicator."""
    out = {}
    try:
        base_date = datetime.datetime.strptime(inv.date, "%Y-%m-%d")
    except Exception:
        out["evaluated"] = False
        out["error"] = "invalid date format"
        return out

    delta = datetime.datetime.now() - base_date
    if delta.days < 30:
        out["evaluated"] = False
        out["days_until_evaluation"] = 30 - delta.days
        return out

    # compute changes
    out["evaluated"] = True
    # attendance
    att_change = None
    if inv.baseline_attendance_pct is not None:
        att_change = student.attendance_pct - inv.baseline_attendance_pct
        out["attendance_change"] = round(att_change, 1)
        if att_change > 0:
            out["attendance_status"] = "Improved"
        elif att_change < 0:
            out["attendance_status"] = "Declined"
        else:
            out["attendance_status"] = "No Change"

    # exam score
    score_change = None
    if inv.baseline_exam_score is not None:
        score_change = student.latest_exam_score - inv.baseline_exam_score
        out["score_change"] = round(score_change, 1)
        if score_change > 0:
            out["score_status"] = "Improved"
        elif score_change < 0:
            out["score_status"] = "Declined"
        else:
            out["score_status"] = "No Change"

    # risk
    if inv.baseline_risk_score is not None:
        # lower risk is better
        if student.risk_score < inv.baseline_risk_score:
            out["risk_status"] = "Improved"
        elif student.risk_score > inv.baseline_risk_score:
            out["risk_status"] = "Declined"
        else:
            out["risk_status"] = "No Change"

    # midday meal participation (bool)
    if inv.baseline_midday_meal is not None:
        if student.midday_meal and not inv.baseline_midday_meal:
            out["meal_status"] = "Improved"
        elif not student.midday_meal and inv.baseline_midday_meal:
            out["meal_status"] = "Declined"
        else:
            out["meal_status"] = "No Change"

    return out


@app.get("/api/students/{id}")
def get_student_detail(id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    raw_interventions = db.query(Intervention).filter(Intervention.student_id == student.id).all()
    interventions = []
    for inv in raw_interventions:
        inv_dict = {
            "id": inv.id,
            "date": inv.date,
            "intervention_type": inv.intervention_type,
            "teacher_name": inv.teacher_name,
            "notes": inv.notes,
            "baseline_attendance_pct": inv.baseline_attendance_pct,
            "baseline_exam_score": inv.baseline_exam_score,
            "baseline_midday_meal": inv.baseline_midday_meal,
            "baseline_meal_participation_pct": inv.baseline_meal_participation_pct,
            "baseline_risk_score": inv.baseline_risk_score,
        }
        # attach evaluation/outcome info if available
        inv_dict.update(evaluate_intervention(inv, student))
        interventions.append(inv_dict)

    # Calculate cohort comparisons
    all_students = db.query(Student).all()
    avg_att = sum(s.attendance_pct for s in all_students) / len(all_students) if all_students else 0
    avg_score = sum(s.latest_exam_score for s in all_students) / len(all_students) if all_students else 0
    avg_dist = sum(s.distance_km for s in all_students) / len(all_students) if all_students else 0
    avg_meal = sum(s.meal_participation_pct for s in all_students) / len(all_students) if all_students else 0

    comparison = {
        "metrics": ["Attendance", "Exam Score", "Distance", "Meal Participation"],
        "student": [student.attendance_pct, student.latest_exam_score, student.distance_km, student.meal_participation_pct],
        "class_avg": [round(avg_att, 1), round(avg_score, 1), round(avg_dist, 1), round(avg_meal, 1)],
        "benchmarks": [88, 74, 2.5, 85]
    }

    return {
        "student": student,
        "interventions": interventions,
        "comparison": comparison
    }

@app.get("/api/students/{id}/parent-communication")
def get_parent_communication(id: int, language: str = "English", db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if student.risk_level not in ["Medium", "High"]:
        raise HTTPException(status_code=400, detail="Parent communication is only available for students at Medium or High risk.")
        
    message = generate_parent_communication(
        student_name=student.name,
        level=student.risk_level,
        top_factors=student.top_factors,
        language=language
    )
    
    return {
        "student_id": student.id,
        "student_name": student.name,
        "language": language,
        "message": message
    }

@app.post("/api/students/{id}/interventions")
def log_intervention(id: int, payload: dict, db: Session = Depends(get_db)):
    """Record a new intervention for a student, capturing baseline indicators."""
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # if no date supplied, use today's date
    date_str = payload.get("date")
    if not date_str:
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")

    inv = Intervention(
        student_id=id,
        date=date_str,
        intervention_type=payload.get("intervention_type"),
        teacher_name=payload.get("teacher_name"),
        notes=payload.get("notes"),
        baseline_attendance_pct=student.attendance_pct,
        baseline_exam_score=student.latest_exam_score,
        baseline_midday_meal=student.midday_meal,
        baseline_meal_participation_pct=student.meal_participation_pct,
        baseline_risk_score=student.risk_score,
    )

    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv

# --- intervention library ------------------------------------------------
INTERVENTION_LIBRARY = [
    {
        "name": "Home Visit",
        "description": "Teacher or counselor visits the student’s home to better understand barriers.",
        "evidence_source": "Education Research Study",
        "risk_factors": "Low attendance",
        "typical_impact": "+8–12% attendance" 
    },
    {
        "name": "Counselling Session",
        "description": "One-on-one academic or emotional counselling with a trained staff member.",
        "evidence_source": "School Mental Health Framework",
        "risk_factors": "Academic decline, disengagement",
        "typical_impact": "+5–10% exam score" 
    },
    {
        "name": "Peer Buddy Assignment",
        "description": "Pairing the student with a peer mentor for support and accountability.",
        "evidence_source": "School Retention Programs",
        "risk_factors": "Student disengagement",
        "typical_impact": "+3–7% attendance" 
    },
    {
        "name": "Parent Meeting",
        "description": "Structured discussion with parents/guardians to align on next steps.",
        "evidence_source": "Family Engagement Study",
        "risk_factors": "Various",
        "typical_impact": "Varies" 
    },
    {
        "name": "Academic Support Program",
        "description": "Extra tutoring or remedial classes focusing on weak subjects.",
        "evidence_source": "Government Education Report",
        "risk_factors": "Poor exam performance",
        "typical_impact": "+6–15% exam score" 
    }
]

@app.get("/api/interventions/library")
def get_intervention_library():
    # in a more mature implementation this would come from a table, but a
    # hardcoded list suffices for demonstration purposes
    return INTERVENTION_LIBRARY


@app.get("/api/analytics/interventions")
def intervention_analytics(db: Session = Depends(get_db)):
    """Return aggregate statistics about interventions that have reached their
    30‑day evaluation period."""
    all_invs = db.query(Intervention).all()
    summary = {}
    counts_by_type = {}
    attendance_changes = {}
    total_evaluated = 0

    for inv in all_invs:
        # compute outcome; re-use evaluation helper but we don't need dict
        eval_info = evaluate_intervention(inv, db.query(Student).filter(Student.id == inv.student_id).first())
        if not eval_info.get("evaluated"):
            continue
        total_evaluated += 1
        typ = inv.intervention_type or "<unknown>"
        counts_by_type.setdefault(typ, {"total": 0, "improved": 0})
        counts_by_type[typ]["total"] += 1
        # consider an intervention successful if attendance OR score OR risk improved
        if eval_info.get("attendance_status") == "Improved" or eval_info.get("score_status") == "Improved" or eval_info.get("risk_status") == "Improved":
            counts_by_type[typ]["improved"] += 1
        # accumulate attendance changes for average
        if "attendance_change" in eval_info:
            attendance_changes.setdefault(typ, []).append(eval_info["attendance_change"])

    # build response
    result = []
    for typ, vals in counts_by_type.items():
        avg_att = None
        if attendance_changes.get(typ):
            avg_att = round(sum(attendance_changes[typ]) / len(attendance_changes[typ]), 1)
        success_rate = round((vals["improved"] / vals["total"]) * 100, 1) if vals["total"] > 0 else 0
        result.append({
            "intervention": typ,
            "success_rate": success_rate,
            "avg_attendance_improvement": avg_att
        })

    summary = {
        "total_evaluated": total_evaluated,
        "by_type": result
    }
    return summary

# Serve frontend static files
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
