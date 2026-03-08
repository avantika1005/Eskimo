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

from models import Base, Student, Intervention
from ml_model import model_instance
from llm_service import generate_explanation, generate_parent_communication

# DB Setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
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
        
    # Clear existing data to show only current CSV students
    db.query(Intervention).delete()
    db.query(Student).delete()
    db.commit()

    content = await file.read()
    s = str(content, 'utf-8')
    data = StringIO(s)
    df = pd.read_csv(data)
    
    # Required columns basic check
    required_cols = ['Student ID', 'Student Name', 'Class / Grade', 'Attendance Percentage', 
                     'Latest Exam Score', 'Previous Exam Score', 'Distance from School (km)', 
                     'Midday Meal Participation (Yes/No)', 'Sibling Dropout History (Yes/No)']
                     
    if not all(col in df.columns for col in required_cols):
        raise HTTPException(status_code=400, detail="Missing required columns in CSV")
        
    for index, row in df.iterrows():
        student_data = {
            'attendance_pct': float(row['Attendance Percentage']),
            'latest_exam_score': float(row['Latest Exam Score']),
            'previous_exam_score': float(row['Previous Exam Score']),
            'distance_km': float(row['Distance from School (km)']),
            'midday_meal': str(row['Midday Meal Participation (Yes/No)']).strip().lower() == 'yes',
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
        else:
            avg_att, avg_score, avg_dist = student_data['attendance_pct'], student_data['latest_exam_score'], student_data['distance_km']

        class_avg = {"attendance": round(avg_att, 1), "score": round(avg_score, 1), "distance": round(avg_dist, 1)}
        benchmarks = {"attendance": 88, "score": 74, "distance": 2.5}

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
    
@app.get("/api/students/{id}")
def get_student_detail(id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    interventions = db.query(Intervention).filter(Intervention.student_id == student.id).all()
    
    # Calculate cohort comparisons
    all_students = db.query(Student).all()
    avg_att = sum(s.attendance_pct for s in all_students) / len(all_students) if all_students else 0
    avg_score = sum(s.latest_exam_score for s in all_students) / len(all_students) if all_students else 0
    avg_dist = sum(s.distance_km for s in all_students) / len(all_students) if all_students else 0

    comparison = {
        "metrics": ["Attendance", "Exam Score", "Distance"],
        "student": [student.attendance_pct, student.latest_exam_score, student.distance_km],
        "class_avg": [round(avg_att, 1), round(avg_score, 1), round(avg_dist, 1)],
        "benchmarks": [88, 74, 2.5]
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
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    inv = Intervention(student_id=id, date=payload.get("date"), action=payload.get("action"))
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv

# Serve frontend static files
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
