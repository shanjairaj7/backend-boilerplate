"""
Auto-Discovery Route Registry
This file automatically discovers and registers all routes from the routes/ directory.

To add a new service:
1. Create a new .py file in routes/ directory (e.g., routes/my_service.py)
2. Define a router variable: router = APIRouter(prefix="/my-prefix", tags=["my-service"])
3. Add your endpoints to the router
4. That's it! The system will auto-discover and register it.

NO NEED TO MODIFY app.py OR THIS FILE!
"""
from fastapi import APIRouter
import os
import importlib
from datetime import datetime

def create_api_router():
    """Auto-discover and register all route modules"""
    main_router = APIRouter()
    
    print(f"[{datetime.now()}] 🔍 Auto-discovering routes...")
    
    # Get all Python files in routes directory
    routes_dir = os.path.dirname(__file__)
    route_files = [f[:-3] for f in os.listdir(routes_dir) 
                  if f.endswith('.py') and f != '__init__.py']
    
    registered_routes = []
    
    for route_file in route_files:
        try:
            # Import the route module
            module = importlib.import_module(f'routes.{route_file}')
            
            # Check if it has a router
            if hasattr(module, 'router'):
                main_router.include_router(module.router)
                registered_routes.append(route_file)
                print(f"[{datetime.now()}] ✅ Registered routes from: {route_file}.py")
            else:
                print(f"[{datetime.now()}] ⚠️ No 'router' found in: {route_file}.py")
                
        except Exception as e:
            print(f"[{datetime.now()}] ❌ Failed to load {route_file}.py: {e}")
    
    # Add API root endpoint
    @main_router.get("/", tags=["system"])
    def api_root():
        """API root showing all registered services"""
        return {
            "message": "Backend API - Auto-Discovery System",
            "version": "1.0.0",
            "registered_services": registered_routes,
            "endpoints": {
                service: f"/{service}/*" for service in registered_routes
            },
            "timestamp": str(datetime.now())
        }
    
    print(f"[{datetime.now()}] 🚀 Auto-discovery complete! Registered {len(registered_routes)} services")
    
    return main_router

# Create the main API router
api_router = create_api_router()