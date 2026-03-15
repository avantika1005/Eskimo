from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
import os
import sys
import random

# Add backend to path to import models
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_path)

from models import Base, Student, Intervention
from llm_service import generate_explanation

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

FIRST_NAMES = ["Arun", "Priya", "Vijay", "Ananya", "Karthik", "Meera", "Rahul", "Sita", "Deepak", "Jasmin", "Sanjay", "Aavya", "Aditya", "Ishani", "Kavya", "Mohan", "Nisha", "Rohan", "Sneha", "Vikram", "Abhishek", "Divya", "Ganesh", "Jyoti", "Kiran", "Madhav", "Nehal", "Pranav", "Riya", "Sahil"]
LAST_NAMES = ["Kumar", "Sharma", "Singh", "Das", "R", "Iyer", "Bose", "Lakshmi", "Raj", "Kaur", "Gupta", "Verma", "Reddy", "Nair", "Patel", "Mehta", "Joshi", "Chopra", "Malhotra", "Kapoor"]
TOWNS = ["Kanchipuram", "Sriperumbudur", "Walajabad", "Uthiramerur", "Kundrathur", "Madurantakam", "Chengalpattu", "Tambaram", "Pallavaram", "Ambattur", "Avadi", "Ponneri", "Gummidipoondi", "Tiruvallur", "Poonamallee", "Tiruttani", "Arakkonam", "Vellore", "Ranipet", "Arcot", "Gudiyatham", "Ambur", "Vaniyambadi", "Tirupathur", "Krishnagiri", "Hosur", "Dharmapuri", "Tiruvannamalai", "Polur", "Arani", "Cheyyar", "Vandavasi", "Villupuram", "Tindivanam", "Gingee", "Kallakurichi", "Ulundurpet", "Salem", "Attur", "Mettur", "Namakkal", "Rasipuram", "Erode", "Bhavani", "Perundurai", "Tiruppur", "Avinashi", "Coimbatore", "Pollachi", "Mettu-palayam", "Udagamandalam", "Coonoor", "Kotagiri", "Gudalur", "Thiruchirappalli", "Srirangam", "Manapparai", "Thuraiyur", "Musiri", "Karur", "Kulithalai", "Perambalur", "Ariyalur", "Jayankondam", "Cuddalore", "Chidambaram", "Panruti", "Virudhachalam", "Neyveli", "Nagapattinam", "Mayiladuthurai", "Sirkazhi", "Tharangambadi", "Tiruvarur", "Mannargudi", "Thiruthuraipoondi", "Thanjavur", "Kumbakonam", "Pattukkottai", "Orathanadu", "Pudukkottai", "Aranthangi", "Madurai", "Melur", "Thirumangalam", "Usilampatti", "Dindigul", "Palani", "Oddanchatram", "Kodaikanal", "Theni", "Periyakulam", "Bodinayakanur", "Cumbum", "Virudhunagar", "Sivakasi", "Rajapalayam", "Aruppukkottai", "Sivagangai", "Karaikudi", "Devakottai", "Ramanathapuram", "Paramakudi", "Rameswaram", "Tirunelveli", "Palayamkottai", "Ambasamudram", "Tenkasi", "Sankarankovil", "Tuticorin", "Thoothukudi", "Kovilpatti", "Tiruchendur", "Kanyakumari", "Nagercoil", "Padmanabhapuram", "Kuzhithurai"]
SCHOOL_SUFFIXES = ["Govt Model School", "Panchayat Union School", "Excellence Academy", "Higher Secondary", "Matric Hr.Sec.School", "Zilla Parishad High School", "Christian Mission School", "Vidyalayam", "Public School", "Aided High School"]

# Generate 125 unique schools
SCHOOLS = []
for town in TOWNS:
    suffix = random.choice(SCHOOL_SUFFIXES)
    SCHOOLS.append(f"{town} {suffix}")
# Ensure at least 125 by adding more combinations if needed
while len(SCHOOLS) < 125:
    town = random.choice(TOWNS)
    suffix = random.choice(SCHOOL_SUFFIXES)
    name = f"{town} {suffix}"
    if name not in SCHOOLS:
        SCHOOLS.append(name)

GRADES = ["8th", "9th", "10th", "11th", "12th"]
FACTORS_LIST = ["Attendance", "Latest Exam Score", "Distance", "Midday Meal", "Sibling Dropout", "Behavioral", "Financial"]

ACTIONS = [
    "Parent–Teacher Meeting",
    "Attendance Monitoring",
    "Academic Counseling",
    "Peer Mentoring",
    "Extra Tutoring",
    "Weekly Progress Tracking",
    "Home Visit",
    "Scholarship Application",
    "Counselling Session"
]

