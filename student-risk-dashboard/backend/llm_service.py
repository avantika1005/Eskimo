import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = None
if os.getenv("OPENAI_API_KEY"):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_explanation(student_name: str, score: int, level: str, top_factors: str, attendance: float, exams: float) -> str:
    prompt = f"""
    Explain the student's dropout risk in simple language for a school teacher.
    Avoid technical terms. Explain the top contributing factors clearly.
    
    Student: {student_name}
    Risk Level: {level}
    Risk Score: {score}/100
    Top Factors: {top_factors}
    Attendance: {attendance}%
    Latest Exam: {exams}
    """
    
    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful educational assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"LLM Error: {e}")
            return _generate_mock_explanation(student_name, score, level, top_factors, attendance)
    else:
        return _generate_mock_explanation(student_name, score, level, top_factors, attendance)

def _generate_mock_explanation(student_name: str, score: int, level: str, top_factors: str, attendance: float) -> str:
    factors_list = [f.strip() for f in top_factors.split(",")] if top_factors else []
    
    if level == "Low":
        return f"{student_name} is performing well and shows a very low risk of dropping out. They have stable attendance and academic performance."
        
    explanation = f"{student_name}'s risk score is {level.lower()} mainly because of "
    
    if len(factors_list) == 1:
        explanation += f"{factors_list[0].lower()}."
    elif len(factors_list) == 2:
        explanation += f"{factors_list[0].lower()} and {factors_list[1].lower()}."
    else:
        explanation += f"{factors_list[0].lower()}, {factors_list[1].lower()}, and other factors."
        
    if "Attendance" in top_factors and attendance < 75:
        explanation += f" Specifically, attendance has dropped to {attendance}% which may hinder their learning."
        
    return explanation
