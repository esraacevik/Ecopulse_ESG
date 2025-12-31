"""
FastAPI Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir.parent))

# Add modeller path for ML routes
modeller_dir = backend_dir.parent / "modeller"
sys.path.insert(0, str(modeller_dir))

from app.config import settings
from app.api.v1 import emission, report, ai, activity, upload, analyzer

# ML Routes (try import, may fail if dependencies missing)
try:
    # Ensure modeller path is in sys.path
    if str(modeller_dir) not in sys.path:
        sys.path.insert(0, str(modeller_dir))
    
    from api.ml_routes import router as ml_router
    ML_AVAILABLE = True
    print(f"[INFO] ML routes loaded successfully. Available endpoints: {len([r for r in ml_router.routes if hasattr(r, 'path')])}")
except ImportError as e:
    import traceback
    print(f"[ERROR] ML routes not available: {e}")
    traceback.print_exc()
    ML_AVAILABLE = False
except Exception as e:
    import traceback
    print(f"[ERROR] ML routes initialization failed: {e}")
    traceback.print_exc()
    ML_AVAILABLE = False

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(emission.router, prefix="/api/v1", tags=["Emission"])
app.include_router(report.router, prefix="/api/v1", tags=["Report"])
app.include_router(ai.router, prefix="/api/v1", tags=["AI"])
app.include_router(activity.router, prefix="/api/v1", tags=["Activity"])
app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])
app.include_router(analyzer.router, prefix="/api/v1", tags=["Analyzer"])

# ML Router (if available)
if ML_AVAILABLE:
    app.include_router(ml_router, prefix="/api/v1", tags=["Machine Learning"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ECOLOGIA API",
        "version": settings.API_VERSION,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "climatiq": bool(settings.CLIMATIQ_API_KEY),
            "gemini": bool(settings.GEMINI_API_KEY),
            "huggingface": bool(settings.HUGGINGFACE_API_KEY),
            "esg_analyzer": True,
            "ocr": True,
            "ml_models": ML_AVAILABLE
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

