from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.routes import auth, admin, elections
from app.models.database import engine
from app.models.models import Base
import os

# Create FastAPI app FIRST
app = FastAPI(
    title="E-Voting API",
    description="A secure e-voting system with role-based access control",
    version="2.0.0"
)

# Enable CORS BEFORE anything else
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database tables created!")

# Create uploads directory structure
os.makedirs("uploads/profile_images", exist_ok=True)
os.makedirs("uploads/party_logos", exist_ok=True)
os.makedirs("uploads/candidate_images", exist_ok=True)

# Serve static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/admin", tags=["Administration"])
app.include_router(elections.router, prefix="/api", tags=["Elections & Voting"])

@app.get("/")
async def root():
    return {"message": "Welcome to E-Voting API", "status": "active"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))  # default local
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
