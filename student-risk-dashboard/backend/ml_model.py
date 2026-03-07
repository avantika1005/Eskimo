import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import random

class DropoutModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False
        self.feature_names = [
            'attendance_pct', 
            'latest_exam_score', 
            'previous_exam_score',
            'distance_km',
            'midday_meal',
            'sibling_dropout'
        ]
        
    def _generate_synthetic_data(self, n=500):
        # generate simple synthetic data for initial training
        np.random.seed(42)
        random.seed(42)
        
        data = {
            'attendance_pct': np.random.uniform(40, 100, n),
            'latest_exam_score': np.random.uniform(30, 100, n),
            'previous_exam_score': np.random.uniform(30, 100, n),
            'distance_km': np.random.uniform(1, 15, n),
            'midday_meal': np.random.choice([0, 1], n),
            'sibling_dropout': np.random.choice([0, 1], n, p=[0.8, 0.2]),
        }
        df = pd.DataFrame(data)
        
        # Determine dropout (highly simplified logic for MVP)
        # High risk if attendance < 65, scores declining or low, sibling dropout
        risk = (
            ((df['attendance_pct'] < 70).astype(int) * 2) +
            ((df['latest_exam_score'] < 50).astype(int) * 1.5) +
            (df['sibling_dropout'] * 2) +
            ((df['distance_km'] > 8).astype(int) * 1)
        )
        
        # Probability of dropout
        prob = np.clip(risk / 6.5, 0, 1)
        
        # 1 means dropped out, 0 means not
        y = (np.random.random(n) < prob).astype(int)
        
        return df, y

    def train_initial(self):
        X, y = self._generate_synthetic_data()
        self.model.fit(X, y)
        self.is_trained = True
        
    def predict_risk(self, student_data: dict):
        if not self.is_trained:
            self.train_initial()
            
        # Data prep
        X = pd.DataFrame([{
            'attendance_pct': student_data['attendance_pct'],
            'latest_exam_score': student_data['latest_exam_score'],
            'previous_exam_score': student_data['previous_exam_score'],
            'distance_km': student_data['distance_km'],
            'midday_meal': 1 if student_data['midday_meal'] else 0,
            'sibling_dropout': 1 if student_data['sibling_dropout'] else 0
        }])
        
        # Get probability of class 1 (dropout)
        prob = self.model.predict_proba(X)[0][1]
        score = int(prob * 100)
        
        # Get risk level
        if score <= 30:
            level = 'Low'
        elif score <= 60:
            level = 'Medium'
        else:
            level = 'High'
            
        # Extract local feature importances by multiplying global importance
        # with the "badness" of the student's feature (simple heuristic for MVP)
        # Or simply use global feature importances for this MVP snippet
        importances = self.model.feature_importances_
        feature_scores = {}
        
        # Heuristic explanation
        if student_data['attendance_pct'] < 70:
            feature_scores['Low Attendance'] = importances[0] * 2
        if student_data['latest_exam_score'] < 50:
            feature_scores['Low Exam Scores'] = importances[1] * 2
        if student_data['distance_km'] > 5:
            feature_scores['Long Commute'] = importances[3] * 1.5
        if student_data['sibling_dropout']:
            feature_scores['Sibling Dropout History'] = importances[5] * 3
            
        # Fallback if dictionary is empty
        if not feature_scores:
            feature_scores = {
                'Attendance Level': importances[0],
                'Academic Performance': importances[1],
                'Commute Distance': importances[3]
            }
            
        # Sort by importance and get top 3
        sorted_features = sorted(feature_scores.items(), key=lambda x: x[1], reverse=True)
        top_factors = [f[0] for f in sorted_features[:3]]
        
        return {
            'score': score,
            'level': level,
            'top_factors': ", ".join(top_factors)
        }

# Global instance
model_instance = DropoutModel()
