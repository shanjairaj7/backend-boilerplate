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

# Generate Modal-compliant volume name
def generate_volume_name(app_name: str) -> str:
    """Generate a Modal-compliant volume name that's under 64 characters"""
    import hashlib
    import re
    
    base_name = app_name
    suffix = "_database"  # Use underscore for volumes
    
    # If the full name would be too long, create a shorter version
    full_name = f"{base_name}{suffix}"
    if len(full_name) >= 64:
        # Create a hash-based short name that's deterministic
        hash_obj = hashlib.md5(app_name.encode())
        short_hash = hash_obj.hexdigest()[:8]
        
        # Use first part of app_name + hash + suffix
        max_base_length = 64 - len(suffix) - len(short_hash) - 1  # -1 for separator
        short_base = base_name[:max_base_length].rstrip('_-')
        full_name = f"{short_base}_{short_hash}{suffix}"
    
    # Ensure it's under 64 chars and valid
    full_name = full_name[:63]  # Leave room for safety
    
    # Replace any invalid characters with underscores
    full_name = re.sub(r'[^a-zA-Z0-9._-]', '_', full_name)
    
    # Replace consecutive separators with single underscore
    full_name = re.sub(r'[-_]+', '_', full_name)
    
    # Ensure it doesn't start or end with separator
    full_name = full_name.strip('-_')
    
    return full_name

# Create persistent volume for JSON database with Modal-compliant name
volume_name = generate_volume_name(APP_NAME)
database_volume = modal.Volume.from_name(volume_name, create_if_missing=True)
print(f"📦 Using database volume: {volume_name}")

