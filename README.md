# DSA Mentor - Modular AI-Powered Coding Coach

A comprehensive Data Structures and Algorithms learning platform with a **modular architecture** featuring a **FastAPI backend** and **Streamlit frontend**.

## 🏗️ Architecture Overview

### Modular Separation
- **Backend (FastAPI)**: AI services, business logic, data management
- **Frontend (Streamlit)**: User interface, interactions, visualizations  
- **Shared**: Common models, schemas, and utilities

```
DSA Mentor/
├── backend/               # FastAPI Backend Services
│   ├── main.py           # FastAPI application entry point
│   ├── api/              # API route handlers
│   └── services/         # Business logic services
├── frontend/             # Streamlit Frontend Application
│   ├── app.py            # Main Streamlit app
│   ├── api_client.py     # Backend API client
│   └── components/       # UI components
├── shared/               # Shared models and utilities
│   ├── models.py         # Pydantic data models
│   └── config.py         # Configuration settings
└── data/                 # Data storage and persistence
```

## 🚀 Quick Start

### Option 1: Start Both Servers (Recommended)
```bash
python start_app.py
```
- Backend: http://localhost:8000
- Frontend: http://localhost:8501
- API Docs: http://localhost:8000/docs

### Option 2: Start Individually

**Backend Only:**
```bash
python start_backend.py
```

**Frontend Only:**
```bash
python start_frontend.py
```

## 📋 Prerequisites

- Python 3.11+
- UV package manager (recommended) or pip

## 🛠️ Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd DSAMentor
```

2. **Install dependencies:**
```bash
# Using UV (recommended)
uv sync

# Using pip
pip install -e .
```

3. **Set up environment variables:**
```bash
# Create .env file
echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
```

4. **Start the application:**
```bash
python start_app.py
```

## 🎯 Features

### 🧠 AI-Powered Components
- **Problem Generator**: Create similar problems for practice
- **Progressive Hint System**: Guided learning without spoilers
- **Code Reviewer**: AI-powered code analysis and feedback
- **Interview Simulator**: Mock coding interviews
- **Smart Debugger**: Code debugging assistance
- **Memory Palace**: Visual learning aids creation

### 📊 Analytics & Tracking
- **Progress Tracker**: Detailed learning analytics
- **Skill Assessment**: Track improvement across topics
- **Achievement System**: Gamified learning milestones
- **Activity Timeline**: Comprehensive learning history

## 🔧 Backend API (FastAPI)

### Core Services
- **AI Service**: Gemini API integration for intelligent responses
- **Problem Service**: Problem generation and management
- **Hint Service**: Progressive hint system logic
- **Code Review Service**: Code analysis and feedback
- **Progress Service**: User analytics and tracking
- **Data Service**: User data and persistence management

### API Endpoints
```
GET  /health                    # Health check
POST /api/problems/generate     # Generate problem variations
POST /api/hints/progressive     # Get progressive hints  
POST /api/code/review          # Analyze and review code
GET  /api/progress/{user_id}   # Get user progress
POST /api/users/profile        # User profile management
```

### API Documentation
Visit http://localhost:8000/docs for interactive API documentation.

## 🎨 Frontend (Streamlit)

### Component Architecture
- **Modular UI Components**: Each feature as a separate component
- **API Client**: Centralized backend communication
- **Session Management**: User state and preferences
- **Responsive Design**: Modern, intuitive interface

### Key Components
- `problem_generator.py`: Problem generation interface
- `hint_system.py`: Progressive hint interface  
- `code_reviewer.py`: Code review interface
- `progress_tracker.py`: Analytics dashboard
- `interview_simulator.py`: Interview practice interface

## 📁 Project Structure

```
DSAMentor/
├── app.py                     # Legacy monolithic app (deprecated)
├── start_app.py              # Main application launcher
├── start_backend.py          # Backend server launcher  
├── start_frontend.py         # Frontend server launcher
├── pyproject.toml            # Project dependencies and metadata
├── uv.lock                   # Dependency lock file
│
├── backend/                  # FastAPI Backend
│   ├── __init__.py
│   ├── main.py              # FastAPI app and routes
│   ├── api/                 # API route handlers
│   │   ├── __init__.py
│   │   ├── problems.py      # Problem-related endpoints
│   │   ├── hints.py         # Hint system endpoints
│   │   ├── code_review.py   # Code review endpoints
│   │   ├── progress.py      # Progress tracking endpoints
│   │   └── users.py         # User management endpoints
│   └── services/            # Business logic services
│       ├── __init__.py
│       ├── ai_service.py    # AI/Gemini integration
│       ├── problem_service.py
│       ├── hint_service.py
│       ├── code_review_service.py
│       ├── progress_service.py
│       └── data_service.py
│
├── frontend/                # Streamlit Frontend
│   ├── __init__.py
│   ├── app.py              # Main Streamlit application
│   ├── api_client.py       # Backend API client
│   ├── components/         # UI components
│   │   ├── __init__.py
│   │   ├── problem_generator.py
│   │   ├── hint_system.py
│   │   ├── code_reviewer.py
│   │   ├── progress_tracker.py
│   │   ├── interview_simulator.py
│   │   ├── debugger.py
│   │   └── memory_palace.py
│   └── pages/              # Additional Streamlit pages
│       └── __init__.py
│
├── shared/                  # Shared utilities and models
│   ├── __init__.py
│   ├── models.py           # Pydantic data models
│   └── config.py           # Configuration management
│
├── data/                   # Data storage
│   ├── user_progress.json  # User progress data
│   └── problems_history.json # Problem generation history
│
├── utils/                  # Legacy utilities (to be migrated)
│   ├── gemini_client.py    # Gemini AI client
│   └── data_manager.py     # Data management utilities
│
└── components/             # Legacy components (deprecated)
    ├── problem_generator.py
    ├── hint_system.py
    ├── code_reviewer.py
    ├── progress_tracker.py
    ├── interview_simulator.py
    ├── debugger.py
    └── memory_palace.py
