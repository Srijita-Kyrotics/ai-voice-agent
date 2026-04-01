import os
from dotenv import load_dotenv
from enum import Enum

load_dotenv()

class AgentState(Enum):
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    THINKING = "THINKING"
    SPEAKING = "SPEAKING"
    INTERRUPTED = "INTERRUPTED"
    ERROR = "ERROR"

class Settings:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Providers
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
    LOCAL_LLM_URL = os.getenv("LOCAL_LLM_URL", "http://localhost:11434/v1")
    
    # Models
    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
    TTS_MODEL = os.getenv("TTS_MODEL", "en_US-lessac-medium")
    
    # Audio Settings
    SAMPLE_RATE = 16000
    CHANNELS = 1
    SILENCE_THRESHOLD = 0.02
    MAX_SILENCE_DURATION = 1.8 
    
    # Storage
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    INPUT_AUDIO_DIR = os.path.join(BASE_DIR, "..", "data", "input_audio")
    OUTPUT_AUDIO_DIR = os.path.join(BASE_DIR, "..", "data", "output_audio")
    
    # Memory
    MAX_MEMORY_MESSAGES = 10

    @classmethod
    def ensure_dirs(cls):
        """Create necessary directories if they don't exist."""
        for d in [cls.INPUT_AUDIO_DIR, cls.OUTPUT_AUDIO_DIR]:
            os.makedirs(d, exist_ok=True)

settings = Settings()
