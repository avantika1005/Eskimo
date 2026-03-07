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
    date = Column(String)
    action = Column(String)
