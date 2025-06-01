"""
FastAPI Backend for Romanian Public Administration Platform
Main application entry point with database initialization and route registration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import logging

from app.core.config import settings
from app.db.database import create_tables, check_database_connection, get_db
from app.db.init_data import initialize_default_data
from app.api.routes import auth, users, documents, archive, dashboard, ai, parking, settings as settings_routes, search, auto_archive, personal_documents

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events: startup and shutdown
    """
    # Startup
    logger.info("🚀 Starting Romanian Admin Platform Backend...")
    
    # Create database tables (with error handling)
    try:
        await create_tables()
        
        # Check if database is actually accessible
        if await check_database_connection():
            logger.info("✅ Database connection successful")
            
            # Initialize default data (categories, etc.)
            try:
                async for db in get_db():
                    await initialize_default_data(db)
                    break  # Only need one session
                logger.info("✅ Default data initialized")
            except Exception as e:
                logger.warning(f"⚠️  Default data initialization failed: {e}")
                
        else:
            logger.warning("⚠️  Database connection failed - API will run without database")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        if settings.ENVIRONMENT == "development":
            logger.warning("🔧 Running in development mode without database")
        else:
            raise e
    
    # Create upload directory if it doesn't exist
    try:
        os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)
        # Create auto-archive subdirectories
        os.makedirs(os.path.join(settings.UPLOAD_DIRECTORY, "scans"), exist_ok=True)
        os.makedirs(os.path.join(settings.UPLOAD_DIRECTORY, "archive"), exist_ok=True)
        logger.info(f"✅ Upload directory ready: {settings.UPLOAD_DIRECTORY}")
    except Exception as e:
        logger.error(f"Failed to create upload directory: {e}")
    
    logger.info("🎯 Backend startup complete - API is ready!")
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down backend...")


# Create FastAPI app with metadata
app = FastAPI(
    title="Romanian Public Administration API",
    description="Backend API for Romanian public administration document management platform with AI-powered auto-archive",
    version="1.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# Mount static files directory (with error handling)
try:
    app.mount("/static", StaticFiles(directory=settings.UPLOAD_DIRECTORY), name="static")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")

# Include API routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(archive.router, prefix="/api/archive", tags=["Archive"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI Agent"])
app.include_router(parking.router, prefix="/api/parking", tags=["Parking"])
app.include_router(settings_routes.router, prefix="/api/settings", tags=["Settings"])
app.include_router(search.router, prefix="/api/search", tags=["Advanced Search"])
app.include_router(auto_archive.router, prefix="/api/auto-archive", tags=["Auto Archive & OCR"])
app.include_router(personal_documents.router, prefix="/api/personal-documents", tags=["Personal Documents"])


@app.get("/")
async def root():
    """
    Root endpoint for health check
    """
    return {
        "message": "Romanian Public Administration API with Auto-Archive",
        "version": "1.1.0",
        "status": "online",
        "environment": settings.ENVIRONMENT,
        "features": {
            "database": True,
            "file_uploads": True,
            "ai_agent": True,
            "auto_archive": True,
            "ocr_processing": True
        }
    }


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint with database status
    """
    db_status = "connected"
    try:
        if await check_database_connection():
            db_status = "connected"
        else:
            db_status = "disconnected"
    except Exception:
        db_status = "error"
    
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "version": "1.1.0",
        "features": {
            "auto_archive": True,
            "ocr_processing": True
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    ) 