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

class VoiceAgent:
    def __init__(self):
        logger.info("--- INITIALIZING INTELLIGENT VOICE AGENT ---")
        settings.ensure_dirs()
        
        # Core Components
        self.recorder = AudioRecorder()
        self.player = AudioPlayer()
        self.stt = WhisperSTT()
        self.llm = LLMClient()
        self.tts = PiperTTS()
        
        # State & Memory
        self.state = AgentState.IDLE
        self.memory = ConversationMemory(
            system_prompt=PromptManager.get_voice_assistant_prompt()
        )
        
        self.running = False
        self._lock = threading.Lock()

    def transition_to(self, new_state):
        """Utility to safely change agent state."""
        with self._lock:
            if self.state != new_state:
                logger.info(f"AGENT STATE: {self.state.value} -> {new_state.value}")
                self.state = new_state

    def handle_cycle(self):
        """A sophisticated agent cycle with state management."""
        try:
            # 1. LISTENING
            self.transition_to(AgentState.LISTENING)
            audio_data = self.recorder.listen_and_record()
            
            if audio_data is None:
                self.transition_to(AgentState.IDLE)
                return

            # 2. THINKING (STT + LLM)
            self.transition_to(AgentState.THINKING)
            audio_path = self.recorder.save_wav(audio_data)
            user_text = self.stt.transcribe(audio_path)
            
            if not user_text or len(user_text) < 2:
                logger.info("Ignoring empty or very short input.")
                self.transition_to(AgentState.IDLE)
                return

            # Add to memory and get context
            self.memory.add_message("user", user_text)
            context = self.memory.get_context()
            
            # Generate AI response
            ai_text = self.llm.generate_response(context)
            self.memory.add_message("assistant", ai_text)

            # 3. SPEAKING
            self.transition_to(AgentState.SPEAKING)
            output_wav = self.tts.synthesize(ai_text)
            
            if output_wav:
                # Start playback in a way that can be interrupted
                # For this version, we block but monitor for new speech in a separate thread if needed
                # SIMPLE INTERRUPT: If new speech is detected while playing, sd.stop() is called (logic below)
                self.player.play(output_wav)
            
            self.transition_to(AgentState.IDLE)

        except Exception as e:
            logger.error(f"Agent Cycle Error: {e}")
            self.transition_to(AgentState.ERROR)
            time.sleep(2) # Cooldown
            self.transition_to(AgentState.IDLE)

    def run(self):
        """Main Agent execution loop."""
        self.running = True
        logger.info("System Online. Awaiting your voice...")
        
        try:
            while self.running:
                self.handle_cycle()
        except KeyboardInterrupt:
            logger.info("Shutdown requested.")
            self.running = False
        finally:
            self.player.stop()
            logger.info("System Offline.")
