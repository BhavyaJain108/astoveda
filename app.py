from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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
    question_type = db.Column(db.String(50), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text)
    required = db.Column(db.Boolean, default=True)
    order_index = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, default=1.0)
    
    responses = db.relationship('Response', backref='question', lazy=True, cascade='all, delete-orphan')
    
    def get_options(self):
        if self.options:
            return json.loads(self.options)
        return []

class QuizSession(db.Model):
    __tablename__ = 'quiz_sessions'
    
    session_id = db.Column(db.String(36), primary_key=True)
    user_ip = db.Column(db.String(45))
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
    result_data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_result_data(self):
        return json.loads(self.result_data)

class ResultCalculator:
    def __init__(self):
        self.personality_types = {
            'explorer': {
                'title': 'The Explorer',
                'description': 'You thrive on adventure and new experiences. You are curious, independent, and adaptable.',
                'traits': ['Curious', 'Independent', 'Adaptable', 'Adventurous'],
                'recommendations': ['Try rock climbing', 'Visit a new country', 'Learn a new skill', 'Join an adventure club']
            },
            'nurturer': {
                'title': 'The Nurturer',
                'description': 'You are caring, supportive, and find joy in helping others. You value harmony and relationships.',
                'traits': ['Caring', 'Supportive', 'Empathetic', 'Harmonious'],
                'recommendations': ['Volunteer for a cause', 'Join a support group', 'Practice meditation', 'Spend time in nature']
            },
            'thinker': {
                'title': 'The Thinker',
                'description': 'You are analytical, introspective, and value knowledge and understanding. You prefer depth over breadth.',
                'traits': ['Analytical', 'Introspective', 'Knowledgeable', 'Contemplative'],
                'recommendations': ['Read philosophy books', 'Take up chess', 'Join a book club', 'Learn a new language']
            },
            'leader': {
                'title': 'The Leader',
                'description': 'You are confident, decisive, and naturally take charge. You inspire others and drive results.',
                'traits': ['Confident', 'Decisive', 'Inspiring', 'Goal-oriented'],
                'recommendations': ['Take a leadership course', 'Start a project', 'Mentor someone', 'Join a professional organization']
            }
        }
    
    def calculate(self, responses):
        scores = {
            'explorer': 0,
            'nurturer': 0,
            'thinker': 0,
            'leader': 0
        }
        
        response_dict = {}
        for response in responses:
            response_dict[response.question_id] = response.answer_value
        
        # Question 4: Ideal weekend scoring
        weekend_answer = response_dict.get(4, '')
        if weekend_answer == 'Adventure outdoors':
            scores['explorer'] += 3
        elif weekend_answer == 'Cozy at home':
            scores['thinker'] += 2
        elif weekend_answer == 'Social gathering':
            scores['nurturer'] += 2
        elif weekend_answer == 'Learning something new':
            scores['thinker'] += 1
            scores['explorer'] += 1
        
        # Question 5: Introversion scoring
        introverted = response_dict.get(5, '')
        if introverted == 'yes':
            scores['thinker'] += 2
            scores['nurturer'] += 1
        else:
            scores['leader'] += 2
            scores['explorer'] += 1
        
        # Question 6: Stress handling scoring
        stress_answer = response_dict.get(6, '')
        if stress_answer == 'Talk it out with friends':
            scores['nurturer'] += 2
        elif stress_answer == 'Exercise or physical activity':
            scores['explorer'] += 2
        elif stress_answer == 'Take time alone to think':
            scores['thinker'] += 2
        elif stress_answer == 'Dive into work or projects':
            scores['leader'] += 2
        
        # Question 7: Planning vs spontaneous scoring
        planning = response_dict.get(7, '')
        if planning == 'yes':
            scores['leader'] += 1
            scores['thinker'] += 1
        else:
            scores['explorer'] += 2
        
        # Question 8: Group settings scoring
        group_answer = response_dict.get(8, '')
        if group_answer == 'Take charge and lead':
            scores['leader'] += 3
        elif group_answer == 'Contribute ideas actively':
            scores['explorer'] += 1
            scores['leader'] += 1
        elif group_answer == 'Listen and support others':
            scores['nurturer'] += 3
        elif group_answer == 'Observe and analyze':
            scores['thinker'] += 3
        
        # Question 9: Daydreaming scoring
        daydream = response_dict.get(9, '')
        if daydream == 'yes':
            scores['explorer'] += 1
            scores['thinker'] += 1
        else:
            scores['leader'] += 1
        
        # Find the highest scoring personality type
        top_personality = max(scores, key=scores.get)
        personality_data = self.personality_types[top_personality].copy()
        personality_data['result_type'] = top_personality
        personality_data['scores'] = scores
        
        return personality_data

