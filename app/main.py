from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routes import auth, admin  # Import admin routes
from app.models.database import engine
from app.models.models import Base

# Create database tables
print("🔧 Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Database tables created!")

# Create FastAPI app
app = FastAPI(
    title="E-Voting API",
    description="A secure e-voting system with role-based access control",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/admin", tags=["Administration"])

@app.get("/")
async def root():
    return {"message": "Welcome to E-Voting API", "status": "active"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)