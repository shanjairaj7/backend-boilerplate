"""
Modal.com Compatible FastAPI Backend - Production Ready Boilerplate
Main application file with dynamic Modal configuration for mass deployment
"""

import os
import modal
from datetime import datetime

# Dynamic configuration for production deployment
APP_NAME = os.getenv("MODAL_APP_NAME", "backend-api")
APP_TITLE = os.getenv("APP_TITLE", "AI Generated Backend")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "Auto-generated FastAPI backend")
SECRET_NAME = os.getenv("MODAL_SECRET_NAME", f"{APP_NAME}-secrets")

print(f"🚀 Initializing Modal app: {APP_NAME}")
print(f"📋 Using secret: {SECRET_NAME}")

# Modal app configuration with dynamic naming
modal_app = modal.App(APP_NAME)
app = modal_app  # Alias for Modal deployment

# Modal image with required dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install([
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "pydantic==2.5.0",
        "sqlalchemy==2.0.23",
        "python-multipart==0.0.6",
        "python-dotenv==1.0.0",
        "passlib==1.7.4",
        "python-jose==3.3.0",
        "bcrypt==4.0.1",
        "cryptography==41.0.7"
    ])
    .add_local_dir(".", "/root")
)

# Modal ASGI app with secrets and configuration
@modal_app.function(
    image=image,
    secrets=[
        modal.Secret.from_name(SECRET_NAME),  # Dynamic secret name per deployment
    ],
)
@modal.asgi_app()
def fastapi_app():
    """Create and configure FastAPI application for Modal deployment"""
    
    # Import dependencies inside function for Modal compatibility
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from routes import api_router  # Import auto-discovery router registry
    
    # Create FastAPI app with dynamic configuration
    app = FastAPI(
        title=APP_TITLE, 
        version="1.0.0",
        description=APP_DESCRIPTION
    )
    
    print(f"[{datetime.now()}] FastAPI app instance created for Modal deployment")
    
    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Health check endpoint (root)
    @app.get("/")
    def read_root():
        return {
            "app_name": APP_NAME,
            "title": APP_TITLE,
            "status": "Backend running on Modal.com",
            "timestamp": str(datetime.now()),
            "environment": "modal"
        }
    
    @app.get("/health")
    def health_check():
        return {
            "status": "healthy",
            "service": "Backend API",
            "platform": "Modal.com",
            "timestamp": str(datetime.now())
        }
    
    # Include auto-discovered API routes
    app.include_router(api_router)
    
    print(f"[{datetime.now()}] Auto-discovered API routes included")
    print(f"[{datetime.now()}] Modal FastAPI app configuration complete")
    
    return app

# For local development (won't run on Modal)
if __name__ == "__main__":
    import uvicorn
    
    # Import for local development
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from routes import api_router
    
    # Create local app with dynamic configuration
    local_app = FastAPI(title=f"{APP_TITLE} (Local)", version="1.0.0")
    
    local_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @local_app.get("/")
    def read_root():
        return {"status": "Backend running locally", "timestamp": str(datetime.now())}
    
    @local_app.get("/health")
    def health_check():
        return {"status": "healthy", "environment": "local", "timestamp": str(datetime.now())}
    
    # Include auto-discovered routes
    local_app.include_router(api_router)
    
    print(f"[{datetime.now()}] Starting local development server...")
    uvicorn.run(local_app, host="0.0.0.0", port=8892)