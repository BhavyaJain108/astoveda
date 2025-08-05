"""Route handlers for the quiz application."""

from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from datetime import date
from quiz import db
from quiz.models import Quiz, Question, CompletedQuiz
from quiz.services import SessionService, QuizService, ResultCalculator

# Create blueprint
quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/')
def landing():
    """Landing page - clears any existing session."""
    SessionService.clear_session(session)
    quiz = QuizService.get_active_quiz()
    return render_template('landing.html', quiz=quiz)

@quiz_bp.route('/begin')
def begin_quiz():
    """Start a new quiz session."""
    # Always start fresh - clear any existing session
    SessionService.clear_session(session)
    session_id = SessionService.init_session(session)
    return redirect(url_for('quiz.questions_page', page=1))

@quiz_bp.route('/questions/<int:page>')
def questions_page(page):
    """Display questions for a specific page."""
    session_data = SessionService.get_session_data(session)
    if not session_data:
        return redirect(url_for('quiz.landing'))
    
    # Prevent access to quiz pages after completion
    if session_data['completed']:
        return redirect(url_for('quiz.results'))
    
    questions = QuizService.get_questions_for_page(page)
    if not questions:
        return redirect(url_for('quiz.questions_page', page=1))
    
    # Update current page
    session['current_page'] = page
    session.modified = True
    
    max_page = QuizService.get_max_page()
    
    # Get existing responses for pre-population
    existing_responses = {}
    for question in questions:
        if str(question.id) in session_data['responses']:
            existing_responses[question.id] = session_data['responses'][str(question.id)]
    
    return render_template('questions.html', 
                         questions=questions, 
                         page=page, 
                         max_page=max_page, 
                         existing_responses=existing_responses,
                         today=date.today())

@quiz_bp.route('/submit', methods=['POST'])
def submit_answers():
    """Process submitted answers."""
    session_data = SessionService.get_session_data(session)
    if not session_data or session_data['completed']:
        return redirect(url_for('quiz.landing'))
    
    # Save responses to session
    for key, value in request.form.items():
        if key.startswith('question_'):
            question_id = int(key.split('_')[1])
            SessionService.save_response(session, question_id, value)
    
    next_page = request.form.get('next_page')
    
    if next_page == 'results':
        # Quiz completed - now save to database
        try:
            result_data = QuizService.complete_quiz(
                session_data=SessionService.get_session_data(session),
                user_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )
            
            # Mark as completed in session
            session['quiz_completed'] = True
            session['result_data'] = result_data
            session.modified = True
            
            return redirect(url_for('quiz.results'))
        except Exception as e:
            # Log error and redirect to landing
            print(f"Error completing quiz: {e}")
            return redirect(url_for('quiz.landing'))
    else:
        return redirect(url_for('quiz.questions_page', page=int(next_page)))

@quiz_bp.route('/save_answer', methods=['POST'])
def save_answer():
    """Save answer in real-time via AJAX."""
    try:
        session_data = SessionService.get_session_data(session)
        if not session_data:
            print("DEBUG: No active session for save_answer")
            return jsonify({'error': 'No active session'}), 400
        
        data = request.get_json()
        print(f"DEBUG: Received save_answer data: {data}")
        
        if not data or 'question_id' not in data or 'answer' not in data:
            print("DEBUG: Invalid data structure")
            return jsonify({'error': 'Invalid data'}), 400
        
        question_id = data['question_id']
        answer = data['answer']
        
        # Save the answer
        SessionService.save_response(session, question_id, answer)
        print(f"DEBUG: Saved answer for question {question_id}: {answer}")
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"DEBUG: Error in save_answer: {e}")
        return jsonify({'error': str(e)}), 500

@quiz_bp.route('/cleanup_session', methods=['POST'])
def cleanup_session():
    """Clean up session when user closes tab."""
    print("DEBUG: cleanup_session called")
    session_data = SessionService.get_session_data(session)
    if session_data and not session_data['completed']:
        print("DEBUG: Clearing incomplete session")
        SessionService.clear_session(session)
    else:
        print("DEBUG: Not clearing session - either no session or already completed")
    return '', 204

@quiz_bp.route('/results')
def results():
    """Display quiz results."""
    session_data = SessionService.get_session_data(session)
    if not session_data or not session_data['completed']:
        return redirect(url_for('quiz.landing'))
    
    result_data = session.get('result_data', {
        'result_type': 'Type A',
        'title': 'Type A Personality',
        'description': 'You are a Type A personality.'
    })
    
    return render_template('results.html', result_data=result_data)