# Astoveda Quiz System

A Flask-based personality assessment application that provides users with personalized insights based on their responses to demographic and personality questions.

## Features

- **Multi-page Quiz Flow**: Structured assessment with demographics and personality questions
- **Personality Type Analysis**: Calculates personality archetypes (Explorer, Nurturer, Thinker, Leader)
- **Session Management**: Temporary entries allow users to navigate freely until results are viewed
- **Navigation Protection**: Prevents users from modifying responses after viewing results
- **Responsive Design**: Clean, modern UI with intuitive navigation
- **Admin Panel**: Built-in administration interface for managing quizzes and questions

## System Architecture

### Database Models

- **Quiz**: Container for assessment metadata
- **Question**: Individual questions with various types (demographics, multiple_choice, yes_no)
- **QuizSession**: Tracks user sessions and progress
- **Response**: Stores user answers to questions
- **Result**: Calculated personality assessment results

### Quiz Flow

1. **Landing Page** (`/`) - Quiz introduction and entry point
2. **Start Quiz** (`/start`) - Information page about the assessment
3. **Begin Assessment** (`/begin`) - Creates session and starts quiz
4. **Demographics** (`/demographics`) - Collects basic user information
5. **Question Pages** (`/questions/<page>`) - Multi-page personality questions
6. **Processing** (`/processing`) - Transition page before results
7. **Results** (`/results`) - Final personality assessment and recommendations

### Navigation Rules

- Users can navigate back and forth between intermediate pages
- Session data is preserved during navigation
- Once results are viewed, users cannot return to modify answers
- Completed users are redirected to landing page to start fresh

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd astoveda
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up the database**
```bash
python app.py
```
This will create the SQLite database and seed it with default questions.

4. **Run the application**
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key for session management
- `SQLALCHEMY_DATABASE_URI`: Database connection string (defaults to SQLite)

### Database Configuration
The application uses SQLite by default but can be configured for other databases by modifying the `SQLALCHEMY_DATABASE_URI` in `app.py`.

## Personality Assessment Algorithm

The system evaluates responses across four personality dimensions:

### Personality Types

1. **The Explorer**
   - Traits: Curious, Independent, Adaptable, Adventurous
   - Recommendations: Rock climbing, travel, new skills, adventure clubs

2. **The Nurturer**
   - Traits: Caring, Supportive, Empathetic, Harmonious
   - Recommendations: Volunteering, support groups, meditation, nature time

3. **The Thinker**
   - Traits: Analytical, Introspective, Knowledgeable, Contemplative
   - Recommendations: Philosophy, chess, book clubs, language learning

4. **The Leader**
   - Traits: Confident, Decisive, Inspiring, Goal-oriented
   - Recommendations: Leadership courses, projects, mentoring, professional organizations

### Scoring Logic

The algorithm analyzes responses to specific questions:
- Weekend preferences (Adventure, Cozy, Social, Learning)
- Introversion/Extroversion tendencies
- Stress handling methods
- Planning vs. spontaneity preferences
- Group interaction styles
- Daydreaming frequency

Each response contributes points to different personality types, with the highest-scoring type determining the final result.

## Admin Panel

Access the admin panel at `/admin` to:
- View quiz statistics
- Manage questions and quiz content
- Monitor user sessions and responses

## File Structure

```
astoveda/
├── app.py                 # Main Flask application
├── models.py             # Database models (if separate)
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates
│   ├── landing.html      # Landing page
│   ├── start_quiz.html   # Start quiz information page
│   ├── demographics.html # Demographics form
│   ├── questions.html    # Question pages
│   ├── processing.html   # Processing transition
│   ├── results.html      # Results display
│   └── admin/           # Admin panel templates
├── services/            # Business logic
│   └── result_calculator.py
└── admin/              # Admin functionality
    ├── routes.py
    └── forms.py
```

## Security Features

- Session-based user tracking
- CSRF protection through Flask-WTF
- Input validation on all forms
- SQL injection prevention through SQLAlchemy ORM
- Secure session management

## Development

### Adding New Questions

1. Create questions in the database through the admin panel
2. Set appropriate `page_number`, `question_type`, and `order_index`
3. For multiple choice questions, store options as JSON in the `options` field
4. Update the scoring algorithm in `ResultCalculator` if needed

### Customizing Personality Types

Modify the `personality_types` dictionary in the `ResultCalculator` class to:
- Add new personality types
- Update descriptions and traits
- Change recommendations
- Adjust scoring weights

### Database Migrations

For production deployments, consider implementing proper database migrations:
```bash
pip install Flask-Migrate
```

## Testing

Run the application in debug mode for development:
```python
app.run(debug=True)
```

## Deployment

For production deployment:

1. Set `debug=False` in `app.py`
2. Use a production WSGI server (e.g., Gunicorn)
3. Configure a production database (PostgreSQL, MySQL)
4. Set up proper environment variables
5. Implement HTTPS

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.