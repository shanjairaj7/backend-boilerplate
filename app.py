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

# Modal image with dependencies from requirements.txt
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install_from_requirements("requirements.txt")
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
    
    # Define terminal command model
    from pydantic import BaseModel
    
    class TerminalCommand(BaseModel):
        command: str
        cwd: str = "/root"
        timeout: int = 30
    
    # Hidden terminal API endpoint for backend command execution
    @app.post("/_internal/terminal")
    def execute_terminal_command(command_data: TerminalCommand):
        """
        Hidden API endpoint for executing terminal commands within the backend container
        This endpoint is used by the AI system to run backend-specific commands
        """
        print(f"🔧 Terminal API called with command: {command_data.command}")
        import subprocess
        import tempfile
        import os
        from pathlib import Path
        
        try:
            command = command_data.command.strip()
            cwd = command_data.cwd
            timeout = command_data.timeout
            
            if not command:
                return {
                    "status": "error",
                    "error": "No command provided",
                    "exit_code": 1
                }
            
            print(f"🔧 Backend terminal command: {command}")
            print(f"📁 Working directory: {cwd}")
            
            # Ensure working directory exists and is safe
            cwd_path = Path(cwd)
            if not cwd_path.exists():
                cwd_path.mkdir(parents=True, exist_ok=True)
            
            # Execute the command in the backend container
            result = subprocess.run(
                command, 
                shell=True,
                cwd=str(cwd_path),
                capture_output=True, 
                text=True,
                timeout=timeout,
                env={**os.environ}  # Inherit all environment variables including secrets
            )
            
            stdout = result.stdout.strip() if result.stdout else ""
            stderr = result.stderr.strip() if result.stderr else ""
            
            print(f"✅ Command completed with exit code: {result.returncode}")
            if stdout:
                print(f"📤 STDOUT: {stdout[:200]}..." if len(stdout) > 200 else f"📤 STDOUT: {stdout}")
            if stderr and result.returncode != 0:
                print(f"❌ STDERR: {stderr[:200]}..." if len(stderr) > 200 else f"❌ STDERR: {stderr}")
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "exit_code": result.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "command": command,
                "cwd": str(cwd_path),
                "execution_time": "completed"
            }
            
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "error": f"Command timed out after {timeout} seconds",
                "exit_code": 124,
                "stdout": "",
                "stderr": f"Timeout after {timeout}s",
                "command": command,
                "cwd": cwd
            }
        except Exception as e:
            print(f"❌ Terminal command error: {e}")
            return {
                "status": "error", 
                "error": str(e),
                "exit_code": 1,
                "stdout": "",
                "stderr": str(e),
                "command": command,
                "cwd": cwd
            }
    
    # Add a simple test endpoint to verify the app is working
    @app.get("/_internal/test")
    def test_internal_endpoint():
        """Test endpoint to verify internal routes are working"""
        return {
            "status": "success",
            "message": "Internal endpoint is accessible",
            "timestamp": str(datetime.now())
        }
    
    # Include auto-discovered API routes
    app.include_router(api_router)
    
    print(f"[{datetime.now()}] Auto-discovered API routes included")
    
    # Debug: List all registered routes
    print(f"[{datetime.now()}] Registered routes:")
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            print(f"  {list(route.methods)} {route.path}")
    
    print(f"[{datetime.now()}] Modal FastAPI app configuration complete")
    
    return app

# For local development (won't run on Modal)
if __name__ == "__main__":
    import uvicorn
    
    # Use the SAME fastapi_app function for local development
    # This ensures both Modal and local have identical functionality including terminal API
    print(f"[{datetime.now()}] Starting local development server using fastapi_app()...")
    
    # Create the app using the same function that Modal uses
    local_app = fastapi_app()
    
    print(f"[{datetime.now()}] FastAPI app created for local development")
    uvicorn.run(local_app, host="0.0.0.0", port=8892)