TEACHERS = ["Admin", "Mr. Rajesh", "Ms. Lakshmi", "Mr. Sivakumar", "Ms. Anitha", "Mr. Murali"]

def seed():
    db = SessionLocal()
    
    print("Clearing existing data...")
    db.query(Intervention).delete()
    db.query(Student).delete()
    db.commit()
    
    print(f"Generating 500 student records across {len(SCHOOLS)} schools...")
    for i in range(1, 501):
        s_id = f"STU{1000 + i}"
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        school = random.choice(SCHOOLS)
        grade = random.choice(GRADES)
        
        # Determine risk level based on some randomized logic
        risk_roll = random.random()
        if risk_roll < 0.15:
            risk = "High"
            num_factors = random.randint(2, 3)
        elif risk_roll < 0.40:
            risk = "Medium"
            num_factors = random.randint(1, 2)
        else:
            risk = "Low"
            num_factors = 0
            
        factors = ", ".join(random.sample(FACTORS_LIST, num_factors)) if num_factors > 0 else ""
        
        att = round(random.uniform(55, 98), 1)
        score = round(random.uniform(35, 95), 1)
        dist = round(random.uniform(0.2, 8.0), 1)
        meal_pct = round(random.uniform(40, 100), 1)
        risk_score = round(random.uniform(10, 95), 1)
        
        # Adjust risk_level to match random score for consistency
        if risk_score > 75: risk = "High"
        elif risk_score > 40: risk = "Medium"
        else: risk = "Low"

        # Add explanation
        explanation = generate_explanation(
            student_name=name,
            score=int(risk_score),
            level=risk,
            top_factors=factors,
            attendance=att,
            exams=score,
            class_avg={"attendance": 82, "score": 68, "distance": 2.2, "meal": 75},
            benchmarks={"attendance": 88, "score": 74, "distance": 2.5, "meal": 85}
        )

        student = Student(
            student_id=s_id,
            name=name,
            school_name=school,
            block_name="Kanchipuram Central",
            district_name="Kanchipuram",
            grade_class=grade,
            attendance_pct=att,
            latest_exam_score=score,
            previous_exam_score=round(score - random.uniform(-10, 15), 1),
            distance_km=dist,
            meal_participation_pct=meal_pct,
            sibling_dropout=random.choice([True, False, False, False]), # 25% chance
            risk_score=risk_score,
            risk_level=risk,
            top_factors=factors,
            llm_explanation=explanation
        )
        db.add(student)
        db.commit()
        db.refresh(student)

        # Generate interventions for some students (higher probability for High/Medium risk)
        inv_prob = 0.9 if risk == "High" else (0.6 if risk == "Medium" else 0.2)
        
        if random.random() < inv_prob:
            num_inv = random.randint(1, 5)
            for j in range(num_inv):
                action = random.choice(ACTIONS)
                is_eval = random.choice([True, True, False]) # 66% chance of being evaluated
                
                baseline_att = round(random.uniform(50, 85), 1)
                baseline_score = round(random.uniform(30, 75), 1)
                baseline_risk = round(random.uniform(40, 95), 1)
                
                # Outcome (if evaluated)
                outcome_att = round(baseline_att + random.uniform(-8, 20), 1) if is_eval else None
                outcome_score = round(baseline_score + random.uniform(-10, 25), 1) if is_eval else None
                outcome_risk = round(baseline_risk - random.uniform(-5, 30), 1) if is_eval else None
                
                status = "Pending"
                if is_eval:
                    if outcome_att > baseline_att + 3:
                        status = "Improved"
                    elif outcome_att < baseline_att - 3:
                        status = "Declined"
                    else:
                        status = "No Change"

                inv = Intervention(
                    student_id=student.id,
                    date=(datetime.datetime.now() - datetime.timedelta(days=random.randint(5, 120))).strftime("%Y-%m-%d"),
                    action=action,
                    teacher_name=random.choice(TEACHERS),
                    notes=f"Automated risk mitigation step for {name}. Focus on {action}.",
                    baseline_attendance=baseline_att,
                    baseline_score=baseline_score,
                    baseline_meal_pct=round(random.uniform(60, 95), 1),
                    baseline_risk_score=baseline_risk,
                    outcome_attendance=outcome_att,
                    outcome_score=outcome_score,
                    outcome_risk_score=outcome_risk,
                    outcome_status=status,
                    is_evaluated=is_eval
                )
                db.add(inv)
    
    db.commit()
    print(f"Database successfully seeded with 120 students and varied intervention histories.")
    db.close()

if __name__ == "__main__":
    seed()
