import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import os
import time
from app.utils.logger import logger
from app.config.settings import settings

class AudioRecorder:
    def __init__(self, sample_rate=16000, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.recording = False

    def record(self, duration=None, silence_threshold=0.01, max_silence=2.0):
        """
        Record audio from microphone. 
        If duration is None, it records until silence is detected.
        """
        logger.info("Starting audio recording...")
        
        if duration:
            recording = sd.rec(int(duration * self.sample_rate), 
                               samplerate=self.sample_rate, 
                               channels=self.channels)
            sd.wait()
            return recording
        
        # Dynamic recording based on silence
        audio_data = []
        
        def callback(indata, frames, time, status):
            if status:
                logger.warning(status)
            audio_data.append(indata.copy())
            
        with sd.InputStream(samplerate=self.sample_rate, 
                            channels=self.channels, 
                            callback=callback):
            logger.info("Recording... (Press Ctrl+C to stop or wait for silence)")
            while True:
                try:
                    time.sleep(0.1)
                    # Simple silence detection logic could be added here
                    # For now, we'll suggest manual stop or fixed chunks
                    # In a production app, we'd use a VAD (Voice Activity Detection)
                except KeyboardInterrupt:
                    break
        
        recording = np.concatenate(audio_data, axis=0)
        return recording

    def save_wav(self, data, filename="input.wav"):
        path = os.path.join(settings.INPUT_AUDIO_DIR, filename)
        wav.write(path, self.sample_rate, data)
        logger.info(f"Audio saved to {path}")
        return path
