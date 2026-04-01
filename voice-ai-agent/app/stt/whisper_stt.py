import whisper
import os
from app.utils.logger import logger
from app.config.settings import settings

class WhisperSTT:
    def __init__(self, model_name=None):
        model_name = model_name or settings.WHISPER_MODEL
        logger.info(f"Loading Whisper model: {model_name}")
        self.model = whisper.load_model(model_name)
        logger.info("Whisper model loaded successfully.")

    def transcribe(self, audio_path):
        """Transcribe an audio file into text."""
        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return ""
        
        try:
            logger.info(f"Transcribing: {audio_path}")
            result = self.model.transcribe(audio_path)
            text = result.get("text", "").strip()
            logger.info(f"Transcription result: {text}")
            return text
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
