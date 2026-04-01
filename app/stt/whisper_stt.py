import whisper
import os
import torch
from app.utils.logger import logger
from app.config.settings import settings

class WhisperSTT:
    def __init__(self, model_name=None):
        self.model_name = model_name or settings.WHISPER_MODEL
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading Whisper model '{self.model_name}' on {self.device}...")
        try:
            self.model = whisper.load_model(self.model_name, device=self.device)
            logger.info("Whisper model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            self.model = None

    def transcribe(self, audio_path):
        """Transcribe audio with auto-language detection."""
        if self.model is None:
            logger.error("Whisper model not initialized.")
            return ""
            
        if not os.path.exists(audio_path):
            return ""
        
        try:
            logger.info(f"TRANSCRIBING: {os.path.basename(audio_path)}")
            # Advanced Feature: Auto-detect language
            result = self.model.transcribe(audio_path, fp16=False if self.device=="cpu" else True)
            text = result.get("text", "").strip()
            language = result.get("language", "unknown")
            
            if text:
                logger.info(f"DETECTED LANGUAGE: {language}")
                logger.info(f"TRANSCRIPTION: {text}")
            return text
        except Exception as e:
            logger.error(f"STT Error: {e}")
            return ""
