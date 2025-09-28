"""
Health check endpoints for monitoring API status and model availability
"""

import logging
from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Dict, Any

logger = logging.getLogger(__name__)

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    message: str
    models: Dict[str, Any]
    system_info: Dict[str, Any]


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """Basic health check endpoint"""
    try:
        # Get model manager from app state
        model_manager = getattr(request.app.state, 'model_manager', None)
        
        if not model_manager:
            return HealthResponse(
                status="unhealthy",
                message="Model manager not available",
                models={},
                system_info={}
            )
        
        model_info = model_manager.get_model_info()
        
        # Check if models are loaded
        models_healthy = (
            model_info.get("whisper_loaded", False) and
            model_info.get("summarization_loaded", False)
        )
        
        status = "healthy" if models_healthy else "degraded"
        message = "All systems operational" if models_healthy else "Some models not loaded"
        
        return HealthResponse(
            status=status,
            message=message,
            models=model_info,
            system_info={
                "device": model_info.get("device", "unknown"),
                "cache_dir": model_info.get("cache_dir", "unknown")
            }
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            message=f"Health check failed: {str(e)}",
            models={},
            system_info={}
        )


@router.get("/health/models")
async def models_health(request: Request):
    """Detailed model health check"""
    try:
        model_manager = getattr(request.app.state, 'model_manager', None)
        
        if not model_manager:
            return {"error": "Model manager not available"}
        
        return model_manager.get_model_info()
        
    except Exception as e:
        logger.error(f"Model health check failed: {e}")
        return {"error": str(e)}


@router.get("/health/ready")
async def readiness_check(request: Request):
    """Readiness probe for deployment"""
    try:
        model_manager = getattr(request.app.state, 'model_manager', None)
        
        if not model_manager:
            return {"ready": False, "reason": "Model manager not available"}
        
        model_info = model_manager.get_model_info()
        
        ready = (
            model_info.get("whisper_loaded", False) and
            model_info.get("summarization_loaded", False)
        )
        
        return {
            "ready": ready,
            "reason": "All models loaded" if ready else "Models not fully loaded"
        }
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"ready": False, "reason": str(e)}

