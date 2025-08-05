"""Business logic services for the quiz application."""

import json
from datetime import datetime
from quiz import db
from quiz.models import Quiz, Question, CompletedQuiz

class SessionService:
    """Handles quiz session management."""
    
    @staticmethod
    def init_session(session):
        """Initialize a new quiz session."""
        import uuid
        
        session_id = str(uuid.uuid4())
        session['quiz_session_id'] = session_id
        session['quiz_started_at'] = datetime.utcnow().isoformat()
        session['quiz_completed'] = False
        session['current_page'] = 1
        session['responses'] = {}
        return session_id
    
    @staticmethod
    def get_session_data(session):
        """Get current session data."""
        if 'quiz_session_id' not in session:
            return None
        
        return {
            'session_id': session['quiz_session_id'],
            'started_at': session.get('quiz_started_at'),
            'completed': session.get('quiz_completed', False),
            'current_page': session.get('current_page', 1),
            'responses': session.get('responses', {})
        }
    
    @staticmethod
    def save_response(session, question_id, answer):
        """Save a response to the session."""
        if 'responses' not in session:
            session['responses'] = {}
        session['responses'][str(question_id)] = answer
        session.modified = True
    
    @staticmethod
    def clear_session(session):
        """Clear all quiz-related session data."""
        keys_to_remove = [
            'quiz_session_id', 'quiz_started_at', 'quiz_completed', 
            'current_page', 'responses', 'result_data'
        ]
        for key in keys_to_remove:
            session.pop(key, None)

class QuizService:
    """Handles quiz-related business logic."""
    
    @staticmethod
    def get_active_quiz():
        """Get the active quiz."""
        return Quiz.query.filter_by(is_active=True).first()
    
    @staticmethod
    def get_questions_for_page(page_number):
        """Get questions for a specific page."""
        return Question.query.filter_by(page_number=page_number).order_by(Question.order_index).all()
    
    @staticmethod
    def get_max_page():
        """Get the maximum page number."""
        return db.session.query(db.func.max(Question.page_number)).scalar() or 1
    
    @staticmethod
    def complete_quiz(session_data, user_ip, user_agent):
        """Complete a quiz and save results to database."""
        # Calculate results
        result_data = ResultCalculator.calculate(session_data['responses'])
        
        # Save to database
        completed_quiz = CompletedQuiz(
            session_id=session_data['session_id'],
            quiz_id=1,  # Assuming single quiz for now
            user_ip=user_ip,
            user_agent=user_agent,
            started_at=datetime.fromisoformat(session_data['started_at']),
            result_type=result_data['result_type'],
            result_data=json.dumps(result_data),
            responses=json.dumps(session_data['responses'])
        )
        
        db.session.add(completed_quiz)
        db.session.commit()
        
        return result_data
    
    @staticmethod
    def seed_database():
        """Seed the database with initial data."""
        if Quiz.query.first():
            return  # Already seeded
        
        # Create quiz
        quiz = Quiz(
            title="Personality Assessment",
            description="Discover your personality archetype through this comprehensive assessment."
        )
        db.session.add(quiz)
        db.session.flush()
        
        # Create questions
        questions = [
            # Demographics (Page 1)
            Question(
                quiz_id=quiz.id, page_number=1, question_type='demographics',
                question_text='What is your name?', required=True, order_index=1
            ),
            Question(
                quiz_id=quiz.id, page_number=1, question_type='demographics',
                question_text='Date of birth', required=True, order_index=2
            ),
            Question(
                quiz_id=quiz.id, page_number=1, question_type='demographics',
                question_text='Location', required=True, order_index=3,
                options='["Urban", "Suburban", "Rural"]'
            ),
            
            # Personality Questions (Page 2)
            Question(
                quiz_id=quiz.id, page_number=2, question_type='multiple_choice',
                question_text='What is your ideal weekend?', required=True, order_index=1,
                options='["Adventure outdoors", "Cozy at home", "Social gathering", "Learning something new"]'
            ),
            Question(
                quiz_id=quiz.id, page_number=2, question_type='yes_no',
                question_text='Do you consider yourself introverted?', required=True, order_index=2
            ),
            Question(
                quiz_id=quiz.id, page_number=2, question_type='multiple_choice',
                question_text='How do you handle stress?', required=True, order_index=3,
                options='["Talk it out with friends", "Exercise or physical activity", "Take time alone to think", "Dive into work or projects"]'
            ),
            
            # More Questions (Page 3)
            Question(
                quiz_id=quiz.id, page_number=3, question_type='yes_no',
                question_text='Do you prefer planning ahead over being spontaneous?', required=True, order_index=1
            ),
            Question(
                quiz_id=quiz.id, page_number=3, question_type='multiple_choice',
                question_text='In group settings, you tend to:', required=True, order_index=2,
                options='["Take charge and lead", "Contribute ideas actively", "Listen and support others", "Observe and analyze"]'
            ),
            Question(
                quiz_id=quiz.id, page_number=3, question_type='yes_no',
                question_text='Do you often daydream or think about possibilities?', required=True, order_index=3
            ),
        ]
        
        for question in questions:
            db.session.add(question)
        
        db.session.commit()

class ResultCalculator:
    """Calculates quiz results."""
    
    @staticmethod
    def calculate(responses):
        """Calculate quiz results based on responses."""
        # For now, always return Type A
        # This can be expanded with more complex logic later
        return {
            'result_type': 'Type A',
            'title': 'Type A Personality',
            'description': 'You are a Type A personality.',
            'traits': ['Driven', 'Competitive', 'Time-conscious', 'Achievement-oriented'],
            'recommendations': [
                'Practice stress management techniques',
                'Take regular breaks',
                'Focus on work-life balance',
                'Consider meditation or relaxation exercises'
            ]
        }