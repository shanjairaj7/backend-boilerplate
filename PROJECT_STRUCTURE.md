# Backend Project Structure

This backend template uses a clean, conflict-free Python package structure.

## ✅ Recommended Structure

```
backend/
├── app.py                    # Main FastAPI application
├── db_config.py             # Database configuration (NOT database.py)
├── requirements.txt
├── database/                # Database models folder
│   ├── __init__.py
│   ├── user.py             # SQLAlchemy models
│   └── todo.py             # Example model
├── services/               # API routes and business logic
│   ├── __init__.py
│   ├── health_service.py
│   └── user_service.py
└── routes/                 # Optional: additional route organization
    ├── __init__.py
    └── api_v1.py
```

## 🚫 Common Naming Conflicts to Avoid

### 1. File vs Folder Naming
- ❌ `database.py` + `database/` folder
- ✅ `db_config.py` + `database/` folder

### 2. Import Conflicts
- ❌ `from backend.services import health_service` (when running from backend/)
- ✅ `from services import health_service`

- ❌ `from database.user import User` (when database.py file exists)
- ✅ `from database.user import User` (when only database/ folder exists)

## 📋 Import Guidelines

### Database Models
```python
# In database/user.py
from db_config import Base  # ✅ Clear, no conflicts

# In services/user_service.py  
from database.user import User  # ✅ Clean package import
```

### Service Imports
```python
# In app.py
from services import api_router  # ✅ Correct relative import

# In services/__init__.py
from .health_service import router as health_router  # ✅ Relative import
```

## 🔧 Key Rules

1. **No file/folder name conflicts**: Never have `database.py` and `database/` folder
2. **Relative imports from backend root**: Import as if running from backend/ directory
3. **Use descriptive names**: `db_config.py` instead of `database.py`
4. **Always include `__init__.py`**: Makes folders proper Python packages
5. **Consistent naming**: Use `snake_case` for files and folders

This structure prevents the common `ModuleNotFoundError` issues that occur when Python can't resolve import paths due to naming conflicts.

## 🧪 Testing and Database Setup

**IMPORTANT**: Database tables are NOT auto-created. You must create test files to:
1. Create database tables explicitly
2. Verify models work correctly  
3. Test API endpoints

### Example Test File Pattern
```python
# test_your_feature_setup.py
from db_config import create_tables, get_db_session
from database.your_model import YourModel
import requests

def test_database_setup():
    # Create tables explicitly
    create_tables()
    
    # Test model creation
    with get_db_session() as db:
        test_item = YourModel(name="test")
        db.add(test_item)
        db.commit()
        # Clean up
        db.delete(test_item)
        db.commit()

def test_api_endpoints():
    # Test API endpoints work
    response = requests.get("http://localhost:8001/your-endpoint/")
    assert response.status_code == 200

if __name__ == "__main__":
    test_database_setup()
    test_api_endpoints()
    print("✅ All tests passed!")
```

### Development Workflow
1. Create your SQLAlchemy model in `database/`
2. Create your Pydantic models in `models/`
3. Create your API routes in `services/`
4. **Create a test file** to verify everything works
5. **Run the test file** to create tables and verify functionality
6. Start backend and run integration tests

This approach ensures every feature is properly tested and verified before use.