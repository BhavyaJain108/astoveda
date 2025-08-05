"""Quiz application factory."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions
db = SQLAlchemy()

def create_app(config_name='default'):
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from quiz.routes import quiz_bp
    app.register_blueprint(quiz_bp)
    
    # Register admin blueprint if needed
    try:
        from admin.routes import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')
    except ImportError:
        pass  # Admin module is optional
    
    # Create database tables
    with app.app_context():
        db.create_all()
        from quiz.services import QuizService
        QuizService.seed_database()
    
    return app