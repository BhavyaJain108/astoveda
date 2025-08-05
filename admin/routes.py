from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from database import db, Quiz, Question, QuizSession, Response, Result
from admin.forms import LoginForm, QuizForm, QuestionForm
from utils.security import sanitize_input
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = sanitize_input(form.username.data)
        password = form.password.data
        
        if (username == current_app.config['ADMIN_USERNAME'] and 
            password == current_app.config['ADMIN_PASSWORD']):
            session['admin_logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html', form=form)

@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # Get stats
    total_sessions = QuizSession.query.count()
    completed_sessions = QuizSession.query.filter(QuizSession.completed_at.isnot(None)).count()
    total_questions = Question.query.filter_by(is_active=True).count()
    total_quizzes = Quiz.query.filter_by(is_active=True).count()
    
    completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
    
    # Recent sessions
    recent_sessions = QuizSession.query.order_by(QuizSession.started_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', 
                         total_sessions=total_sessions,
                         completed_sessions=completed_sessions,
                         total_questions=total_questions,
                         total_quizzes=total_quizzes,
                         completion_rate=completion_rate,
                         recent_sessions=recent_sessions)

@admin_bp.route('/quizzes')
@admin_required
def quizzes():
    quizzes = Quiz.query.all()
    return render_template('admin/quizzes.html', quizzes=quizzes)

@admin_bp.route('/quiz/new', methods=['GET', 'POST'])
@admin_required
def new_quiz():
    form = QuizForm()
    if form.validate_on_submit():
        quiz = Quiz(
            title=sanitize_input(form.title.data),
            description=sanitize_input(form.description.data, 1000),
            is_active=form.is_active.data,
            version=sanitize_input(form.version.data)
        )
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz created successfully!', 'success')
        return redirect(url_for('admin.quizzes'))
    
    return render_template('admin/quiz_form.html', form=form, title='New Quiz')

@admin_bp.route('/quiz/<int:quiz_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuizForm(obj=quiz)
    
    if form.validate_on_submit():
        quiz.title = sanitize_input(form.title.data)
        quiz.description = sanitize_input(form.description.data, 1000)
        quiz.is_active = form.is_active.data
        quiz.version = sanitize_input(form.version.data)
        
        db.session.commit()
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('admin.quizzes'))
    
    return render_template('admin/quiz_form.html', form=form, title='Edit Quiz', quiz=quiz)

@admin_bp.route('/quiz/<int:quiz_id>/questions')
@admin_required
def quiz_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).order_by(Question.page_number, Question.order_index).all()
    return render_template('admin/questions.html', quiz=quiz, questions=questions)

@admin_bp.route('/quiz/<int:quiz_id>/question/new', methods=['GET', 'POST'])
@admin_required
def new_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuestionForm()
    form.quiz_id.data = quiz_id
    
    if form.validate_on_submit():
        question = Question(
            quiz_id=quiz_id,
            page_number=form.page_number.data,
            question_type=form.question_type.data,
            question_text=sanitize_input(form.question_text.data, 1000),
            required=form.required.data,
            order_index=form.order_index.data,
            weight=form.weight.data,
            is_active=form.is_active.data
        )
        
        if form.question_type.data == 'multiple_choice':
            options = [sanitize_input(opt) for opt in form.get_options_list()]
            question.set_options(options)
        
        db.session.add(question)
        db.session.commit()
        flash('Question created successfully!', 'success')
        return redirect(url_for('admin.quiz_questions', quiz_id=quiz_id))
    
    return render_template('admin/question_form.html', form=form, title='New Question', quiz=quiz)

@admin_bp.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    form = QuestionForm(obj=question)
    
    # Set options in form
    if question.question_type == 'multiple_choice':
        form.set_options_from_list(question.get_options())
    
    if form.validate_on_submit():
        question.page_number = form.page_number.data
        question.question_type = form.question_type.data
        question.question_text = sanitize_input(form.question_text.data, 1000)
        question.required = form.required.data
        question.order_index = form.order_index.data
        question.weight = form.weight.data
        question.is_active = form.is_active.data
        
        if form.question_type.data == 'multiple_choice':
            options = [sanitize_input(opt) for opt in form.get_options_list()]
            question.set_options(options)
        else:
            question.options = None
        
        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('admin.quiz_questions', quiz_id=question.quiz_id))
    
    return render_template('admin/question_form.html', form=form, title='Edit Question', question=question)

@admin_bp.route('/question/<int:question_id>/delete', methods=['POST'])
@admin_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('admin.quiz_questions', quiz_id=quiz_id))

@admin_bp.route('/analytics')
@admin_required
def analytics():
    # Session analytics
    total_sessions = QuizSession.query.count()
    completed_sessions = QuizSession.query.filter(QuizSession.completed_at.isnot(None)).count()
    
    # Response analytics
    total_responses = Response.query.count()
    
    # Result type distribution
    result_distribution = db.session.query(
        Result.result_type,
        db.func.count(Result.id).label('count')
    ).group_by(Result.result_type).all()
    
    return render_template('admin/analytics.html',
                         total_sessions=total_sessions,
                         completed_sessions=completed_sessions,
                         total_responses=total_responses,
                         result_distribution=result_distribution)

@admin_bp.route('/export/responses')
@admin_required
def export_responses():
    # This would generate CSV export of responses
    # For now, return JSON
    responses = Response.query.join(Question).join(QuizSession).all()
    
    data = []
    for response in responses:
        data.append({
            'session_id': response.session_id,
            'question_text': response.question.question_text,
            'question_type': response.question.question_type,
            'answer': response.answer_value,
            'created_at': response.created_at.isoformat() if response.created_at else None
        })
    
    return jsonify(data)