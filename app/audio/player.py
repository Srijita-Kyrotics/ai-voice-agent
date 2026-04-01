import sounddevice as sd
import soundfile as sf
import os
from app.utils.logger import logger

class AudioPlayer:
    def __init__(self):
        pass

    def play(self, file_path):
        """Play an audio file using sounddevice."""
        if not os.path.exists(file_path):
            logger.error(f"Audio file not found: {file_path}")
            return
        
        try:
            logger.info(f"Playing audio: {file_path}")
            data, fs = sf.read(file_path, dtype='float32')
            sd.play(data, fs)
            sd.wait()
            logger.info("Playback finished.")
        except Exception as e:
            logger.error(f"Error playing audio: {e}")

    def stop(self):
        """Stop any ongoing playback."""
        sd.stop()
        logger.info("Playback stopped.")
