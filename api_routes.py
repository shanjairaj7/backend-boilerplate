"""
API Routes Handler
Contains all API logic and routes that will be served under /api prefix
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any
import os

# Create main API router
api_router = APIRouter()

# Security scheme
security = HTTPBearer()

# Request/Response Models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    is_active: bool

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class HealthResponse(BaseModel):
    status: str
    services: Dict[str, str]
    timestamp: str

# Database Models (Placeholder - would normally import from database module)
class User:
    def __init__(self, id: int, username: str, email: str, is_active: bool = True):
        self.id = id
        self.username = username
        self.email = email
        self.is_active = is_active
        self.created_at = datetime.now()

# In-memory user storage (for demo - replace with actual database)
users_db = {
    1: User(1, "admin", "admin@example.com", True),
    2: User(2, "user", "user@example.com", True)
}

# Utility Functions
def get_user_by_username(username: str) -> Optional[User]:
    """Get user by username from database"""
    for user in users_db.values():
        if user.username == username:
            return user
    return None

def get_user_by_id(user_id: int) -> Optional[User]:
    """Get user by ID from database"""
    return users_db.get(user_id)

def create_access_token(user_id: int) -> str:
    """Create access token for user (simplified - use proper JWT in production)"""
    return f"token_user_{user_id}_{int(datetime.now().timestamp())}"

def verify_token(token: str) -> Optional[int]:
    """Verify access token and return user ID (simplified)"""
    try:
        parts = token.split("_")
        if len(parts) >= 3 and parts[0] == "token" and parts[1] == "user":
            return int(parts[2])
    except:
        pass
    return None

# Dependency Functions
async def get_current_user(token: str = Depends(security)) -> User:
    """Get current authenticated user"""
    user_id = verify_token(token.credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

# API Routes

@api_router.get("/", response_model=Dict[str, Any])
def api_root():
    """API root endpoint"""
    return {
        "message": "Backend API is running",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/auth/*",
            "users": "/api/users/*",
            "health": "/api/health"
        },
        "timestamp": str(datetime.now())
    }

@api_router.get("/health", response_model=HealthResponse)
def api_health():
    """Detailed API health check"""
    
    # Check various services
    services = {
        "api": "healthy",
        "database": "healthy",  # Would check actual DB connection
        "auth": "healthy",
        "cache": "healthy"
    }
    
    # Overall status
    overall_status = "healthy" if all(s == "healthy" for s in services.values()) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        services=services,
        timestamp=str(datetime.now())
    )

# Authentication Routes
@api_router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate):
    """Register a new user"""
    
    # Check if user already exists
    if get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new user (simplified - would hash password, etc.)
    new_id = max(users_db.keys()) + 1 if users_db else 1
    new_user = User(new_id, user_data.username, user_data.email, True)
    users_db[new_id] = new_user
    
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        created_at=new_user.created_at,
        is_active=new_user.is_active
    )

@api_router.post("/auth/login", response_model=TokenResponse)
def login_user(login_data: UserLogin):
    """Login user and return access token"""
    
    # Find user
    user = get_user_by_username(login_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # In production, verify hashed password
    # For demo, accept any password for existing users
    
    # Create access token
    access_token = create_access_token(user.id)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=3600  # 1 hour
    )

@api_router.post("/auth/logout")
def logout_user(current_user: User = Depends(get_current_user)):
    """Logout user (invalidate token)"""
    return {"message": "Successfully logged out", "user": current_user.username}

# User Routes
@api_router.get("/users/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at,
        is_active=current_user.is_active
    )

@api_router.get("/users", response_model=List[UserResponse])
def list_users(current_user: User = Depends(get_current_user)):
    """List all users (requires authentication)"""
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at,
            is_active=user.is_active
        )
        for user in users_db.values()
    ]

@api_router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, current_user: User = Depends(get_current_user)):
    """Get user by ID"""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
        is_active=user.is_active
    )

# Environment and System Routes
@api_router.get("/system/env")
def get_environment_info():
    """Get environment information"""
    return {
        "platform": "Modal.com",
        "python_version": os.environ.get("PYTHON_VERSION", "3.11"),
        "environment_variables": {
            key: "***" if "key" in key.lower() or "secret" in key.lower() or "token" in key.lower() 
            else value for key, value in os.environ.items() 
            if not key.startswith("_")
        },
        "timestamp": str(datetime.now())
    }

@api_router.get("/system/status")
def get_system_status():
    """Get system status"""
    return {
        "status": "operational",
        "uptime": "running",
        "memory": "available",
        "cpu": "normal",
        "disk": "available",
        "network": "connected",
        "timestamp": str(datetime.now())
    }

# Demo/Test Routes
@api_router.get("/demo/ping")
def ping():
    """Simple ping endpoint"""
    return {"message": "pong", "timestamp": str(datetime.now())}

@api_router.post("/demo/echo")
def echo(data: Dict[str, Any]):
    """Echo back the provided data"""
    return {
        "echoed_data": data,
        "received_at": str(datetime.now()),
        "message": "Data echoed successfully"
    }

# Error handling example
@api_router.get("/demo/error")
def trigger_error():
    """Trigger an error for testing"""
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="This is a test error"
    )