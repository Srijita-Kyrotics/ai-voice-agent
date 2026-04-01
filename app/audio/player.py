import sounddevice as sd
import soundfile as sf
import os
import threading
from app.utils.logger import logger

class AudioPlayer:
    def __init__(self):
        self._is_speaking = False
        self._stop_event = threading.Event()

    @property
    def is_speaking(self):
        return self._is_speaking

    def play(self, file_path):
        """Play audio file (blocking but interruptible via stop())."""
        if not os.path.exists(file_path):
            logger.error(f"Audio playback failed: File {file_path} not found.")
            return
        
        try:
            self._is_speaking = True
            logger.info(f"SPEAKING (Audio: {os.path.basename(file_path)})")
            
            data, fs = sf.read(file_path, dtype='float32')
            sd.play(data, fs)
            sd.wait()
            
        except Exception as e:
            logger.error(f"Playback error: {e}")
        finally:
            self._is_speaking = False

    def stop(self):
        """Stop playback immediately."""
        if self._is_speaking:
            sd.stop()
            self._is_speaking = False
            logger.info("Playback INTERRUPTED.")