```

## 🔒 Environment Variables

Create a `.env` file in the project root:

```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
BACKEND_HOST=localhost
BACKEND_PORT=8000
FRONTEND_HOST=localhost  
FRONTEND_PORT=8501
LOG_LEVEL=info
```

## 🧪 Development

### Running in Development Mode

**Backend with auto-reload:**
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend with auto-reload:**
```bash
streamlit run frontend/app.py --server.port 8501
```

### Testing

```bash
# Run backend tests
pytest backend/tests/

# Run frontend tests  
pytest frontend/tests/

# Run all tests
pytest
```

### Code Quality

```bash
# Format code
black .
isort .

# Type checking
mypy backend/ frontend/ shared/

# Linting
flake8 backend/ frontend/ shared/
```

## 📦 Dependencies

### Core Dependencies
- **FastAPI**: Modern web framework for building APIs
- **Streamlit**: App framework for ML and data science
- **Google Generative AI**: Gemini API integration
- **Plotly**: Interactive visualizations
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for FastAPI

### Development Dependencies
- **pytest**: Testing framework
- **black**: Code formatter
- **isort**: Import sorting
- **mypy**: Static type checking
- **flake8**: Code linting

## 🚀 Deployment

### Docker Deployment

```bash
# Build and run with docker-compose
docker-compose up -d

# Or build individually
docker build -t dsa-mentor-backend -f Dockerfile.backend .
docker build -t dsa-mentor-frontend -f Dockerfile.frontend .
```

### Manual Deployment

1. **Deploy Backend:**
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

2. **Deploy Frontend:**
```bash
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes in the appropriate backend/frontend directory
4. Add tests for new functionality
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📝 API Usage Examples

### Generate Problem Variations
```python
import requests

response = requests.post("http://localhost:8000/api/problems/generate", json={
    "problem_text": "Given an array of integers, find two numbers that add up to target",
    "num_variations": 3,
    "difficulty_level": "Same Level",
    "user_id": "user123"
})

problems = response.json()["data"]
```

### Get Progressive Hints
```python
response = requests.post("http://localhost:8000/api/hints/progressive", json={
    "problem": {"statement": "Two Sum problem"},
    "hint_level": 1,
    "user_id": "user123"
})

hint = response.json()["data"]
```

### Analyze Code
```python
response = requests.post("http://localhost:8000/api/code/review", json={
    "code": "def two_sum(nums, target): ...",
    "language": "python",
    "user_id": "user123"
})

analysis = response.json()["data"]
```

## 🎓 Learning Path

1. **Start with Problem Generator**: Create practice problems
2. **Use Progressive Hints**: Learn problem-solving approaches  
3. **Code Review**: Get feedback on your solutions
4. **Track Progress**: Monitor your improvement
5. **Interview Practice**: Prepare for coding interviews

## 🔧 Troubleshooting

### Common Issues

**Backend not starting:**
- Check if port 8000 is available
- Verify Gemini API key in .env file
- Ensure all dependencies are installed

**Frontend not connecting to backend:**
- Confirm backend is running on localhost:8000
- Check firewall settings
- Verify API endpoints are accessible

**Performance issues:**
- Check available memory and CPU
- Consider reducing concurrent requests
- Monitor API rate limits

### Logs

- Backend logs: Check console output from `start_backend.py`
- Frontend logs: Check browser console and Streamlit logs
- Application logs: Check `logs/` directory if configured

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini API for AI capabilities
- Streamlit team for the amazing framework
- FastAPI team for the modern web framework
- Open source community for various tools and libraries

---

## 🆕 Migration from Monolithic Architecture

This version represents a complete migration from the previous monolithic Streamlit application to a modern, modular architecture:

### Key Improvements
- **Separation of Concerns**: Clear division between UI and business logic
- **Scalability**: Independent scaling of frontend and backend
- **Maintainability**: Modular codebase easier to maintain and extend
- **API-First**: RESTful API enables future integrations
- **Performance**: Optimized for better resource utilization

### Migration Benefits  
- 🚀 Better performance and responsiveness
- 🔧 Easier development and debugging
- 📈 Improved scalability and deployment options
- 🧪 Better testability and code quality
- 🔌 API enables mobile apps and integrations

Ready to start your DSA learning journey? Run `python start_app.py` and visit http://localhost:8501! 🎓
