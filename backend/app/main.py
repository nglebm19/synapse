"""
Synapse Backend - FastAPI application for AI-powered video lecture processing
Optimized for Apple M1 Pro with self-hosted models
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from app.models.model_manager import ModelManager
from app.api import video_processing, health
from app.database.database import create_tables

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global model manager instance
model_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - handles startup and shutdown"""
    global model_manager
    
    # Startup
    logger.info("🚀 Starting Synapse Backend...")
    
    # Create database tables
    await create_tables()
    logger.info("📊 Database tables created")
    
    # Initialize model manager
    model_manager = ModelManager()
    await model_manager.initialize()
    logger.info("🤖 AI models loaded successfully")
    
    # Store model manager in app state
    app.state.model_manager = model_manager
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Synapse Backend...")
    if model_manager:
        await model_manager.cleanup()


# Create FastAPI application
app = FastAPI(
    title="Synapse Backend",
    description="AI-Powered Video Lecture Processing API",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(video_processing.router, prefix="/api", tags=["video-processing"])


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Synapse Backend API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