def seed_data():
    if Quiz.query.first():
        return
    
    quiz = Quiz(
        title="Personality Assessment",
        description="Discover your personality archetype through this comprehensive assessment."
    )
    db.session.add(quiz)
    db.session.flush()
    
    questions = [
        Question(quiz_id=quiz.id, page_number=1, question_type='demographics', 
                question_text='What is your name?', required=True, order_index=1),
        Question(quiz_id=quiz.id, page_number=1, question_type='demographics', 
                question_text='Date of birth', required=True, order_index=2),
        Question(quiz_id=quiz.id, page_number=1, question_type='demographics', 
                question_text='Location', required=False, order_index=3,
                options='["Urban", "Suburban", "Rural"]'),
        
        Question(quiz_id=quiz.id, page_number=2, question_type='multiple_choice',
                question_text='What is your ideal weekend?', required=True, order_index=1,
                options='["Adventure outdoors", "Cozy at home", "Social gathering", "Learning something new"]'),
        Question(quiz_id=quiz.id, page_number=2, question_type='yes_no',
                question_text='Do you consider yourself introverted?', required=True, order_index=2),
        Question(quiz_id=quiz.id, page_number=2, question_type='multiple_choice',
                question_text='How do you handle stress?', required=True, order_index=3,
                options='["Talk it out with friends", "Exercise or physical activity", "Take time alone to think", "Dive into work or projects"]'),
        
        Question(quiz_id=quiz.id, page_number=3, question_type='yes_no',
                question_text='Do you prefer planning ahead over being spontaneous?', required=True, order_index=1),
        Question(quiz_id=quiz.id, page_number=3, question_type='multiple_choice',
                question_text='In group settings, you tend to:', required=True, order_index=2,
                options='["Take charge and lead", "Contribute ideas actively", "Listen and support others", "Observe and analyze"]'),
        Question(quiz_id=quiz.id, page_number=3, question_type='yes_no',
                question_text='Do you often daydream or think about possibilities?', required=True, order_index=3),
    ]
    
    for q in questions:
        db.session.add(q)
    
    db.session.commit()

@app.route('/')
def landing():
    # Clear any existing session data when returning to landing page
    session.pop('quiz_session_id', None)
    session.pop('quiz_completed', None)
    
    quiz = Quiz.query.first()
    return render_template('landing.html', quiz=quiz)

@app.route('/start')
def start_quiz():
    quiz = Quiz.query.first()
    return render_template('start_quiz.html', quiz=quiz)

@app.route('/begin')
def begin_quiz():
    session_id = str(uuid.uuid4())
    session['quiz_session_id'] = session_id
    session['quiz_completed'] = False
    
    quiz_session = QuizSession(
        session_id=session_id,
        user_ip=request.remote_addr,
        user_agent=request.headers.get('User-Agent', ''),
        current_page=1
    )
    db.session.add(quiz_session)
    db.session.commit()
    
    return redirect(url_for('demographics'))

@app.route('/demographics')
def demographics():
    if 'quiz_session_id' not in session:
        return redirect(url_for('landing'))
    
    # Redirect to home if quiz is already completed
    if session.get('quiz_completed', False):
        return redirect(url_for('landing'))
    
    questions = Question.query.filter_by(page_number=1, question_type='demographics').order_by(Question.order_index).all()
    return render_template('demographics.html', questions=questions)

@app.route('/questions/<int:page>')
def questions_page(page):
    if 'quiz_session_id' not in session:
        return redirect(url_for('landing'))
    
    # Redirect to home if quiz is already completed
    if session.get('quiz_completed', False):
        return redirect(url_for('landing'))
    
    questions = Question.query.filter_by(page_number=page).filter(Question.question_type != 'demographics').order_by(Question.order_index).all()
    if not questions:
        return redirect(url_for('processing'))
    
    max_page = db.session.query(db.func.max(Question.page_number)).scalar()
    return render_template('questions.html', questions=questions, page=page, max_page=max_page)

@app.route('/submit', methods=['POST'])
def submit_answers():
    if 'quiz_session_id' not in session:
        return redirect(url_for('landing'))
    
    # Redirect to home if quiz is already completed
    if session.get('quiz_completed', False):
        return redirect(url_for('landing'))
    
    session_id = session['quiz_session_id']
    
    for key, value in request.form.items():
        if key.startswith('question_'):
            question_id = int(key.split('_')[1])
            
            existing_response = Response.query.filter_by(
                session_id=session_id, 
                question_id=question_id
            ).first()
            
            if existing_response:
                existing_response.answer_value = value
            else:
                response = Response(
                    session_id=session_id,
                    question_id=question_id,
                    answer_value=value
                )
                db.session.add(response)
    
    db.session.commit()
    
    next_page = request.form.get('next_page')
    if next_page == 'processing':
        return redirect(url_for('processing'))
    else:
        return redirect(url_for('questions_page', page=int(next_page)))

@app.route('/processing')
def processing():
    if 'quiz_session_id' not in session:
        return redirect(url_for('landing'))
    
    # Redirect to home if quiz is already completed
    if session.get('quiz_completed', False):
        return redirect(url_for('landing'))
    
    return render_template('processing.html')

@app.route('/calculate_results')
def calculate_results():
    if 'quiz_session_id' not in session:
        return redirect(url_for('landing'))
    
    session_id = session['quiz_session_id']
    
    existing_result = Result.query.filter_by(session_id=session_id).first()
    if existing_result:
        session['quiz_completed'] = True
        return redirect(url_for('results'))
    
    responses = Response.query.filter_by(session_id=session_id).all()
    calculator = ResultCalculator()
    result_data = calculator.calculate(responses)
    
    result = Result(
        session_id=session_id,
        result_type=result_data['result_type'],
        result_data=str(result_data)
    )
    db.session.add(result)
    
    quiz_session = QuizSession.query.filter_by(session_id=session_id).first()
    quiz_session.completed_at = datetime.utcnow()
    
    db.session.commit()
    
    # Mark quiz as completed in session
    session['quiz_completed'] = True
    
    return redirect(url_for('results'))

@app.route('/results')
def results():
    if 'quiz_session_id' not in session:
        return redirect(url_for('landing'))
    
    session_id = session['quiz_session_id']
    result = Result.query.filter_by(session_id=session_id).first()
    
    if not result:
        return redirect(url_for('processing'))
    
    import json
    result_data = eval(result.result_data)
    
    return render_template('results.html', result=result_data)

def create_tables():
    with app.app_context():
        db.create_all()
        seed_data()

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)