# Modal image with dependencies from requirements.txt - Force rebuild v2
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
    volumes={f"/root/json_data": database_volume},  # Mount persistent volume for JSON database
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
        description=APP_DESCRIPTION,
        redirect_slashes=False  # Disable automatic trailing slash redirects
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
    @app.post("/_internal/terminal", include_in_schema=False)
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
                    "exit_code": 1,
                    "stdout": "",
                    "stderr": "Empty command string",
                    "command": "",
                    "cwd": cwd,
                    "suggestion": "Please provide a valid command to execute. Example: 'ls', 'python --version', 'pip list'"
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
            error_msg = f"Command timed out after {timeout} seconds"
            print(f"⏰ Terminal timeout: {error_msg}")
            return {
                "status": "error",
                "error": error_msg,
                "exit_code": 124,
                "stdout": "",
                "stderr": f"Timeout after {timeout}s",
                "command": command,
                "cwd": cwd,
                "suggestion": "Try increasing the timeout or break the command into smaller steps. If persistent, redeploy the backend and try again."
            }
        except FileNotFoundError as e:
            error_msg = f"Command not found: {str(e)}"
            print(f"❓ Terminal command not found: {error_msg}")
            return {
                "status": "error", 
                "error": error_msg,
                "exit_code": 127,
                "stdout": "",
                "stderr": str(e),
                "command": command,
                "cwd": cwd,
                "suggestion": "The command or executable was not found in the container. Verify the command exists or redeploy the backend with required dependencies."
            }
        except PermissionError as e:
            error_msg = f"Permission denied: {str(e)}"
            print(f"🔒 Terminal permission error: {error_msg}")
            return {
                "status": "error", 
                "error": error_msg,
                "exit_code": 126,
                "stdout": "",
                "stderr": str(e),
                "command": command,
                "cwd": cwd,
                "suggestion": "Permission denied. The command may require elevated privileges or write access to protected directories."
            }
        except Exception as e:
            error_msg = f"Terminal execution failed: {str(e)}"
            print(f"❌ Terminal command error: {error_msg}")
            return {
                "status": "error", 
                "error": error_msg,
                "exit_code": 1,
                "stdout": "",
                "stderr": str(e),
                "command": command,
                "cwd": cwd,
                "suggestion": "Unexpected error occurred during command execution. Try redeploying the backend and attempting the command again. If the issue persists, check the backend logs."
            }
    
    # Add a simple test endpoint to verify the app is working
    @app.get("/_internal/test", include_in_schema=False)
    def test_internal_endpoint():
        """Test endpoint to verify internal routes are working"""
        return {
            "status": "success",
            "message": "Internal endpoint is accessible",
            "timestamp": str(datetime.now())
        }
    
    # Stealth database inspection endpoint - hidden from OpenAPI docs
    @app.get("/_internal/db/inspect", include_in_schema=False)
    def inspect_database():
        """
        Hidden database inspection endpoint - not visible in OpenAPI documentation
        Provides complete visibility into all JSON database tables and contents
        """
        import json
        import os
        from pathlib import Path
        
        try:
            # Import JSON DB instance
            from json_db import db
            
            result = {
                "database_path": str(db.db_dir),
                "tables": {},
                "metadata": {
                    "table_count": 0,
                    "total_records": 0,
                    "file_sizes": {},
                    "inspection_timestamp": str(datetime.now())
                }
            }
            
            # Check if database directory exists
            if not db.db_dir.exists():
                return {
                    "status": "warning",
                    "message": "Database directory does not exist",
                    "database_path": str(db.db_dir),
                    "tables": {},
                    "metadata": result["metadata"]
                }
            
            # Find all JSON database files
            db_files = list(db.db_dir.glob("*.json"))
            result["metadata"]["table_count"] = len(db_files)
            
            # Process each JSON file
            for file_path in db_files:
                # Extract table name from filename (remove db_name prefix if present)
                filename = file_path.stem
                if filename.startswith(f"{db.db_name}_"):
                    table_name = filename[len(f"{db.db_name}_"):]
                else:
                    table_name = filename
                
                try:
                    # Get file size
                    file_size = file_path.stat().st_size
                    result["metadata"]["file_sizes"][table_name] = f"{file_size} bytes"
                    
                    # Load and parse JSON content
                    with open(file_path, 'r') as f:
                        table_data = json.load(f)
                    
                    # Store table data and count records
                    result["tables"][table_name] = table_data
                    record_count = len(table_data) if isinstance(table_data, list) else 1
                    result["metadata"]["total_records"] += record_count
                    
                    print(f"📋 Inspected table '{table_name}': {record_count} records ({file_size} bytes)")
                    
                except json.JSONDecodeError as e:
                    result["tables"][table_name] = {
                        "error": "Invalid JSON",
                        "details": str(e)
                    }
                    print(f"❌ JSON decode error in table '{table_name}': {e}")
                    
                except Exception as e:
                    result["tables"][table_name] = {
                        "error": "File read error", 
                        "details": str(e)
                    }
                    print(f"❌ File read error in table '{table_name}': {e}")
            
            print(f"🔍 Database inspection complete: {len(result['tables'])} tables, {result['metadata']['total_records']} total records")
            
            return {
                "status": "success",
                **result
            }
            
        except ImportError:
            return {
                "status": "error",
                "message": "JSON database module not available",
                "error": "Could not import json_db module"
            }
        except Exception as e:
            print(f"❌ Database inspection error: {e}")
            return {
                "status": "error",
                "message": "Database inspection failed",
                "error": str(e),
                "timestamp": str(datetime.now())
            }
    
    # Unified table management endpoint - stealth API for all table operations
    from pydantic import BaseModel
    
    class TableManageRequest(BaseModel):
        operation: str  # "insert", "update", "delete", "get"
        data: dict = None  # Record data for insert/update
        row_id: int = None  # Required for update/delete
        filters: dict = None  # Optional filters for get operations
    
    @app.post("/_internal/db/tables/{table_name}/manage", include_in_schema=False)
    def manage_table_data(table_name: str, request: TableManageRequest):
        """
        Unified table management endpoint - handles all CRUD operations
        Hidden from OpenAPI documentation - stealth endpoint
        """
        import json
        from datetime import datetime
        
        try:
            # Import JSON DB instance
            from json_db import db
            
            operation = request.operation.lower()
            print(f"🔧 Table management: {operation} on table '{table_name}'")
            
            if operation == "get":
                # Get table data or specific records
                if request.filters:
                    records = db.find_all(table_name, **request.filters)
                elif request.row_id:
                    record = db.find_one(table_name, id=request.row_id)
                    records = [record] if record else []
                else:
                    records = db.find_all(table_name)
                
                return {
                    "status": "success",
                    "operation": "get",
                    "table_name": table_name,
                    "affected_rows": len(records),
                    "data": records,
                    "message": f"Retrieved {len(records)} record(s) from {table_name}"
                }
            
            elif operation == "insert":
                # Insert new record
                if not request.data:
                    return {
                        "status": "error",
                        "operation": "insert",
                        "table_name": table_name,
                        "error": "No data provided for insert operation"
                    }
                
                # Insert the record (json_db will auto-add id and created_at)
                inserted_record = db.insert(table_name, request.data.copy())
                
                print(f"✅ Inserted record with ID {inserted_record.get('id')} into {table_name}")
                
                return {
                    "status": "success",
                    "operation": "insert",
                    "table_name": table_name,
                    "affected_rows": 1,
                    "data": inserted_record,
                    "message": f"Record inserted successfully into {table_name}"
                }
            
            elif operation == "update":
                # Update existing record
                if not request.row_id:
                    return {
                        "status": "error",
                        "operation": "update",
                        "table_name": table_name,
                        "error": "row_id is required for update operation"
                    }
                
                if not request.data:
                    return {
                        "status": "error",
                        "operation": "update",
                        "table_name": table_name,
                        "error": "No data provided for update operation"
                    }
                
                # Check if record exists
                existing_record = db.find_one(table_name, id=request.row_id)
                if not existing_record:
                    return {
                        "status": "error",
                        "operation": "update",
                        "table_name": table_name,
                        "error": f"Record with id {request.row_id} not found in {table_name}"
                    }
                
                # Update the record (json_db will auto-add updated_at)
                update_success = db.update_one(
                    table_name, 
                    {"id": request.row_id}, 
                    request.data
                )
                
                if update_success:
                    # Get the updated record
                    updated_record = db.find_one(table_name, id=request.row_id)
                    print(f"✅ Updated record ID {request.row_id} in {table_name}")
                    
                    return {
                        "status": "success",
                        "operation": "update",
                        "table_name": table_name,
                        "affected_rows": 1,
                        "data": updated_record,
                        "message": f"Record {request.row_id} updated successfully in {table_name}"
                    }
                else:
                    return {
                        "status": "error",
                        "operation": "update",
                        "table_name": table_name,
                        "error": f"Failed to update record {request.row_id} in {table_name}"
                    }
            
            elif operation == "delete":
                # Delete record
                if not request.row_id:
                    return {
                        "status": "error",
                        "operation": "delete",
                        "table_name": table_name,
                        "error": "row_id is required for delete operation"
                    }
                
                # Check if record exists before deletion
                existing_record = db.find_one(table_name, id=request.row_id)
                if not existing_record:
                    return {
                        "status": "error",
                        "operation": "delete",
                        "table_name": table_name,
                        "error": f"Record with id {request.row_id} not found in {table_name}"
                    }
                
                # Delete the record
                delete_success = db.delete_one(table_name, id=request.row_id)
                
                if delete_success:
                    print(f"✅ Deleted record ID {request.row_id} from {table_name}")
                    
                    return {
                        "status": "success",
                        "operation": "delete",
                        "table_name": table_name,
                        "affected_rows": 1,
                        "data": {"deleted_id": request.row_id},
                        "message": f"Record {request.row_id} deleted successfully from {table_name}"
                    }
                else:
                    return {
                        "status": "error",
                        "operation": "delete",
                        "table_name": table_name,
                        "error": f"Failed to delete record {request.row_id} from {table_name}"
                    }
            
            else:
                return {
                    "status": "error",
                    "operation": operation,
                    "table_name": table_name,
                    "error": f"Unsupported operation: {operation}. Supported: insert, update, delete, get"
                }
        
        except ImportError:
            return {
                "status": "error",
                "operation": request.operation,
                "table_name": table_name,
                "error": "JSON database module not available"
            }
        except Exception as e:
            print(f"❌ Table management error for {table_name}: {e}")
            return {
                "status": "error",
                "operation": request.operation,
                "table_name": table_name,
                "error": f"Table management failed: {str(e)}"
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