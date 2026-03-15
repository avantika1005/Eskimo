import sys
import os

# Add backend folder to Python path
sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "student-risk-dashboard", "backend")
)

from main import app
