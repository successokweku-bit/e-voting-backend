from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.routes import auth, admin, elections
from app.models.database import engine
from app.models.models import Base
import os

# Custom middleware to force CORS headers on ALL responses
class ForceCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Handle preflight OPTIONS requests
        if request.method == "OPTIONS":
            return JSONResponse(
                content={},
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Credentials": "true",
                }
            )
        
        # Process the request
        try:
            response = await call_next(request)
        except Exception as e:
            # Handle any errors and ensure CORS headers
            return JSONResponse(
                content={"detail": str(e)},
                status_code=500,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*",
                }
            )
        
        # Add CORS headers to every response
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "*"
        
        return response

# Create FastAPI app
app = FastAPI(
    title="E-Voting API",
    description="A secure e-voting system with role-based access control",
    version="2.0.0"
)

# Add custom CORS middleware FIRST (this is critical!)
app.add_middleware(ForceCORSMiddleware)

# Add standard CORS middleware as backup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Create database tables
print("Creating database tables...")
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
except Exception as e:
    print(f"Error creating database tables: {e}")

# Create uploads directory structure
try:
    os.makedirs("uploads/profile_images", exist_ok=True)
    os.makedirs("uploads/party_logos", exist_ok=True)
    os.makedirs("uploads/candidate_images", exist_ok=True)
    print("Upload directories created successfully!")
except Exception as e:
    print(f"Error creating upload directories: {e}")

# Serve static files
try:
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
    print("Static files mounted successfully!")
except Exception as e:
    print(f"Error mounting static files: {e}")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/admin", tags=["Administration"])
app.include_router(elections.router, prefix="/api", tags=["Elections & Voting"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to E-Voting API",
        "status": "active",
        "version": "2.0.0",
        "cors": "enabled"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint with CORS verification"""
    return {
        "status": "healthy",
        "cors_enabled": True,
        "cors_policy": "allow_all",
        "server": "running"
    }

@app.get("/test-cors")
async def test_cors():
    """Dedicated CORS test endpoint"""
    return {
        "message": "If you can see this, CORS is working!",
        "timestamp": "2025-11-29",
        "cors": "success"
    }

# Global exception handler to ensure CORS headers on errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Ensure CORS headers are present even on errors"""
    print(f"Global exception handler caught: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    print(f"Starting server on port {port}...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
