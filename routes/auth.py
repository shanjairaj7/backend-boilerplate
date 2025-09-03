"""
Authentication Service - Complete Auth System in One File
Contains routes, business logic, database operations, and JWT handling
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional
import os
import secrets

# Database imports
from json_db import JsonDBSession, get_db, create_tables, db

# Router setup
router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# JWT and Password settings
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User data model for JSON storage
class User:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.email = kwargs.get('email')
        self.hashed_password = kwargs.get('hashed_password')
        self.is_active = kwargs.get('is_active', True)
        self.created_at = kwargs.get('created_at')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'hashed_password': self.hashed_password,
            'is_active': self.is_active,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

# Pydantic Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

# Auth Utilities
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        name = payload.get("name")
        if user_id is None:
            return None
        return {"user_id": int(user_id), "name": name}
    except JWTError:
        return None

# Dependencies
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: JsonDBSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(credentials.credentials)
    if token_data is None:
        raise credentials_exception
    
    user_data = db.db.find_one("users", id=token_data["user_id"])
    if user_data is None:
        raise credentials_exception
    
    return User.from_dict(user_data)

# Routes
@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(request: Request):
    user_data = await request.json()
    
    # Validate required fields
    if not user_data.get("email") or not user_data.get("password") or not user_data.get("name"):
        raise HTTPException(status_code=400, detail="Email, password, and name are required")
    
    # Check if name exists (optional - you might want to allow duplicate names)
    # if db.db.exists("users", name=user_data.get("name")):
    #     raise HTTPException(status_code=400, detail="Name already registered")
    
    # Check if email exists (using direct db access)
    if db.exists("users", email=user_data.get("email")):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = hash_password(user_data["password"])
    user_record = db.insert("users", {
        "name": user_data["name"],
        "email": user_data["email"],
        "hashed_password": hashed_password,
        "is_active": True
    })
    
    db_user = User.from_dict(user_record)
    
    # Create token
    access_token = create_access_token(
        data={"sub": str(db_user.id), "name": db_user.name}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": db_user.to_dict()
    }

@router.post("/login")
async def login(request: Request):
    login_data = await request.json()
    
    # Validate required fields
    if not login_data.get("email") or not login_data.get("password"):
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    user_data = db.find_one("users", email=login_data.get("email"))
    
    if not user_data or not verify_password(login_data["password"], user_data["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user_data["is_active"]:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    user = User.from_dict(user_data)
    
    access_token = create_access_token(
        data={"sub": str(user.id), "name": user.name}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user.to_dict()
    }

@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user.to_dict()

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    return {"message": f"User {current_user.name} logged out successfully"}

# Initialize database tables when module is imported
create_tables()