import os
import random
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = None
if os.getenv("OPENAI_API_KEY"):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_explanation(student_name: str, score: int, level: str, top_factors: str, attendance: float, exams: float, class_avg: dict = None, benchmarks: dict = None) -> str:
    avg_text = ""
    if class_avg and benchmarks:
        avg_text = f"""
        Comparison Data:
        - Attendance: Student {attendance}%, Class Avg {class_avg.get('attendance') or 'N/A'}%, Benchmark {benchmarks.get('attendance') or '88'}%
        - Exam Score: Student {exams}, Class Avg {class_avg.get('score') or 'N/A'}, Benchmark {benchmarks.get('score') or '74'}
        - Distance: Student {class_avg.get('student_dist') or 'N/A'}km, Class Avg {class_avg.get('distance') or 'N/A'}km, Benchmark {benchmarks.get('distance') or '2.5'}km
        """

    prompt = f"""
    Explain the student's dropout risk in simple language for a school teacher.
    Avoid technical terms. Explain the top contributing factors clearly.
    
    Student: {student_name}
    Risk Level: {level}
    Risk Score: {score}/100
    Top Factors: {top_factors}
    Attendance: {attendance}%
    Latest Exam: {exams}
    {avg_text}
    
    When explaining, compare the student to the class average and the successful student benchmarks to provide context.
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
            return _generate_mock_explanation(student_name, score, level, top_factors, attendance, class_avg, benchmarks)
    else:
        return _generate_mock_explanation(student_name, score, level, top_factors, attendance, class_avg, benchmarks)

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
    
    Provide ONLY the message content in {language}. Provide a unique, creative variation if possible.
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
            return _generate_mock_parent_comm(student_name, level, language, top_factors)
    else:
        return _generate_mock_parent_comm(student_name, level, language, top_factors)

def _generate_mock_explanation(student_name: str, score: int, level: str, top_factors: str, attendance: float, class_avg: dict = None, benchmarks: dict = None) -> str:
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
        
    if class_avg and benchmarks:
        avg_att = class_avg.get('attendance', 0)
        if attendance < avg_att:
            explanation += f" Specifically, their attendance of {attendance}% is below the class average of {avg_att}%."
        
        bench_score = benchmarks.get('score', 0)
        # Note: exams score is not passed to this helper yet, let's keep it simple or update signature
        
    return explanation

def _generate_mock_parent_comm(student_name: str, level: str, language: str, top_factors: str = "") -> str:
    factors = top_factors.lower() if top_factors else "general concerns"
    
    # Simple localization for factors in mock
    localized_factors = {
        "English": factors,
        "Tamil": "வருகைப்பதிவு அல்லது பாடங்களில் சவால்கள்" if "attendance" in factors or "exam" in factors else "சில பொதுவான சவால்கள்",
        "Hindi": "उपस्थिति या पढ़ाई में चुनौतियाँ" if "attendance" in factors or "exam" in factors else "कुछ सामान्य चुनौतियाँ"
    }
    
    factor_text = localized_factors.get(language, localized_factors["English"])

    templates = {
        "English": [
            f"Dear Parent, We value {student_name}'s participation in our school. We've noticed some challenges regarding {factor_text}, and we would love to discuss how we can work together to support them. Are you available for a brief chat?",
            f"Hello, We are reaching out because we care about {student_name}'s success. We've observed some hurdles with {factor_text} lately. Could we meet to find a way to help them improve together?",
            f"Dear Parent, {student_name} is an important part of our class. To help them reach their full potential, we'd like to talk about {factor_text}. When would be a good time for a supportive discussion?"
        ],
        "Tamil": [
            f"அன்புள்ள பெற்றோரே, எங்கள் பள்ளியில் {student_name} இருப்பதை நாங்கள் மதிக்கிறோம். {factor_text} தொடர்பாக சில சவால்களை நாங்கள் கவனித்துள்ளோம். அவர்களுக்கு ஆதரவளிக்க நாம் எவ்வாறு இணைந்து செயல்படலாம் என்பதைப் பற்றி விவாதிக்க விரும்புகிறோம். நீங்கள் ஒரு சிறிய உரையாடலுக்கு தயாரா?",
            f"வணக்கம், {student_name}-ன் வெற்றியில் நாங்கள் அக்கறை கொண்டுள்ளோம். சமீபகாலமாக {factor_text} தொடர்பான சில தடைகளை நாங்கள் கவனித்தோம். அவர்களை மேம்படுத்த நாம் எவ்வாறு உதவலாம் என்பதைக் கண்டறிய நாம் சந்திக்கலாமா?",
            f"அன்புள்ள பெற்றோரே, {student_name} எங்கள் வகுப்பின் ஒரு முக்கிய அங்கமாகும். அவர்கள் முழு திறனை அடைய உதவ, {factor_text} பற்றி நாங்கள் பேச விரும்புகிறோம். ஆதரவான கலந்துரையாடலுக்கு எப்போது சரியான நேரமாக இருக்கும்?"
        ],
        "Hindi": [
            f"प्रिय अभिभावक, हम अपने स्कूल में {student_name} की भागीदारी को महत्व देते हैं। हमने {factor_text} के संबंध में कुछ चुनौतियों पर ध्यान दिया है, और हम उनके समर्थन के लिए मिलकर काम करने पर चर्चा करना चाहेंगे। क्या आप बातचीत के लिए उपलब्ध हैं?",
            f"नमस्ते, हम {student_name} की सफलता की परवाह करते हैं। हमने हाल ही में {factor_text} के साथ कुछ बाधाएं देखी हैं। क्या हम उन्हें एक साथ बेहतर बनाने का रास्ता खोजने के लिए मिल सकते हैं?",
            f"प्रिय अभिभावक, {student_name} हमारी कक्षा का एक महत्वपूर्ण हिस्सा है। उन्हें उनकी पूरी क्षमता तक पहुँचने में मदद करने के लिए, हम {factor_text} के बारे में बात करना चाहेंगे। एक सहायक चर्चा के लिए अच्छा समय कब होगा?"
        ]
    }
    
    options = templates.get(language, templates["English"])
    return random.choice(options)
