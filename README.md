# Backend Boilerplate

A modern FastAPI backend boilerplate with authentication, database integration, and project structure for rapid API development.

## Features

- **FastAPI** with automatic OpenAPI documentation
- **SQLAlchemy** for database ORM
- **Authentication System** with JWT tokens
- **User Management** (signup, login, profile)
- **Password Hashing** with bcrypt
- **Database Migrations** ready
- **Error Handling** and validation
- **Testing Setup** with pytest
- **Python Error Checking** with AST analyzer

## Quick Start

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database URL and secret key

# Run the application
python app.py
# Or with uvicorn: uvicorn app:app --reload
```

## API Documentation

Once running, visit:
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Project Structure

```
├── app.py              # Main FastAPI application
├── db_config.py        # Database configuration
├── requirements.txt    # Python dependencies
├── database/           # SQLAlchemy models
├── models/            # Pydantic schemas
├── routes/            # API endpoints
├── services/          # Business logic
├── utils/             # Utility functions
└── test_auth_api.py   # API testing
```

## Authentication

The boilerplate includes a complete authentication system:

- **POST /auth/signup** - User registration
- **POST /auth/login** - User login (returns JWT token)
- **GET /auth/profile** - Get user profile (requires auth)
- **POST /auth/change-password** - Change password
- **POST /auth/reset-password** - Password reset

See `AUTH_README.md` for detailed authentication documentation.

## Database

Uses SQLAlchemy with support for:
- User model with authentication
- Database migrations
- Connection pooling
- Environment-based configuration

## Testing

```bash
# Run tests
python test_auth_api.py

# Check for Python errors
python python-error-checker.py
```

## Environment Variables

```env
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

This boilerplate is designed to be cloned and customized for new projects. It provides a solid foundation with authentication, database integration, and modern FastAPI practices.