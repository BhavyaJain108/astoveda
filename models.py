from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    page_number = db.Column(db.Integer, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)  # demographics, multiple_choice, yes_no
    question_text = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text)  # JSON string for multiple choice options
    required = db.Column(db.Boolean, default=True)
    order_index = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, default=1.0)  # For scoring calculations
    
    responses = db.relationship('Response', backref='question', lazy=True, cascade='all, delete-orphan')
    
    def get_options(self):
        if self.options:
            return json.loads(self.options)
        return []

class QuizSession(db.Model):
    __tablename__ = 'quiz_sessions'
    
    session_id = db.Column(db.String(36), primary_key=True)  # UUID
    user_ip = db.Column(db.String(45))  # IPv6 support
    user_agent = db.Column(db.Text)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    current_page = db.Column(db.Integer, default=1)
    quiz_version = db.Column(db.String(50), default='v1')
    
    responses = db.relationship('Response', backref='session', lazy=True, cascade='all, delete-orphan')
    results = db.relationship('Result', backref='session', lazy=True, cascade='all, delete-orphan')

class Response(db.Model):
    __tablename__ = 'responses'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('quiz_sessions.session_id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    answer_value = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Result(db.Model):
    __tablename__ = 'results'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('quiz_sessions.session_id'), nullable=False)
    result_type = db.Column(db.String(100), nullable=False)
    result_data = db.Column(db.Text, nullable=False)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_result_data(self):
        return json.loads(self.result_data)