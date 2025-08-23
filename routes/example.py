"""
Example Service - Shows how easy it is to add new routes
Contains routes and business logic in one simple file
Just create this file and it gets auto-discovered!
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List
from routes.auth import get_current_user, User

# Router setup
router = APIRouter(prefix="/example", tags=["example"])

# Models
class TodoItem(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    created_at: datetime

class TodoCreate(BaseModel):
    title: str
    description: str = ""

# In-memory storage (in real app, use database)
todos_db = {}
next_id = 1

# Business Logic
def create_todo(todo_data: TodoCreate, user_id: int) -> TodoItem:
    """Create a new todo item"""
    global next_id
    todo = TodoItem(
        id=next_id,
        title=todo_data.title,
        description=todo_data.description,
        completed=False,
        created_at=datetime.now()
    )
    todos_db[next_id] = {"todo": todo, "user_id": user_id}
    next_id += 1
    return todo

def get_user_todos(user_id: int) -> List[TodoItem]:
    """Get all todos for a user"""
    return [
        item["todo"] for item in todos_db.values() 
        if item["user_id"] == user_id
    ]

# Routes
@router.get("/")
def example_root():
    """Example service root endpoint"""
    return {
        "message": "Example Service is running!",
        "description": "This shows how easy it is to add new services",
        "endpoints": [
            "/example/todos - Get your todos (requires auth)",
            "/example/todos - Create a new todo (requires auth)",
            "/example/public - Public endpoint (no auth required)"
        ],
        "timestamp": datetime.now().isoformat()
    }

@router.get("/public")
def public_endpoint():
    """Public endpoint - no authentication required"""
    return {
        "message": "This is a public endpoint!",
        "anyone_can_access": True,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/todos", response_model=List[TodoItem])
def get_todos(current_user: User = Depends(get_current_user)):
    """Get user's todos - requires authentication"""
    return get_user_todos(current_user.id)

@router.post("/todos", response_model=TodoItem)
def create_todo_endpoint(
    todo_data: TodoCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new todo - requires authentication"""
    return create_todo(todo_data, current_user.id)

@router.delete("/todos/{todo_id}")
def delete_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user)
):
    """Delete a todo - requires authentication"""
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    if todos_db[todo_id]["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not your todo")
    
    deleted_todo = todos_db[todo_id]["todo"]
    del todos_db[todo_id]
    
    return {
        "message": f"Todo '{deleted_todo.title}' deleted successfully",
        "deleted_todo_id": todo_id
    }