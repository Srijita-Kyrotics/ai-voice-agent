import os
import time
import threading
from app.utils.logger import logger
from app.config.settings import settings, AgentState
from app.audio.recorder import AudioRecorder
from app.audio.player import AudioPlayer
from app.stt.whisper_stt import WhisperSTT
from app.llm.llm_client import LLMClient
from app.llm.prompt_manager import PromptManager
from app.tts.piper_tts import PiperTTS
from app.memory.conversation import ConversationMemory
from app.agents.base_agent import BaseAgent

class VoiceAgent(BaseAgent):
    def __init__(self):
        logger.info("--- INITIALIZING VOICE AGENT ---")
        settings.ensure_dirs()
        
        self.recorder = AudioRecorder()
        self.player = AudioPlayer()
        self.stt = WhisperSTT()
        self.llm = LLMClient()
        self.tts = PiperTTS()
        
        self.state = AgentState.IDLE
        self.memory = ConversationMemory(
            system_prompt=PromptManager.get_voice_assistant_prompt()
        )
        self._lock = threading.Lock()

    def transition_to(self, new_state):
        with self._lock:
            if self.state != new_state:
                self.state = new_state
                logger.info(f"State Transition: {new_state}")

    def record(self):
        """Record audio from the microphone."""
        self.transition_to(AgentState.LISTENING)
        audio_data = self.recorder.listen_and_record()
        if audio_data:
            return self.recorder.save_wav(audio_data)
        return None

    def transcribe(self, audio_path):
        """Transcribe audio to text."""
        user_text = self.stt.transcribe(audio_path)
        return user_text

    def is_valid_input(self, text):
        """Check if the transcribed text is valid for processing."""
        if not text or len(text.split()) < 2:
            return False
        return True

    def decide(self, text):
        """Decide whether to act on the text or ignore it."""
        text_lower = text.lower()
        # Basic academic intent detection
        academic_keywords = ["what", "how", "explain", "physics", "math", "science", "history", "kya", "kaise"]
        if any(word in text_lower for word in academic_keywords):
            return "process"
        return "process" # For now, process everything if not empty

    def generate_response(self, text):
        """Generate a response based on the text."""
        self.transition_to(AgentState.THINKING)
        
        # Temp add to memory for context generation
        self.memory.add_message("user", text)
        context = self.memory.get_context()
        
        ai_text = self.llm.generate_response(context)
        
        # Ensure brevity
        if len(ai_text.split()) > 45:
            ai_text = " ".join(ai_text.split()[:45]) + "."
            
        return ai_text

    def speak(self, response):
        """Convert response text to speech and play it."""
        self.transition_to(AgentState.SPEAKING)
        wav_path = self.tts.synthesize(response)
        
        if wav_path:
            play_thread = threading.Thread(target=self.player.play, args=(wav_path,))
            play_thread.start()
            
            # Handle interruption during playback
            while play_thread.is_alive():
                if self.recorder.is_speech_ongoing(duration=0.15):
                    logger.info("INTERRUPT: User spoke again.")
                    self.player.stop()
                    self.transition_to(AgentState.INTERRUPTED)
                    break
                time.sleep(0.05)
            play_thread.join()

    def update_memory(self, text, response):
        """Update the conversation memory with the interaction."""
        # User message was added in generate_response for context. 
        # Now add assistant message.
        self.memory.add_message("assistant", response)
        self.transition_to(AgentState.IDLE)
