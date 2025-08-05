# Quiz System Architecture Plan

## Overview
Building a modular quiz system for personality/astrology-type quizzes **integrated into existing client website**:
- Multiple question types (multiple choice, yes/no, text input)
- Multi-page flow (demographics → questions → results)
- Extensible result calculation system
- Simple database storage
- **Seamless integration with existing website design/navigation**

## Core Components

### 1. Question Types
- **Demographics**: Name, DOB, race/origins, location
- **Multiple Choice**: Single selection from options
- **Yes/No**: Boolean responses
- **Rating Scale**: 1-5 or 1-10 scales (future)
- **Text Input**: Short text responses (future)

### 2. Database Schema (Initial)
```
quizzes:
  - id
  - title
  - description
  - created_at

questions:
  - id
  - quiz_id
  - page_number
  - question_type (demographics|multiple_choice|yes_no)
  - question_text
  - options (JSON for multiple choice)
  - required (boolean)
  - order_index

responses:
  - id
  - session_id (UUID)
  - question_id
  - answer_value
  - created_at

results:
  - id
  - session_id
  - result_type
  - result_data (JSON)
  - created_at
```

### 3. Page Flow
1. **Landing/Intro** - Quiz description, start button
2. **Demographics** - Basic user info collection
3. **Question Pages** - Grouped questions (5-10 per page)
4. **Processing** - Result calculation (placeholder)
5. **Results** - Display calculated personality/astrology result

### 4. Technology Stack Options
- **Backend**: Node.js/Express or Python/Flask
- **Database**: SQLite (simple start) → PostgreSQL (production)
- **Frontend**: React/Vue (later phase)
- **State Management**: Simple session storage initially

### 5. Modular Architecture
```
/backend
  /models (Question, Response, Result)
  /controllers (quiz flow logic)
  /services (result calculation)
  /routes (API endpoints)
  /db (schema, migrations)

/frontend (future phase)
  /components (QuestionCard, ResultDisplay)
  /pages (Demographics, Questions, Results)
  /hooks (quiz state management)
```

## Development Phases

### Phase 1: Core Infrastructure
- Database setup and models
- Basic CRUD operations for questions
- Session management for responses
- Simple API endpoints

### Phase 2: Question System
- Implement different question types
- Page-based question grouping
- Response validation and storage

### Phase 3: Result System
- Pluggable result calculation framework
- Result display templates
- Basic scoring algorithms

### Phase 4: Frontend Integration
- React/Vue frontend
- State management
- Responsive design

## Sample Data Structure

### Sample Questions
```json
{
  "demographics": [
    {"type": "text", "question": "What's your name?", "required": true},
    {"type": "date", "question": "Date of birth", "required": true},
    {"type": "select", "question": "Location", "options": ["Urban", "Suburban", "Rural"]}
  ],
  "personality": [
    {"type": "multiple_choice", "question": "Your ideal weekend?", 
     "options": ["Adventure outdoors", "Cozy at home", "Social gathering", "Learning something new"]},
    {"type": "yes_no", "question": "Do you consider yourself introverted?"}
  ]
}
```

### Sample Result Template
```json
{
  "result_type": "personality_archetype",
  "title": "The Explorer",
  "description": "You thrive on adventure and new experiences...",
  "traits": ["Curious", "Independent", "Adaptable"],
  "recommendations": ["Try rock climbing", "Visit a new country"]
}
```

## Website Integration Considerations

### URL Structure & Routing
```
/quiz/                          # Quiz landing/intro page
/quiz/start                     # Begin quiz (creates session)
/quiz/demographics              # Personal info collection
/quiz/questions/1               # Question page 1
/quiz/questions/2               # Question page 2
/quiz/questions/N               # Question page N
/quiz/processing               # Loading/calculation screen
/quiz/results                  # Final results display
/quiz/results/share            # Shareable results page (optional)
```

### State Management Strategy
- **Session-based**: Store quiz progress in database with session ID
- **URL-safe navigation**: Allow direct linking to quiz pages (with session validation)
- **Browser back/forward**: Handle gracefully without losing progress
- **Abandonment recovery**: Save partial responses, allow resume later
- **Multi-tab handling**: Prevent conflicts if user opens multiple tabs

### Integration Points with Existing Website

#### Navigation & Header
- Maintain existing site header/navigation
- Add breadcrumb: Home > Quiz > Current Step
- Consider quiz-specific header styling (darker/focused mode?)

#### Styling & Theming
- Use existing CSS framework/design system
- Match typography, colors, button styles
- Responsive design matching site's breakpoints
- Loading states consistent with site patterns

#### Analytics & Tracking
- Integrate with existing GA/analytics setup
- Track quiz completion rates, drop-off points
- A/B testing capability for questions/results
- Social sharing tracking (if results are shareable)

#### Performance Considerations
- Lazy load question pages
- Preload next question while user answers current
- Optimize images/assets for results page
- Consider caching strategy for repeat visitors

### Data Architecture Refinements

#### Session Management
```sql
quiz_sessions:
  - session_id (UUID, primary key)
  - user_ip (for basic analytics)
  - user_agent (browser detection)
  - started_at
  - completed_at
  - current_page
  - quiz_version (for A/B testing)
```

#### Question Versioning
```sql
quiz_versions:
  - version_id
  - quiz_id
  - version_name
  - is_active
  - created_at

questions:
  - id
  - quiz_version_id (instead of quiz_id)
  - page_number
  - question_type
  - question_text
  - options (JSON)
  - required
  - order_index
  - weight (for scoring)
```

### Admin Interface Considerations
- Simple CMS for client to manage questions
- A/B testing controls
- Analytics dashboard
- Export responses to CSV
- Result template editor

### Technical Implementation Details

#### Backend API Structure
```
GET /api/quiz/config              # Quiz metadata & structure
POST /api/quiz/start              # Create new session
GET /api/quiz/questions/:page     # Get questions for page
POST /api/quiz/answers            # Submit answers
GET /api/quiz/results/:session    # Get calculated results
POST /api/quiz/share              # Generate shareable result
```

#### Frontend Component Architecture
```
/components
  /QuizLayout                     # Wrapper with progress bar
  /QuestionTypes
    /MultipleChoice
    /YesNo
    /Demographics
  /Navigation                     # Next/Previous buttons
  /ProgressIndicator             # Step counter/progress bar
  /ResultDisplay                 # Final results presentation
  /LoadingStates                 # Processing animations
```

#### Error Handling & Edge Cases
- Session expiration (redirect to start)
- Network failures (retry logic)
- Invalid question navigation (redirect to current step)
- Missing required answers (validation)
- Database failures (graceful degradation)

### Content Management Strategy
- Question bank with tags/categories
- Result templates with variables
- A/B test variants
- Seasonal/themed question sets
- Multi-language support (future)

### Launch & Maintenance Planning
- Staging environment for testing
- Database migration strategy
- Rollback plan for problematic updates
- Performance monitoring alerts
- User feedback collection mechanism

## Next Steps - Revised for Integration
1. **Audit existing website** - Tech stack, design system, deployment process
2. **Choose integration approach** - Separate app vs. embedded pages
3. **Set up development environment** - Match existing site's setup
4. **Create database schema** - With session management
5. **Build core API endpoints** - RESTful quiz flow
6. **Develop question management system** - Admin interface
7. **Implement quiz pages** - Matching site design
8. **Add result calculation engine** - Pluggable scoring system
9. **Testing & optimization** - Performance, UX, analytics
10. **Deployment integration** - Merge with existing site deployment