"""Database models for the quiz application."""

import json
from datetime import datetime
from quiz import db

class Quiz(db.Model):
    """Quiz model - contains quiz metadata."""
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Quiz {self.title}>'

class Question(db.Model):
    """Question model - individual quiz questions."""
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    page_number = db.Column(db.Integer, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)  # demographics, multiple_choice, yes_no
    question_text = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text)  # JSON string for multiple choice options
    required = db.Column(db.Boolean, default=True)
    order_index = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, default=1.0)
    
    def get_options(self):
        """Parse options JSON string."""
        if self.options:
            try:
                return json.loads(self.options)
            except json.JSONDecodeError:
                return []
        return []
    
    def __repr__(self):
        return f'<Question {self.question_text[:50]}...>'

class CompletedQuiz(db.Model):
    """Completed quiz model - stores finished quiz results."""
    __tablename__ = 'completed_quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), nullable=False, unique=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    
    # User data
    user_ip = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    
    # Timing
    started_at = db.Column(db.DateTime, nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Results
    result_type = db.Column(db.String(100), nullable=False)
    result_data = db.Column(db.Text)  # JSON string with detailed results
    responses = db.Column(db.Text, nullable=False)  # JSON string of all responses
    
    # Relationships
    quiz = db.relationship('Quiz', backref='completed_quizzes')
    
    def get_responses(self):
        """Parse responses JSON string."""
        if self.responses:
            try:
                return json.loads(self.responses)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def get_result_data(self):
        """Parse result data JSON string."""
        if self.result_data:
            try:
                return json.loads(self.result_data)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def __repr__(self):
        return f'<CompletedQuiz {self.session_id}>'