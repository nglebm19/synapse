"""
YouTube Service - Handles YouTube video processing and audio extraction
Uses yt-dlp for reliable video downloading and ffmpeg for audio conversion
"""

import os
import logging
import asyncio
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
import yt_dlp
import ffmpeg

logger = logging.getLogger(__name__)


class YouTubeService:
    """Service for YouTube video processing and audio extraction"""
    
    def __init__(self):
        self.temp_dir = Path(os.getenv("TEMP_DIR", "./temp"))
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.max_video_length = int(os.getenv("MAX_VIDEO_LENGTH", 3600))  # 1 hour
        
    async def extract_video_info(self, url: str) -> Dict[str, Any]:
        """Extract video information without downloading"""
        try:
            logger.info(f"🔍 Extracting video info for: {url}")
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            loop = asyncio.get_event_loop()
            
            def get_info():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(url, download=False)
            
            info = await loop.run_in_executor(None, get_info)
            
            # Validate video length
            duration = info.get('duration', 0)
            if duration > self.max_video_length:
                raise ValueError(f"Video too long: {duration}s (max: {self.max_video_length}s)")
            
            video_info = {
                'title': info.get('title', 'Unknown'),
                'duration': duration,
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'upload_date': info.get('upload_date'),
                'description': info.get('description', ''),
                'url': url
            }
            
            logger.info(f"✅ Video info extracted: {video_info['title']} ({duration}s)")
            return video_info
            
        except Exception as e:
            logger.error(f"❌ Failed to extract video info: {e}")
            raise
    
    async def download_audio(self, url: str) -> str:
        """Download and extract audio from YouTube video"""
        try:
            logger.info(f"📥 Downloading audio from: {url}")
            
            # Create temporary file for audio
            temp_audio_file = self.temp_dir / f"audio_{os.urandom(8).hex()}.wav"
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(self.temp_dir / f"video_{os.urandom(8).hex()}.%(ext)s"),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '192',
                }],
                'postprocessor_args': [
                    '-ar', '16000',  # 16kHz sample rate for Whisper
                    '-ac', '1',      # Mono audio
                ],
                'quiet': True,
                'no_warnings': True,
            }
            
            loop = asyncio.get_event_loop()
            
            def download():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url)
                    # Find the downloaded audio file
                    for file in self.temp_dir.glob("*.wav"):
                        if file.stat().st_mtime > (asyncio.get_event_loop().time() - 60):
                            return str(file)
                    raise FileNotFoundError("Downloaded audio file not found")
            
            audio_path = await loop.run_in_executor(None, download)
            
            logger.info(f"✅ Audio downloaded: {audio_path}")
            return audio_path
            
        except Exception as e:
            logger.error(f"❌ Audio download failed: {e}")
            raise
    
    async def convert_audio_for_whisper(self, input_path: str) -> str:
        """Convert audio to optimal format for Whisper (16kHz, mono, WAV)"""
        try:
            logger.info(f"🔄 Converting audio for Whisper: {input_path}")
            
            output_path = str(self.temp_dir / f"whisper_{os.urandom(8).hex()}.wav")
            
            loop = asyncio.get_event_loop()
            
            def convert():
                (
                    ffmpeg
                    .input(input_path)
                    .output(
                        output_path,
                        acodec='pcm_s16le',
                        ac=1,  # mono
                        ar=16000,  # 16kHz
                        f='wav'
                    )
                    .overwrite_output()
                    .run(quiet=True)
                )
                return output_path
            
            result_path = await loop.run_in_executor(None, convert)
            
            logger.info(f"✅ Audio converted: {result_path}")
            return result_path
            
        except Exception as e:
            logger.error(f"❌ Audio conversion failed: {e}")
            raise
    
    def cleanup_temp_files(self, *file_paths: str):
        """Clean up temporary files"""
        for file_path in file_paths:
            try:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"🧹 Cleaned up: {file_path}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to cleanup {file_path}: {e}")
    
    def validate_youtube_url(self, url: str) -> bool:
        """Validate if URL is a valid YouTube URL"""
        youtube_patterns = [
            'youtube.com/watch',
            'youtu.be/',
            'youtube.com/embed',
            'youtube.com/v/'
        ]
        return any(pattern in url.lower() for pattern in youtube_patterns)
    
    async def get_video_metadata(self, url: str) -> Dict[str, Any]:
        """Get comprehensive video metadata"""
        try:
            info = await self.extract_video_info(url)
            
            return {
                'title': info['title'],
                'duration': info['duration'],
                'duration_formatted': self._format_duration(info['duration']),
                'uploader': info['uploader'],
                'view_count': info.get('view_count', 0),
                'upload_date': info.get('upload_date'),
                'thumbnail': info.get('thumbnail'),
                'description': info.get('description', '')[:500],  # Truncate description
                'url': url,
                'is_valid': True
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get video metadata: {e}")
            return {
                'url': url,
                'is_valid': False,
                'error': str(e)
            }
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration in seconds to human-readable format"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

