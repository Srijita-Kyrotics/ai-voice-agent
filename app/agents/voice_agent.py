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
        logger.info("--- PRODUCTION AGENT INITIALIZATION ---")
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
                # Only log state transitions to file, keep console for UX

    def think(self, user_text):
        """THINK: Analyze user input for intent and quality."""
        if not user_text or len(user_text.split()) < 2:
            return "IGNORE", "Noise or silence detected."
        
        text_lower = user_text.lower()
        
        # Detect clear intents
        if any(word in text_lower for word in ["help", "what", "how", "repeat"]):
            return "CLARIFY", "User is asking for help or clarification."
            
        if len(user_text.split()) > 15:
            return "PROCESS_DETAILED", "User provided a comprehensive answer."
            
        return "PROCESS_STANDARD", "Standard conversational input."

    def decide(self, thought_action, reason):
        """DECIDE: Choose the best strategy based on the 'thought'."""
        if thought_action == "IGNORE":
            return None
            
        logger.debug(f"Decision Logic: {thought_action} due to '{reason}'")
        return thought_action

    def act(self, strategy, user_text):
        """ACT: Execute the chosen strategy."""
        if not strategy:
            return

        # 1. Update context
        self.memory.add_message("user", user_text)
        
        # 2. Generate Intelligent Response
        self.transition_to(AgentState.THINKING)
        print("Thinking...")
        
        context = self.memory.get_context()
        ai_text = self.llm.generate_response(context)
        
        # Ensure brevity (as per requirements)
        if len(ai_text.split()) > 40:
            ai_text = " ".join(ai_text.split()[:40]) + "."

        self.memory.add_message("assistant", ai_text)

        # 3. Speak & Support Interrupts
        self.transition_to(AgentState.SPEAKING)
        wav_path = self.tts.synthesize(ai_text)
        
        if wav_path:
            play_thread = threading.Thread(target=self.player.play, args=(wav_path,))
            play_thread.start()
            
            # Monitor for interrupts
            while play_thread.is_alive():
                if self.recorder.is_speech_ongoing(duration=0.15):
                    logger.info("INTERRUPT: Stopping AI playback.")
                    self.player.stop()
                    break
                time.sleep(0.05)
            play_thread.join()

    def handle_cycle(self):
        try:
            # LISTEN
            self.transition_to(AgentState.LISTENING)
            print("Listening...")
            audio_data = self.recorder.listen_and_record()
            
            if audio_data is None:
                self.transition_to(AgentState.IDLE)
                return

            # TRANSCRIBE
            audio_path = self.recorder.save_wav(audio_data)
            user_text = self.stt.transcribe(audio_path)

            # THINK-DECIDE-ACT
            thought, reason = self.think(user_text)
            strategy = self.decide(thought, reason)
            self.act(strategy, user_text)
            
            self.transition_to(AgentState.IDLE)

        except Exception as e:
            logger.error(f"Production Loop Error: {e}")
            print(f"Error: {e}")
            self.transition_to(AgentState.ERROR)
            time.sleep(1)
            self.transition_to(AgentState.IDLE)

    def run(self):
        self.running = True
        print("\n" + "="*40)
        print("  AI INTERVIEW ASSISTANT: ONLINE")
        print("="*40)
        print("Status: Ready to help with your mock interview.")
        
        try:
            # Initial Greeting
            intro = "Welcome! I'm your AI Interview Assistant. Shall we begin your mock interview?"
            wav = self.tts.synthesize(intro)
            if wav: self.player.play(wav)
            
            while self.running:
                self.handle_cycle()
        except KeyboardInterrupt:
            self.running = False
        except Exception as e:
            logger.critical(f"System Failure: {e}")
        finally:
            self.player.stop()
            print("\n" + "="*40)
            print("  SYSTEM SHUTDOWN: GOODBYE")
            print("="*40)
