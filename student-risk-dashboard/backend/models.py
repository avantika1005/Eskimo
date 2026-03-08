from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    grade_class = Column(String)
    attendance_pct = Column(Float)
    latest_exam_score = Column(Float)
    previous_exam_score = Column(Float)
    distance_km = Column(Float)
    midday_meal = Column(Boolean)
    meal_participation_pct = Column(Float, default=0.0)
    sibling_dropout = Column(Boolean)
    
    # ML predicted fields
    risk_score = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True) # Low, Medium, High
    top_factors = Column(String, nullable=True) # comma separated
    llm_explanation = Column(String, nullable=True)

class Intervention(Base):
    __tablename__ = 'interventions'
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.id'))

    # Core metadata about the intervention
    date = Column(String)                        # stored as ISO date string (YYYY-MM-DD)
    intervention_type = Column(String)           # e.g. Home Visit, Counselling
    teacher_name = Column(String)
    notes = Column(String, nullable=True)

    # Baseline snapshot of student indicators at the time of logging
    baseline_attendance_pct = Column(Float)
    baseline_exam_score = Column(Float)
    baseline_midday_meal = Column(Boolean)
    baseline_meal_participation_pct = Column(Float)
    baseline_risk_score = Column(Float)
