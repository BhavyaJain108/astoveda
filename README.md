# Astroveda Quiz System

A simple Flask-based personality quiz application.

## Features

- **Multi-page Quiz Flow**: Demographics → Questions → Results
- **Session Management**: Resume incomplete quizzes
- **Answer Preservation**: Navigate back/forth without losing data
- **Clean Results**: Always returns "Type A" for all users
- **Auto Cleanup**: Removes abandoned sessions when tab closes

## File Structure

```
astroveda/
├── app.py              # Main application (models, routes, logic)
├── requirements.txt    # Python dependencies
├── instance/
│   └── quiz.db        # SQLite database (auto-created)
├── templates/
│   ├── landing.html   # Home page
│   ├── questions.html # Quiz pages (demographics + questions)
│   └── results.html   # Results page
└── admin/             # Admin interface (optional)
    ├── forms.py
    ├── routes.py
    └── templates/
```

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **Open browser:**
   ```
   http://localhost:5000
   ```

## Quiz Flow

1. **Landing** (`/`) - Start page
2. **Demographics** (`/questions/1`) - Name, birth date, location  
3. **Questions** (`/questions/2`, `/questions/3`) - Personality questions
4. **Results** (`/results`) - Shows "Type A" result

## Database Schema

- **Quiz**: Quiz metadata
- **Question**: Individual questions with types (demographics, multiple_choice, yes_no)
- **QuizSession**: User sessions with completion tracking
- **Response**: User answers to questions
- **Result**: Final quiz results

## Navigation Features

- **Free navigation**: Go back/forth between pages
- **Answer persistence**: Form fields pre-populated with previous answers
- **Session resumption**: Resume incomplete quiz if browser closed
- **Completion protection**: Cannot modify answers after completion

## Development

The application uses:
- **Flask** - Web framework
- **SQLAlchemy** - Database ORM  
- **SQLite** - Database (no setup required)
- **Session-based** - No user accounts needed

All code is contained in a single `app.py` file for simplicity.