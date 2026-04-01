import subprocess
import os
from app.utils.logger import logger
from app.config.settings import settings

class PiperTTS:
    """
    Wrapper for Piper TTS.
    Assumes piper binary and model file are available.
    """
    def __init__(self, model_name=None):
        self.model = model_name or settings.TTS_MODEL
        # Normal path structure: models/en_US-lessac-medium.onnx
        self.model_path = os.path.join(settings.BASE_DIR, "..", "models", f"{self.model}.onnx")
        self.config_path = f"{self.model_path}.json"

    def synthesize(self, text, output_filename="output.wav"):
        """Synthesize text into speech WAV file."""
        output_path = os.path.join(settings.OUTPUT_AUDIO_DIR, output_filename)
        logger.info(f"Synthesizing speech via Piper... Output: {output_path}")
        
        if not os.path.exists(self.model_path):
            logger.warning(f"Piper model not found at {self.model_path}. Falling back to mock synthesis.")
            return self._mock_synthesize(text, output_path)

        try:
            # Command: echo text | piper --model model.onnx --output_file output.wav
            cmd = ["echo", text, "|", "piper", "--model", self.model_path, "--output_file", output_path]
            # Since shell=True is needed for piping in some environments:
            cmd_str = f'echo "{text}" | piper --model {self.model_path} --output_file {output_path}'
            subprocess.run(cmd_str, shell=True, check=True)
            logger.info("Synthesis complete.")
            return output_path
        except Exception as e:
            logger.error(f"Piper TTS Error: {e}")
            return ""

    def _mock_synthesize(self, text, output_path):
        """Mock synthesis if model is not present."""
        logger.info("Mocked synthesis: (Sound of someone speaking...)")
        # In a real app, we'd handle the installation or use a library
        return ""
