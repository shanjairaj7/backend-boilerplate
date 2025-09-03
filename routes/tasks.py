"""
Tasks route - simulating the exact problematic pattern that was causing RecursionError
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from json_db import db, JsonDBSession, get_db
from datetime import datetime

router = APIRouter(prefix="/tasks", tags=["tasks"])

# THIS IS THE PROBLEMATIC PATTERN THAT WOULD CAUSE RecursionError:
# @router.post("/")
# def create_task(request: Request, task_data: dict, db_session: JsonDBSession = Depends(get_db)):
#     """This pattern causes circular reference error!"""
#     pass

# THIS IS THE FIXED PATTERN:
@router.post("/")
async def create_task(request: Request):
    """Create a new task using the SAFE CODE pattern"""
    task_data = await request.json()
    
    # Validate required fields
    if not task_data.get("title"):
        raise HTTPException(status_code=400, detail="Title is required")
    
    # Create task with default values
    task = {
        "title": task_data["title"],
        "description": task_data.get("description", ""),
        "status": task_data.get("status", "todo"),
        "user_id": task_data.get("user_id"),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    # Use direct db access (not db_session.db) 
    result = db.insert("tasks", task)
    
    # Return a clean dict to avoid circular references
    return {
        "id": result,
        "title": task["title"],
        "description": task["description"], 
        "status": task["status"],
        "user_id": task["user_id"],
        "created_at": task["created_at"],
        "updated_at": task["updated_at"]
    }

@router.get("/")
def get_tasks():
    """Get all tasks"""
    tasks = db.find_all("tasks")
    return tasks

@router.get("/{task_id}")
def get_task(task_id: int):
    """Get a specific task"""
    task = db.find_one("tasks", id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task