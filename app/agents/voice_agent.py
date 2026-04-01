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
        logger.info("--- INITIALIZING INTELLIGENT INTERVIEW ASSISTANT ---")
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
                logger.info(f"STATUS: {new_state.value}")
                self.state = new_state

    def think(self, user_text):
        """Analyze input and decide approach."""
        if not user_text or len(user_text.split()) < 2:
            return "SKIP", "Input too short or silent."
        
        # Simple heuristic for clarification vs move on
        if "?" in user_text or "help" in user_text.lower():
            return "RESPOND_HELP", "User needs assistance."
            
        return "RESPOND_INTERVIEW", "Valid interview response."

    def decide(self, thought_action, reason):
        """Map thought to a concrete action strategy."""
        logger.info(f"THINK Result: {thought_action} ({reason})")
        
        if thought_action == "SKIP":
            return None
        
        return thought_action

    def act(self, action, user_text):
        """Execute the decided action."""
        if action is None:
            return

        # Update memory
        self.memory.add_message("user", user_text)
        
        # 1. Generate LLM Response
        self.transition_to(AgentState.THINKING)
        context = self.memory.get_context()
        ai_text = self.llm.generate_response(context)
        
        self.memory.add_message("assistant", ai_text)

        # 2. Synthesize & Speak with Interrupt Support
        self.transition_to(AgentState.SPEAKING)
        output_wav = self.tts.synthesize(ai_text)
        
        if output_wav:
            # Play in a thread to allow energy monitoring for interrupts
            play_thread = threading.Thread(target=self.player.play, args=(output_wav,))
            play_thread.start()
            
            # Monitor for interruptions while playing
            while play_thread.is_alive():
                if self.recorder.is_speech_ongoing(duration=0.2):
                    logger.info("USER INTERRUPTED - Stopping AI speech.")
                    self.player.stop()
                    self.transition_to(AgentState.INTERRUPTED)
                    break
                time.sleep(0.1)
            
            play_thread.join()

    def handle_cycle(self):
        try:
            # LISTEN
            self.transition_to(AgentState.LISTENING)
            audio_data = self.recorder.listen_and_record()
            
            if audio_data is None:
                self.transition_to(AgentState.IDLE)
                return

            # TRANSCRIBE
            audio_path = self.recorder.save_wav(audio_data)
            user_text = self.stt.transcribe(audio_path)

            # THINK-DECIDE-ACT
            action, reason = self.think(user_text)
            strategy = self.decide(action, reason)
            self.act(strategy, user_text)
            
            self.transition_to(AgentState.IDLE)

        except Exception as e:
            logger.error(f"Agent Loop Error: {e}")
            self.transition_to(AgentState.ERROR)
            time.sleep(2)
            self.transition_to(AgentState.IDLE)

    def run(self):
        self.running = True
        print("\n--- AI INTERVIEW ASSISTANT ONLINE ---")
        print("I will ask you interview questions. Speak clearly into the microphone.\n")
        
        try:
            # Initial prompt/introduction
            intro = "Hello! I am your AI Interview Assistant. Are you ready to start the mock interview?"
            self.memory.add_message("assistant", intro)
            wav_path = self.tts.synthesize(intro)
            if wav_path: self.player.play(wav_path)
            
            while self.running:
                self.handle_cycle()
        except KeyboardInterrupt:
            self.running = False
        finally:
            self.player.stop()
            print("\nInterview session ended. Good luck!")
