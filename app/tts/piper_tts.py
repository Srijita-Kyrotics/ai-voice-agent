import subprocess
import os
import shutil
from app.utils.logger import logger
from app.config.settings import settings

class PiperTTS:
    def __init__(self, model_name=None):
        self.model = model_name or settings.TTS_MODEL
        # Adjust path to the root models directory
        self.model_path = os.path.join(os.getcwd(), "models", f"{self.model}.onnx")
        
    def synthesize(self, text, output_filename="response.wav"):
        """Synthesize text to speech using Piper (Offline)."""
        output_path = os.path.join(settings.OUTPUT_AUDIO_DIR, output_filename)
        
        # Check if piper is in PATH
        if not shutil.which("piper"):
            logger.warning("Piper binary not found in PATH. Please install piper or add to PATH.")
            return None

        if not os.path.exists(self.model_path):
            logger.error(f"Piper model not found at: {self.model_path}")
            return None

        try:
            logger.info(f"SYNTHESIZING: '{text[:50]}...'")
            
            # Using piper via shell pipe for low latency
            # Format: echo 'text' | piper --model model.onnx --output_file output.wav
            escaped_text = text.replace('"', '\\"').replace('\n', ' ')
            command = f'echo "{escaped_text}" | piper --model "{self.model_path}" --output_file "{output_path}"'
            
            subprocess.run(command, shell=True, check=True, stderr=subprocess.PIPE)
            return output_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Piper synthesis failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected TTS error: {e}")
            return None
