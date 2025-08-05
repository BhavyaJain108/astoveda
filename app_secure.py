from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database import db, init_db, Quiz, Question, Response, QuizSession, Result
from services.result_calculator import ResultCalculator
from utils.security import sanitize_input, generate_session_id, get_client_info
from admin.routes import admin_bp
from config import config
from datetime import datetime
import os

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    app.register_blueprint(admin_bp)
    
    return app

app = create_app()

def seed_data():
    with app.app_context():
        if Quiz.query.first():
            return
        
        quiz = Quiz(
            title="Personality Assessment",
            description="Discover your personality archetype through this comprehensive assessment.",
            is_active=True,
            version="v1"
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
                    options=["Urban", "Suburban", "Rural"]),
            
            Question(quiz_id=quiz.id, page_number=2, question_type='multiple_choice',
                    question_text='What is your ideal weekend?', required=True, order_index=1,
                    options=["Adventure outdoors", "Cozy at home", "Social gathering", "Learning something new"]),
            Question(quiz_id=quiz.id, page_number=2, question_type='yes_no',
                    question_text='Do you consider yourself introverted?', required=True, order_index=2),
            Question(quiz_id=quiz.id, page_number=2, question_type='multiple_choice',
                    question_text='How do you handle stress?', required=True, order_index=3,
                    options=["Talk it out with friends", "Exercise or physical activity", "Take time alone to think", "Dive into work or projects"]),
            
            Question(quiz_id=quiz.id, page_number=3, question_type='yes_no',
                    question_text='Do you prefer planning ahead over being spontaneous?', required=True, order_index=1),
            Question(quiz_id=quiz.id, page_number=3, question_type='multiple_choice',
                    question_text='In group settings, you tend to:', required=True, order_index=2,
                    options=["Take charge and lead", "Contribute ideas actively", "Listen and support others", "Observe and analyze"]),
            Question(quiz_id=quiz.id, page_number=3, question_type='yes_no',
                    question_text='Do you often daydream or think about possibilities?', required=True, order_index=3),
        ]
        
        for q in questions:
            db.session.add(q)
        
        db.session.commit()

@app.route('/')
def landing():
    quiz = Quiz.query.filter_by(is_active=True).first()
    if not quiz:
        return "No active quiz found. Please contact administrator.", 404
    return render_template('landing.html', quiz=quiz)

@app.route('/start')
def start_quiz():
    quiz = Quiz.query.filter_by(is_active=True).first()
    if not quiz:
        return redirect(url_for('landing'))
    
    session_id = generate_session_id()
    session['quiz_session_id'] = session_id
    
    client_info = get_client_info()
    
    quiz_session = QuizSession(
        session_id=session_id,
        user_ip=client_info['ip_hash'],
        user_agent_hash=client_info['user_agent_hash'],
        current_page=1,
        quiz_id=quiz.id,
        quiz_version=quiz.version
    )
    db.session.add(quiz_session)
    db.session.commit()
    
    return redirect(url_for('demographics'))

@app.route('/demographics')
def demographics():
    if 'quiz_session_id' not in session:
        return redirect(url_for('landing'))
    
    session_obj = QuizSession.query.filter_by(session_id=session['quiz_session_id']).first()
    if not session_obj:
        return redirect(url_for('landing'))
    
    questions = Question.query.filter_by(
        quiz_id=session_obj.quiz_id,
        page_number=1, 
        question_type='demographics',
        is_active=True
    ).order_by(Question.order_index).all()
    
    return render_template('demographics.html', questions=questions)

@app.route('/questions/<int:page>')
def questions_page(page):
    if 'quiz_session_id' not in session:
        return redirect(url_for('landing'))
    
    session_obj = QuizSession.query.filter_by(session_id=session['quiz_session_id']).first()
    if not session_obj:
        return redirect(url_for('landing'))
    
    questions = Question.query.filter_by(
        quiz_id=session_obj.quiz_id,
        page_number=page,
        is_active=True
    ).filter(Question.question_type != 'demographics').order_by(Question.order_index).all()
    
    if not questions:
        return redirect(url_for('processing'))
    
    max_page = db.session.query(db.func.max(Question.page_number)).filter_by(
        quiz_id=session_obj.quiz_id,
        is_active=True
    ).scalar()
    
    return render_template('questions.html', questions=questions, page=page, max_page=max_page)

@app.route('/submit', methods=['POST'])
def submit_answers():
    if 'quiz_session_id' not in session:
        return redirect(url_for('landing'))
    
    session_id = session['quiz_session_id']
    
    for key, value in request.form.items():
        if key.startswith('question_'):
            question_id = int(key.split('_')[1])
            
            # Sanitize input
            sanitized_value = sanitize_input(value)
            
            existing_response = Response.query.filter_by(
                session_id=session_id, 
                question_id=question_id
            ).first()
            
            if existing_response:
                existing_response.answer_value = sanitized_value
            else:
                response = Response(
                    session_id=session_id,
                    question_id=question_id,
                    answer_value=sanitized_value
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
    
    return render_template('processing.html')

@app.route('/calculate_results')
def calculate_results():
    if 'quiz_session_id' not in session:
        return redirect(url_for('landing'))
    
    session_id = session['quiz_session_id']
    
    existing_result = Result.query.filter_by(session_id=session_id).first()
    if existing_result:
        return redirect(url_for('results'))
    
    responses = Response.query.filter_by(session_id=session_id).all()
    calculator = ResultCalculator()
    result_data = calculator.calculate(responses)
    
    result = Result(
        session_id=session_id,
        result_type=result_data['result_type'],
        result_data=result_data
    )
    db.session.add(result)
    
    quiz_session = QuizSession.query.filter_by(session_id=session_id).first()
    quiz_session.completed_at = datetime.utcnow()
    
    db.session.commit()
    
    return redirect(url_for('results'))

@app.route('/results')
def results():
    if 'quiz_session_id' not in session:
        return redirect(url_for('landing'))
    
    session_id = session['quiz_session_id']
    result = Result.query.filter_by(session_id=session_id).first()
    
    if not result:
        return redirect(url_for('processing'))
    
    result_data = result.get_result_data()
    
    return render_template('results.html', result=result_data)

def create_tables():
    with app.app_context():
        db.create_all()
        seed_data()

if __name__ == '__main__':
    create_tables()
    app.run(debug=app.config['DEBUG'])