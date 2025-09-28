"""
Video processing API endpoints
Handles YouTube video processing, transcription, and summarization
"""

import logging
import asyncio
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, Request
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session

from app.database.database import get_db, DatabaseService, JobStatus
from app.services.youtube_service import YouTubeService

logger = logging.getLogger(__name__)

router = APIRouter()


class ProcessVideoRequest(BaseModel):
    """Request model for video processing"""
    video_url: HttpUrl
    user_id: Optional[str] = None


class ProcessVideoResponse(BaseModel):
    """Response model for video processing request"""
    job_id: str
    status: str
    message: str
    estimated_time: Optional[int] = None


class JobStatusResponse(BaseModel):
    """Response model for job status"""
    job_id: str
    status: str
    progress: float
    current_step: Optional[str] = None
    error_message: Optional[str] = None
    created_at: str
    estimated_remaining: Optional[int] = None


class JobResultsResponse(BaseModel):
    """Response model for job results"""
    job_id: str
    status: str
    video_title: str
    video_url: str
    transcript: str
    summary: str
    processing_time: Optional[float] = None
    created_at: str
    completed_at: Optional[str] = None


@router.post("/process-video", response_model=ProcessVideoResponse)
async def process_video(
    request: ProcessVideoRequest,
    background_tasks: BackgroundTasks,
    app_request: Request,
    db: Session = Depends(get_db)
):
    """Process a YouTube video - extract audio, transcribe, and summarize"""
    try:
        video_url = str(request.video_url)
        logger.info(f"🎬 Processing video request: {video_url}")
        
        # Validate YouTube URL
        youtube_service = YouTubeService()
        if not youtube_service.validate_youtube_url(video_url):
            raise HTTPException(
                status_code=400,
                detail="Invalid YouTube URL"
            )
        
        # Get video metadata
        metadata = await youtube_service.get_video_metadata(video_url)
        if not metadata.get("is_valid"):
            raise HTTPException(
                status_code=400,
                detail=f"Failed to fetch video metadata: {metadata.get('error', 'Unknown error')}"
            )
        
        # Create processing job
        job = DatabaseService.create_job(
            video_url=video_url,
            video_title=metadata.get("title"),
            video_duration=metadata.get("duration"),
            user_id=request.user_id,
            db_session=db
        )
        
        # Start background processing
        background_tasks.add_task(
            process_video_background,
            job.id,
            video_url,
            app_request.app.state.model_manager
        )
        
        # Estimate processing time (rough estimate)
        duration = metadata.get("duration", 300)  # default 5 minutes
        estimated_time = max(60, duration // 10)  # at least 1 minute, roughly 1/10 of video length
        
        return ProcessVideoResponse(
            job_id=job.id,
            status=job.status,
            message="Video processing started",
            estimated_time=estimated_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Video processing request failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start video processing: {str(e)}"
        )


@router.get("/job-status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """Get the status of a processing job"""
    try:
        job = DatabaseService.get_job(job_id, db_session=db)
        
        if not job:
            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )
        
        # Calculate estimated remaining time
        estimated_remaining = None
        if job.status not in [JobStatus.COMPLETED, JobStatus.FAILED]:
            if job.video_duration and job.progress_percentage > 0:
                total_estimated = job.video_duration // 10  # rough estimate
                remaining = total_estimated * (1 - job.progress_percentage / 100)
                estimated_remaining = max(10, int(remaining))
        
        return JobStatusResponse(
            job_id=job.id,
            status=job.status,
            progress=job.progress_percentage,
            current_step=job.current_step,
            error_message=job.error_message,
            created_at=job.created_at.isoformat(),
            estimated_remaining=estimated_remaining
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get job status: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get job status"
        )


@router.get("/job-results/{job_id}", response_model=JobResultsResponse)
async def get_job_results(job_id: str, db: Session = Depends(get_db)):
    """Get the results of a completed processing job"""
    try:
        job = DatabaseService.get_job(job_id, db_session=db)
        
        if not job:
            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )
        
        if job.status != JobStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail=f"Job not completed. Current status: {job.status}"
            )
        
        return JobResultsResponse(
            job_id=job.id,
            status=job.status,
            video_title=job.video_title or "Unknown",
            video_url=job.video_url,
            transcript=job.transcript or "",
            summary=job.summary or "",
            processing_time=job.processing_time_seconds,
            created_at=job.created_at.isoformat(),
            completed_at=job.completed_at.isoformat() if job.completed_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get job results: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get job results"
        )


async def process_video_background(job_id: str, video_url: str, model_manager):
    """Background task for processing video"""
    youtube_service = YouTubeService()
    db = next(get_db())
    
    try:
        logger.info(f"🎬 Starting background processing for job: {job_id}")
        
        # Update job status to downloading
        DatabaseService.update_job_status(
            job_id, JobStatus.DOWNLOADING, 10, "Downloading audio...", db_session=db
        )
        
        # Download audio
        audio_path = await youtube_service.download_audio(video_url)
        
        # Update job status to transcribing
        DatabaseService.update_job_status(
            job_id, JobStatus.TRANSCRIBING, 40, "Transcribing audio...", db_session=db
        )
        
        # Transcribe audio
        transcription_result = await model_manager.transcribe_audio(audio_path)
        transcript = transcription_result["transcript"]
        
        # Update job status to summarizing
        DatabaseService.update_job_status(
            job_id, JobStatus.SUMMARIZING, 80, "Generating summary...", db_session=db
        )
        
        # Generate summary
        summary = await model_manager.process_text_to_bullet_summary(transcript)
        
        # Save results
        DatabaseService.save_results(
            job_id, transcript, summary, db_session=db
        )
        
        # Update final status
        DatabaseService.update_job_status(
            job_id, JobStatus.COMPLETED, 100, "Processing completed", db_session=db
        )
        
        # Cleanup temporary files
        youtube_service.cleanup_temp_files(audio_path)
        
        logger.info(f"✅ Background processing completed for job: {job_id}")
        
    except Exception as e:
        logger.error(f"❌ Background processing failed for job {job_id}: {e}")
        
        # Update job status to failed
        DatabaseService.update_job_status(
            job_id, JobStatus.FAILED, error_message=str(e), db_session=db
        )
        
        # Cleanup any temporary files
        try:
            youtube_service.cleanup_temp_files()
        except:
            pass
    
    finally:
        db.close()


@router.get("/jobs")
async def get_user_jobs(user_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Get jobs for a user (for dashboard)"""
    try:
        if not user_id:
            # Return empty list for anonymous users
            return []
        
        jobs = DatabaseService.get_user_jobs(user_id, db_session=db)
        
        return [
            {
                "id": job.id,
                "video_title": job.video_title,
                "video_url": job.video_url,
                "status": job.status,
                "created_at": job.created_at.isoformat(),
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "processing_time": job.processing_time_seconds
            }
            for job in jobs
        ]
        
    except Exception as e:
        logger.error(f"❌ Failed to get user jobs: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get user jobs"
        )

