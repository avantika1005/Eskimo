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
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"LLM Error: {e}")
            return _generate_mock_explanation(student_name, score, level, top_factors, attendance)
    else:
        return _generate_mock_explanation(student_name, score, level, top_factors, attendance)

def generate_parent_communication(student_name: str, level: str, top_factors: str, language: str) -> str:
    """
    Generates a sensitive, plain-language message for parents in the specified language.
    Supported languages: English, Hindi, Tamil, Telugu, Kannada, Marathi.
    """
    prompt = f"""
    Draft a sensitive, plain-language message (suitable for a letter or WhatsApp) to a student's parents.
    The goal is to invite them for a supportive discussion about their child's progress without stigmatizing the student.
    
    Student Name: {student_name}
    Situation: The student is currently at {level} risk of dropping out.
    Key Concerns: {top_factors}
    Desired Tone: Supportive, cooperative, non-judgmental, and simple.
    Language: {language}
    
    The message should:
    1. Start with a warm greeting.
    2. Mention that the school values the student's presence.
    3. Gently mention that we've noticed some challenges (based on the concerns) and would like to help.
    4. Propose a meeting or a call to discuss how we can support the student together.
    5. End with a positive note.
    
    Provide ONLY the message content in {language}.
    """
    
    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a compassionate school counselor and teacher communicator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"LLM Parent Comm Error: {e}")
            return _generate_mock_parent_comm(student_name, level, language)
    else:
        return _generate_mock_parent_comm(student_name, level, language)

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

def _generate_mock_parent_comm(student_name: str, level: str, language: str) -> str:
    # Basic English fallback for mock if key is missing or error occurs
    messages = {
        "English": f"Dear Parent, We value {student_name}'s participation in our school. We've noticed some areas where they might need extra support and would love to discuss how we can work together for their success. Are you available for a brief chat?",
        "Tamil": f"அன்புள்ள பெற்றோரே, எங்கள் பள்ளியில் {student_name} இருப்பதை நாங்கள் மதிக்கிறோம். அவர்களுக்கு கூடுதல் ஆதரவு தேவைப்படும் சில பகுதிகளை நாங்கள் கவனித்துள்ளோம். அவர்களின் வெற்றிக்காக நாம் எவ்வாறு இணைந்து செயல்படலாம் என்பதைப் பற்றி விவாதிக்க விரும்புகிறோம். நீங்கள் ஒரு சிறிய உரையாடலுக்கு தயாரா?",
        "Hindi": f"प्रिय अभिभावक, हम अपने स्कूल में {student_name} की भागीदारी को महत्व देते हैं। हमने कुछ ऐसे क्षेत्रों पर ध्यान दिया है जहाँ उन्हें अतिरिक्त सहायता की आवश्यकता हो सकती है। हम चर्चा करना चाहेंगे कि हम उनकी सफलता के लिए मिलकर कैसे काम कर सकते हैं। क्या आप बातचीत के लिए उपलब्ध हैं?"
    }
    return messages.get(language, messages["English"])
