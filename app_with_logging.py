from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services import api_router
import sys
from datetime import datetime
import traceback

# Force unbuffered output for real-time logging
sys.stdout = sys.stdout  # This ensures line buffering
sys.stderr = sys.stderr

def log(message, level="INFO"):
    """Helper function for consistent logging with timestamps"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] [{level}] {message}", flush=True)

log("Starting FastAPI application...", "STARTUP")

app = FastAPI(title="Project Backend with Logging", version="1.0.0")

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    """Initialize database tables on application startup"""
    log("=== APPLICATION STARTUP ===", "STARTUP")
    log("Initializing database...", "INFO")
    
    try:
        from database import create_tables
        log("Importing database module...", "DEBUG")
        create_tables()
        log("✅ Database tables initialized successfully", "SUCCESS")
    except ImportError as e:
        log(f"No database configuration found: {e}", "WARNING")
        log("Skipping database initialization", "INFO")
    except Exception as e:
        log(f"Database initialization failed: {e}", "ERROR")
        log(f"Traceback: {traceback.format_exc()}", "ERROR")
    
    log("Starting API routes registration...", "INFO")
    log("=== STARTUP COMPLETE ===", "STARTUP")

@app.on_event("shutdown")
def shutdown_event():
    """Clean shutdown logging"""
    log("=== APPLICATION SHUTDOWN ===", "SHUTDOWN")
    log("Closing database connections...", "INFO")
    log("Cleanup complete", "INFO")

# CORS configuration for frontend
log("Configuring CORS middleware...", "INFO")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
log("CORS middleware configured", "SUCCESS")

# Include the main router
log("Including API router...", "INFO")
app.include_router(api_router)
log("API router included", "SUCCESS")

@app.get("/")
def read_root():
    log("GET / - Root endpoint accessed", "REQUEST")
    try:
        response = {"status": "Backend running", "timestamp": str(datetime.now())}
        log(f"Root response: {response}", "DEBUG")
        return response
    except Exception as e:
        log(f"Error in root endpoint: {e}", "ERROR")
        log(f"Traceback: {traceback.format_exc()}", "ERROR")
        raise

@app.get("/health")
def health_check():
    log("GET /health - Health check requested", "REQUEST")
    try:
        # Simulate checking various services
        log("Checking database connection...", "DEBUG")
        db_status = "healthy"  # In real app, would check actual DB
        
        log("Checking external services...", "DEBUG")
        external_status = "healthy"
        
        response = {
            "status": "healthy",
            "database": db_status,
            "external_services": external_status,
            "timestamp": str(datetime.now())
        }
        
        log(f"Health check response: {response}", "DEBUG")
        return response
    except Exception as e:
        log(f"Error during health check: {e}", "ERROR")
        log(f"Traceback: {traceback.format_exc()}", "ERROR")
        return {"status": "unhealthy", "error": str(e)}

@app.get("/test/{item_id}")
def test_endpoint(item_id: int):
    log(f"GET /test/{item_id} - Test endpoint accessed", "REQUEST")
    
    try:
        log(f"Processing item_id: {item_id}", "DEBUG")
        
        if item_id < 0:
            log(f"Invalid item_id: {item_id}", "WARNING")
            raise ValueError(f"Item ID must be positive, got {item_id}")
        
        if item_id == 999:
            log("Simulating database error for item_id 999", "WARNING")
            raise Exception("Database connection failed (simulated)")
        
        response = {
            "item_id": item_id,
            "data": f"Test data for item {item_id}",
            "processed_at": str(datetime.now())
        }
        
        log(f"Test endpoint response: {response}", "DEBUG")
        return response
        
    except ValueError as ve:
        log(f"Validation error: {ve}", "ERROR")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        log(f"Unexpected error: {e}", "ERROR")
        log(f"Full traceback: {traceback.format_exc()}", "ERROR")
        raise HTTPException(status_code=500, detail="Internal server error")

# Middleware to log all requests
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.now()
    log(f"Incoming request: {request.method} {request.url.path}", "REQUEST")
    
    try:
        response = await call_next(request)
        duration = (datetime.now() - start_time).total_seconds()
        log(f"Request completed: {request.method} {request.url.path} - Status: {response.status_code} - Duration: {duration:.3f}s", "RESPONSE")
        return response
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        log(f"Request failed: {request.method} {request.url.path} - Error: {e} - Duration: {duration:.3f}s", "ERROR")
        raise

if __name__ == "__main__":
    import uvicorn
    log("Starting Uvicorn server...", "STARTUP")
    log("Server configuration: host=0.0.0.0, port=8890", "INFO")
    uvicorn.run(app, host="0.0.0.0", port=8890, log_level="info")