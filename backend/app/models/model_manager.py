"""
Model Manager - Handles loading and managing AI models optimized for M1 Pro
- Whisper for speech-to-text
- DistilBART for summarization
"""

import os
import re
import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
import torch
from transformers import (
    WhisperProcessor, WhisperForConditionalGeneration,
    BartTokenizer, BartForConditionalGeneration,
    pipeline
)
import whisper

logger = logging.getLogger(__name__)

# Target length (in tokens) for each partial summary in the map-reduce pass
CHUNK_SUMMARY_LENGTH = 150


class ModelManager:
    """Manages AI models with optimizations for Apple M1 Pro"""
    
    def __init__(self):
        self.whisper_model = None
        self.whisper_processor = None
        self.summarization_pipeline = None
        self.device = self._get_optimal_device()
        self.model_cache_dir = os.getenv("MODEL_CACHE_DIR", "./models")
        
        # Create model cache directory
        Path(self.model_cache_dir).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🔧 Model Manager initialized with device: {self.device}")
    
    def _get_optimal_device(self) -> str:
        """Determine the best device for M1 Pro"""
        if torch.backends.mps.is_available():
            return "mps"  # Metal Performance Shaders for M1/M2
        elif torch.cuda.is_available():
            return "cuda"
        else:
            return "cpu"
    
    async def initialize(self):
        """Initialize all models asynchronously"""
        logger.info("🤖 Loading AI models...")
        
        # Load models in parallel for faster startup
        await asyncio.gather(
            self._load_whisper_model(),
            self._load_summarization_model()
        )
        
        logger.info("✅ All models loaded successfully")
    
    async def _load_whisper_model(self):
        """Load Whisper model for speech-to-text"""
        try:
            model_name = os.getenv("WHISPER_MODEL", "openai/whisper-small")
            
            logger.info(f"📥 Loading Whisper model: {model_name}")
            
            # Use the original whisper package for better M1 optimization
            loop = asyncio.get_event_loop()
            self.whisper_model = await loop.run_in_executor(
                None, whisper.load_model, "small"
            )
            
            logger.info("✅ Whisper model loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to load Whisper model: {e}")
            raise
    
    async def _load_summarization_model(self):
        """Load summarization model"""
        try:
            model_name = os.getenv("SUMMARIZATION_MODEL", "sshleifer/distilbart-cnn-12-6")
            
            logger.info(f"📥 Loading summarization model: {model_name}")
            
            loop = asyncio.get_event_loop()
            self.summarization_pipeline = await loop.run_in_executor(
                None,
                lambda: pipeline(
                    "summarization",
                    model=model_name,
                    tokenizer=model_name,
                    device=0 if self.device == "mps" else -1,  # Use GPU if available
                    torch_dtype=torch.float16 if self.device != "cpu" else torch.float32
                )
            )
            
            logger.info("✅ Summarization model loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to load summarization model: {e}")
            raise
    
    async def transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """Transcribe audio using Whisper"""
        try:
            if not self.whisper_model:
                raise RuntimeError("Whisper model not loaded")
            
            logger.info(f"🎤 Transcribing audio: {audio_path}")
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.whisper_model.transcribe(
                    audio_path,
                    fp16=False,  # Use fp32 for better compatibility
                    language="en"  # Can be made configurable
                )
            )
            
            transcript = result["text"].strip()
            logger.info(f"✅ Transcription completed: {len(transcript)} characters")
            
            return {
                "transcript": transcript,
                "language": result.get("language", "en"),
                "segments": result.get("segments", [])
            }
            
        except Exception as e:
            logger.error(f"❌ Transcription failed: {e}")
            raise
    
    async def generate_summary(self, text: str, max_length: int = 150) -> str:
        """Generate summary using DistilBART, covering the whole text"""
        try:
            if not self.summarization_pipeline:
                raise RuntimeError("Summarization model not loaded")

            logger.info(f"📝 Generating summary for text: {len(text)} characters")

            if not text.strip():
                return ""

            loop = asyncio.get_event_loop()
            summary = await loop.run_in_executor(
                None, self._summarize_long_text, text, max_length
            )

            logger.info(f"✅ Summary generated: {len(summary)} characters")

            return summary

        except Exception as e:
            logger.error(f"❌ Summary generation failed: {e}")
            raise

    def _summarize_long_text(self, text: str, max_length: int) -> str:
        """Map-reduce summary: summarize each chunk, then summarize the summaries
        until they fit in one model input"""
        tokenizer = self.summarization_pipeline.tokenizer
        # Leave room for special tokens; some tokenizers report a huge sentinel value
        max_tokens = min(tokenizer.model_max_length, 1024) - 24

        chunks = self._split_into_chunks(text, max_tokens)
        round_number = 0
        while len(chunks) > 1:
            round_number += 1
            logger.info(f"📝 Summary round {round_number}: {len(chunks)} chunks")
            partial_summaries = [
                self._summarize_chunk(chunk, CHUNK_SUMMARY_LENGTH) for chunk in chunks
            ]
            next_chunks = self._split_into_chunks(" ".join(partial_summaries), max_tokens)
            if len(next_chunks) >= len(chunks):
                # Summaries are not getting shorter; stop instead of looping forever
                logger.warning("⚠️ Summaries did not shrink; using first chunk only")
                next_chunks = next_chunks[:1]
            chunks = next_chunks

        return self._summarize_chunk(chunks[0], max_length)

    def _split_into_chunks(self, text: str, max_tokens: int) -> List[str]:
        """Split text into chunks of at most max_tokens, on sentence boundaries
        where possible"""
        tokenizer = self.summarization_pipeline.tokenizer
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())

        chunks: List[str] = []
        current: List[str] = []
        current_tokens = 0

        for sentence in sentences:
            token_ids = tokenizer.encode(sentence, add_special_tokens=False)

            # A single sentence can exceed the limit (Whisper sometimes emits
            # long runs without punctuation), so cut it by tokens
            if len(token_ids) > max_tokens:
                if current:
                    chunks.append(" ".join(current))
                    current, current_tokens = [], 0
                for start in range(0, len(token_ids), max_tokens):
                    chunks.append(tokenizer.decode(token_ids[start:start + max_tokens]))
                continue

            if current_tokens + len(token_ids) > max_tokens:
                chunks.append(" ".join(current))
                current, current_tokens = [], 0

            current.append(sentence)
            current_tokens += len(token_ids)

        if current:
            chunks.append(" ".join(current))

        return chunks

    def _summarize_chunk(self, text: str, max_length: int) -> str:
        """Summarize one chunk that fits in the model input"""
        input_tokens = len(self.summarization_pipeline.tokenizer.encode(text))
        # Short inputs need a short target, or the model pads with repetition
        target_max = max(16, min(max_length, input_tokens // 2))
        target_min = min(50, target_max // 2)

        result = self.summarization_pipeline(
            text,
            max_length=target_max,
            min_length=target_min,
            do_sample=False,
            truncation=True
        )
        return result[0]["summary_text"].strip()
    
    async def process_text_to_bullet_summary(self, transcript: str) -> str:
        """Convert transcript to bullet-point summary"""
        try:
            # First get the base summary
            base_summary = await self.generate_summary(transcript, max_length=200)
            
            # Format as bullet points (simple approach for now)
            sentences = base_summary.split('. ')
            bullet_points = []
            
            for sentence in sentences:
                if sentence.strip():
                    # Clean up the sentence
                    clean_sentence = sentence.strip().rstrip('.')
                    if clean_sentence:
                        bullet_points.append(f"• {clean_sentence}")
            
            formatted_summary = "\n".join(bullet_points)
            
            # Add a header
            final_summary = "**Key Points from the Lecture:**\n\n" + formatted_summary
            
            return final_summary
            
        except Exception as e:
            logger.error(f"❌ Bullet summary generation failed: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup models and free memory"""
        logger.info("🧹 Cleaning up models...")
        
        self.whisper_model = None
        self.whisper_processor = None
        self.summarization_pipeline = None
        
        # Force garbage collection
        import gc
        gc.collect()
        
        if self.device == "mps":
            torch.mps.empty_cache()
        elif self.device == "cuda":
            torch.cuda.empty_cache()
        
        logger.info("✅ Model cleanup completed")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        return {
            "device": self.device,
            "whisper_loaded": self.whisper_model is not None,
            "summarization_loaded": self.summarization_pipeline is not None,
            "cache_dir": self.model_cache_dir
        }

