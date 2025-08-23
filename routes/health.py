"""
Health Service - Complete Health System in One File
Contains routes, business logic, and health checking functionality
"""
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from typing import Dict
import os

# Router setup
router = APIRouter(prefix="/health", tags=["health"])

# Models
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    service: str
    environment: str
    uptime: str
    checks: Dict[str, str]

class PingResponse(BaseModel):
    message: str
    timestamp: str

# Business Logic
def check_database() -> str:
    """Check database connectivity"""
    try:
        from db_config import engine
        with engine.connect():
            return "healthy"
    except Exception:
        return "unhealthy"

def check_auth_service() -> str:
    """Check if auth service is available"""
    try:
        from routes.auth import router as auth_router
        return "healthy" if auth_router else "unhealthy"
    except Exception:
        return "unhealthy"

def get_system_info() -> Dict[str, str]:
    """Get basic system information"""
    return {
        "platform": "Modal.com Compatible",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "python_version": "3.11+",
        "framework": "FastAPI"
    }

# Routes
@router.get("/", response_model=HealthResponse)
def health_check():
    """Main health check endpoint"""
    checks = {
        "database": check_database(),
        "auth": check_auth_service(),
        "api": "healthy"
    }
    
    overall_status = "healthy" if all(check == "healthy" for check in checks.values()) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now().isoformat(),
        service="backend-api",
        environment=os.getenv("ENVIRONMENT", "development"),
        uptime="running",
        checks=checks
    )

@router.get("/ping", response_model=PingResponse)
def ping():
    """Simple ping endpoint"""
    return PingResponse(
        message="pong",
        timestamp=datetime.now().isoformat()
    )

@router.get("/status")
def detailed_status():
    """Detailed system status with additional info"""
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "system": get_system_info(),
        "services": {
            "health_service": "running",
            "auth_service": "running",
            "api_gateway": "running"
        },
        "database": {
            "status": check_database(),
            "type": "SQLite",
            "path": "./app_database.db"
        }
    }

@router.get("/version")
def get_version():
    """Get API version information"""
    return {
        "version": "1.0.0",
        "api_name": "Backend API",
        "build": "modal-compatible",
        "timestamp": datetime.now().isoformat()
    }