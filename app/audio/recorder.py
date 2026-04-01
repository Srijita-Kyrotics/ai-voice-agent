import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import os
import time
from app.utils.logger import logger
from app.config.settings import settings

class AudioRecorder:
    def __init__(self):
        self.sample_rate = settings.SAMPLE_RATE
        self.channels = settings.CHANNELS
        self.recording = False

    def listen_and_record(self, threshold=None, max_silence=None):
        """
        Listen until speech is detected, then record until silence.
        Uses energy-based Voice Activity Detection (VAD).
        """
        threshold = threshold or settings.SILENCE_THRESHOLD
        max_silence = max_silence or settings.MAX_SILENCE_DURATION
        
        logger.info(f"LISTENING... (Threshold: {threshold})")
        
        audio_chunks = []
        silent_chunks = 0
        speech_detected = False
        
        # Simple energy detection callback
        def callback(indata, frames, time, status):
            nonlocal speech_detected, silent_chunks
            volume_norm = np.linalg.norm(indata) * 10 / frames
            
            if volume_norm > threshold:
                if not speech_detected:
                    logger.info("Speech detected!")
                    speech_detected = True
                silent_chunks = 0
                audio_chunks.append(indata.copy())
            elif speech_detected:
                silent_chunks += frames / self.sample_rate
                audio_chunks.append(indata.copy())
                if silent_chunks > max_silence:
                    raise sd.CallbackStop
        
        try:
            with sd.InputStream(samplerate=self.sample_rate, 
                                channels=self.channels, 
                                callback=callback):
                while True:
                    sd.sleep(100)
                    if not sd._initialized: break # Safety break
        except sd.CallbackStop:
            logger.info("Silence detected. Stopping recording.")
        except Exception as e:
            logger.error(f"Recording error: {e}")

        if not audio_chunks:
            return None
            
        return np.concatenate(audio_chunks, axis=0)

    def is_speech_ongoing(self, threshold=None, duration=0.5):
        """Check if there's ongoing speech (useful for interrupts)."""
        threshold = threshold or settings.SILENCE_THRESHOLD
        
        energy = []
        def callback(indata, frames, time, status):
            energy.append(np.linalg.norm(indata) * 10 / frames)

        try:
            with sd.InputStream(samplerate=self.sample_rate, 
                                channels=self.channels, 
                                callback=callback):
                sd.sleep(int(duration * 1000))
        except Exception:
            return False
            
        if not energy: return False
        return np.mean(energy) > threshold

    def save_wav(self, data, filename="input.wav"):
        if data is None or len(data) == 0:
            return None
        path = os.path.join(settings.INPUT_AUDIO_DIR, filename)
        wav.write(path, self.sample_rate, data)
        logger.info(f"Audio captured: {path}")
        return path
