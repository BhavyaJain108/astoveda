from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import json
from cryptography.fernet import Fernet
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine
import os

db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    db.init_app(app)
    migrate.init_app(app, db)
    return db

# Encryption utilities
def get_encryption_key():
    key = os.environ.get('ENCRYPTION_KEY', 'dev-encryption-key-32-bytes-long!')
    return key.encode()[:32].ljust(32, b'0')  # Ensure 32 bytes

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    version = db.Column(db.String(50), default='v1')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'is_active': self.is_active,
            'version': self.version,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    page_number = db.Column(db.Integer, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)  # demographics, multiple_choice, yes_no, rating
    question_text = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON)  # Use JSON column for PostgreSQL, TEXT for SQLite
    required = db.Column(db.Boolean, default=True)
    order_index = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, default=1.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    responses = db.relationship('Response', backref='question', lazy=True, cascade='all, delete-orphan')
    
    def get_options(self):
        if self.options:
            if isinstance(self.options, str):
                return json.loads(self.options)
            return self.options
        return []
    
    def set_options(self, options_list):
        self.options = options_list
    
    def to_dict(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'page_number': self.page_number,
            'question_type': self.question_type,
            'question_text': self.question_text,
            'options': self.get_options(),
            'required': self.required,
            'order_index': self.order_index,
            'weight': self.weight,
            'is_active': self.is_active
        }

class QuizSession(db.Model):
    __tablename__ = 'quiz_sessions'
    
    session_id = db.Column(db.String(36), primary_key=True)
    user_ip = db.Column(db.String(45))  # Hashed for privacy
    user_agent_hash = db.Column(db.String(64))  # Hashed user agent
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    current_page = db.Column(db.Integer, default=1)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'))
    quiz_version = db.Column(db.String(50), default='v1')
    
    responses = db.relationship('Response', backref='session', lazy=True, cascade='all, delete-orphan')
    results = db.relationship('Result', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'current_page': self.current_page,
            'quiz_version': self.quiz_version
        }

class Response(db.Model):
    __tablename__ = 'responses'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('quiz_sessions.session_id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    answer_value = db.Column(db.Text, nullable=False)  # Consider encryption for sensitive data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'question_id': self.question_id,
            'answer_value': self.answer_value,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Result(db.Model):
    __tablename__ = 'results'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('quiz_sessions.session_id'), nullable=False)
    result_type = db.Column(db.String(100), nullable=False)
    result_data = db.Column(db.JSON)  # Store as JSON for easier querying
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_result_data(self):
        if isinstance(self.result_data, str):
            return json.loads(self.result_data)
        return self.result_data
    
    def set_result_data(self, data):
        self.result_data = data
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'result_type': self.result_type,
            'result_data': self.get_result_data(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }