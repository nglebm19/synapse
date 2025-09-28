"""
Database configuration and models for video processing jobs and results
Using SQLite for local development with option to switch to PostgreSQL/Supabase
"""

import os
import logging
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./synapse.db")

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class JobStatus(str, Enum):
    """Job processing status"""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    TRANSCRIBING = "transcribing"
    SUMMARIZING = "summarizing"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoProcessingJob(Base):
    """Video processing job model"""
    __tablename__ = "video_processing_jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=True)  # Optional user association
    
    # Video information
    video_url = Column(String, nullable=False)
    video_title = Column(String)
    video_duration = Column(Integer)  # in seconds
    video_uploader = Column(String)
    
    # Processing status
    status = Column(String, default=JobStatus.PENDING)
    progress_percentage = Column(Float, default=0.0)
    current_step = Column(String)
    error_message = Column(Text)
    
    # Results
    transcript = Column(Text)
    summary = Column(Text)
    
    # Model information
    whisper_model = Column(String)
    summarization_model = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Processing metrics
    processing_time_seconds = Column(Float)
    transcript_length = Column(Integer)
    summary_length = Column(Integer)


class UserSession(Base):
    """User session for tracking anonymous users"""
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_token = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    job_count = Column(Integer, default=0)


async def create_tables():
    """Create database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        raise


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseService:
    """Database service for video processing operations"""
    
    @staticmethod
    def create_job(
        video_url: str,
        video_title: str = None,
        video_duration: int = None,
        user_id: str = None,
        db_session=None
    ) -> VideoProcessingJob:
        """Create a new video processing job"""
        
        job = VideoProcessingJob(
            video_url=video_url,
            video_title=video_title,
            video_duration=video_duration,
            user_id=user_id,
            whisper_model=os.getenv("WHISPER_MODEL", "openai/whisper-small"),
            summarization_model=os.getenv("SUMMARIZATION_MODEL", "sshleifer/distilbart-cnn-12-6")
        )
        
        if db_session:
            db_session.add(job)
            db_session.commit()
            db_session.refresh(job)
        
        return job
    
    @staticmethod
    def update_job_status(
        job_id: str,
        status: JobStatus,
        progress: float = None,
        current_step: str = None,
        error_message: str = None,
        db_session=None
    ) -> Optional[VideoProcessingJob]:
        """Update job status"""
        
        if not db_session:
            return None
            
        job = db_session.query(VideoProcessingJob).filter(
            VideoProcessingJob.id == job_id
        ).first()
        
        if job:
            job.status = status
            if progress is not None:
                job.progress_percentage = progress
            if current_step:
                job.current_step = current_step
            if error_message:
                job.error_message = error_message
            
            # Update timestamps
            if status == JobStatus.PENDING and not job.started_at:
                job.started_at = datetime.utcnow()
            elif status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                job.completed_at = datetime.utcnow()
                if job.started_at:
                    job.processing_time_seconds = (
                        job.completed_at - job.started_at
                    ).total_seconds()
            
            db_session.commit()
            db_session.refresh(job)
        
        return job
    
    @staticmethod
    def save_results(
        job_id: str,
        transcript: str,
        summary: str,
        db_session=None
    ) -> Optional[VideoProcessingJob]:
        """Save processing results"""
        
        if not db_session:
            return None
            
        job = db_session.query(VideoProcessingJob).filter(
            VideoProcessingJob.id == job_id
        ).first()
        
        if job:
            job.transcript = transcript
            job.summary = summary
            job.transcript_length = len(transcript)
            job.summary_length = len(summary)
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            
            if job.started_at:
                job.processing_time_seconds = (
                    job.completed_at - job.started_at
                ).total_seconds()
            
            db_session.commit()
            db_session.refresh(job)
        
        return job
    
    @staticmethod
    def get_job(job_id: str, db_session=None) -> Optional[VideoProcessingJob]:
        """Get job by ID"""
        
        if not db_session:
            return None
            
        return db_session.query(VideoProcessingJob).filter(
            VideoProcessingJob.id == job_id
        ).first()
    
    @staticmethod
    def get_user_jobs(user_id: str, limit: int = 50, db_session=None):
        """Get jobs for a specific user"""
        
        if not db_session:
            return []
            
        return db_session.query(VideoProcessingJob).filter(
            VideoProcessingJob.user_id == user_id
        ).order_by(VideoProcessingJob.created_at.desc()).limit(limit).all()

