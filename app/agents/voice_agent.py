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
        logger.info("--- INITIALIZING AI STUDY ASSISTANT ---")
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
        self.running = False
        self._lock = threading.Lock()

    def transition_to(self, new_state):
        with self._lock:
            if self.state != new_state:
                self.state = new_state

    def think(self, user_text):
        """THINK: Analyze user input for academic intent."""
        if not user_text or len(user_text.split()) < 2:
            return "IGNORE", "Noise or silence."
        
        text_lower = user_text.lower()
        
        # Check for question/explanation markers
        academic_keywords = ["what", "how", "explain", "physics", "math", "science", "history", "kya", "kaise"]
        if any(word in text_lower for word in academic_keywords):
            return "EXPLAIN", "User asked an academic question."
            
        return "CONVERSE", "General study conversation."

    def decide(self, thought_action, reason):
        """DECIDE: Decide action path."""
        if thought_action == "IGNORE":
            return None
        return thought_action

    def act(self, strategy, user_text):
        """ACT: Execute study assistant response."""
        if not strategy:
            return

        self.memory.add_message("user", user_text)
        
        self.transition_to(AgentState.THINKING)
        print("Thinking...")
        
        context = self.memory.get_context()
        ai_text = self.llm.generate_response(context)
        
        # Ensure brevity
        if len(ai_text.split()) > 45:
            ai_text = " ".join(ai_text.split()[:45]) + "."

        self.memory.add_message("assistant", ai_text)

        self.transition_to(AgentState.SPEAKING)
        wav_path = self.tts.synthesize(ai_text)
        
        if wav_path:
            play_thread = threading.Thread(target=self.player.play, args=(wav_path,))
            play_thread.start()
            
            while play_thread.is_alive():
                if self.recorder.is_speech_ongoing(duration=0.15):
                    logger.info("INTERRUPT: Student spoke again.")
                    self.player.stop()
                    break
                time.sleep(0.05)
            play_thread.join()

    def handle_cycle(self):
        try:
            self.transition_to(AgentState.LISTENING)
            print("Listening...")
            audio_data = self.recorder.listen_and_record()
            
            if audio_data is None:
                self.transition_to(AgentState.IDLE)
                return

            audio_path = self.recorder.save_wav(audio_data)
            user_text = self.stt.transcribe(audio_path)

            thought, reason = self.think(user_text)
            strategy = self.decide(thought, reason)
            self.act(strategy, user_text)
            
            self.transition_to(AgentState.IDLE)

        except Exception as e:
            logger.error(f"Study Helper Error: {e}")
            self.transition_to(AgentState.ERROR)
            time.sleep(1)
            self.transition_to(AgentState.IDLE)

    def run(self):
        self.running = True
        print("\n" + "="*40)
        print("  AI STUDY ASSISTANT: ONLINE")
        print("="*40)
        print("Status: I'm ready to help you with your studies.")
        
        try:
            intro = "Namaste! I am your AI Study Assistant. What would you like to learn today?"
            wav = self.tts.synthesize(intro)
            if wav: self.player.play(wav)
            
            while self.running:
                self.handle_cycle()
        except KeyboardInterrupt:
            self.running = False
        finally:
            self.player.stop()
            print("\n" + "="*40)
            print("  STUDY SESSION ENDED")
            print("="*40)
