from fastapi import APIRouter

api_router = APIRouter()

# Import health service
try:
    from .health_service import router as health_router
    api_router.include_router(health_router, tags=["health"])
except ImportError:
    pass

# Import authentication service (optional - can be excluded if not needed)
try:
    from .auth_service import router as auth_router
    api_router.include_router(auth_router)
    print("✅ Authentication service loaded")
except ImportError as e:
    print(f"⚠️ Authentication service not loaded: {e}")
    pass

# Add your service imports here as you create them