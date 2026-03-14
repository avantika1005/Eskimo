import pytest
import requests

@pytest.mark.parametrize(
    "student_id,language",
    [
        (1, "Tamil"),
        (2, "English"),
        (1, "Hindi"),
    ],
)
def test_communication(student_id, language):
    url = f"http://localhost:8000/api/students/{student_id}/parent-communication?language={language}"
    print(f"Testing for Student ID {student_id} in {language}...")

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"Student: {data['student_name']}")
            print(f"Language: {data['language']}")
            print("-" * 20)
            print(data['message'])
            print("-" * 20)
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Connection failed: {e}")


if __name__ == "__main__":
    # Test for a few students and languages
    # Assuming students 1 and 2 exist and are Medium/High risk based on sample data
    test_communication(1, "Tamil")
    test_communication(2, "English")
    test_communication(1, "Hindi")
