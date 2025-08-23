# How to Add Routes - Simple Guide

This backend uses an **auto-discovery system** that makes adding new routes extremely simple. Just create a file and it works!

## 🚀 Quick Start

### Step 1: Create Your Service File

Create a new file in the `routes/` directory:

```bash
touch routes/my_service.py
```

### Step 2: Add Your Routes

Open the file and add this basic template:

```python
"""
My Service - Description of what this service does
"""
from fastapi import APIRouter
from datetime import datetime

# Router setup - this gets auto-discovered
router = APIRouter(prefix="/my-service", tags=["my-service"])

@router.get("/")
def my_service_root():
    """Root endpoint for my service"""
    return {
        "message": "My service is working!",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/hello")
def say_hello():
    """A simple hello endpoint"""
    return {"message": "Hello from my service!"}
```

### Step 3: That's It!

Restart the server and your routes are automatically available:

- `http://localhost:8892/my-service/`
- `http://localhost:8892/my-service/hello`

## 🔐 Adding Authentication

If you need authenticated routes, import the auth system:

```python
from fastapi import APIRouter, Depends
from routes.auth import get_current_user, User
from datetime import datetime

router = APIRouter(prefix="/protected", tags=["protected"])

@router.get("/profile")
def get_my_data(current_user: User = Depends(get_current_user)):
    """This endpoint requires authentication"""
    return {
        "message": f"Hello {current_user.username}!",
        "user_id": current_user.id,
        "timestamp": datetime.now().isoformat()
    }
```

## 📊 Complete Example - Todo Service

Here's a complete example with database operations, authentication, and CRUD:

```python
"""
Todo Service - Complete example with auth and database operations
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List
from routes.auth import get_current_user, User

router = APIRouter(prefix="/todos", tags=["todos"])

# Models
class TodoCreate(BaseModel):
    title: str
    description: str = ""

class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    created_at: datetime

# In-memory storage (use database in real app)
todos_db = {}
next_id = 1

# Routes
@router.get("/", response_model=List[TodoResponse])
def get_todos(current_user: User = Depends(get_current_user)):
    """Get all user's todos"""
    user_todos = [
        todo for todo in todos_db.values()
        if todo["user_id"] == current_user.id
    ]
    return [todo["data"] for todo in user_todos]

@router.post("/", response_model=TodoResponse)
def create_todo(
    todo_data: TodoCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new todo"""
    global next_id

    todo = TodoResponse(
        id=next_id,
        title=todo_data.title,
        description=todo_data.description,
        completed=False,
        created_at=datetime.now()
    )

    todos_db[next_id] = {
        "data": todo,
        "user_id": current_user.id
    }
    next_id += 1

    return todo

@router.delete("/{todo_id}")
def delete_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user)
):
    """Delete a todo"""
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="Todo not found")

    if todos_db[todo_id]["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not your todo")

    del todos_db[todo_id]
    return {"message": "Todo deleted successfully"}
```

## 🏗️ File Structure

```
routes/
├── auth.py        # 🔐 Authentication (signup, login, profile)
├── health.py      # 🏥 Health checks and monitoring
├── example.py     # 📝 Example todo service
└── my_service.py  # 🆕 Your new service!
```

## 🔍 Auto-Discovery Rules

The system automatically finds and registers any Python file in `routes/` that has:

1. A `router` variable
2. The router is a FastAPI `APIRouter` instance

## 🛠️ Available Utilities

### Authentication

```python
from routes.auth import get_current_user, User
# Use as dependency: current_user: User = Depends(get_current_user)
```

### Database

```python
from db_config import get_db
from sqlalchemy.orm import Session
# Use as dependency: db: Session = Depends(get_db)
```

### Models & Validation

```python
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
```

## 🚨 Common Patterns

### Public Endpoint

```python
@router.get("/public")
def public_endpoint():
    return {"message": "Anyone can access this!"}
```

### Protected Endpoint

```python
@router.get("/private")
def private_endpoint(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}!"}
```

### With Database

```python
from sqlalchemy.orm import Session
from db_config import get_db

@router.get("/data")
def get_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Your database operations here
    return {"data": "from database"}
```

## ✅ That's It!

The system is designed to be **extremely simple**:

1. **Create a file** in `routes/`
2. **Add a router** with your endpoints
3. **Restart the server**
4. **Your routes work!**

No configuration files, no registration needed - just code and go! 🚀
