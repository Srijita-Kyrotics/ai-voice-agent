import os
import time
from app.utils.logger import logger
from app.audio.recorder import AudioRecorder
from app.audio.player import AudioPlayer
from app.stt.whisper_stt import WhisperSTT
from app.llm.llm_client import LLMClient
from app.llm.prompt_manager import PromptManager
from app.tts.piper_tts import PiperTTS
from app.memory.conversation import ConversationMemory
from app.config.settings import settings

class VoiceAgent:
    def __init__(self):
        logger.info("Initializing Voice Agent Architecture...")
        settings.ensure_dirs()
        
        self.recorder = AudioRecorder()
        self.player = AudioPlayer()
        self.stt = WhisperSTT()
        self.llm = LLMClient()
        self.tts = PiperTTS()
        self.memory = ConversationMemory()
        
        self.running = False
        logger.info("Voice Agent ready.")

    def process_cycle(self):
        """One full cycle: Listen -> Transcribe -> Respond -> Speak."""
        try:
            # 1. Record Audio
            audio_data = self.recorder.record(duration=5) # 5s fixed for demo
            audio_path = self.recorder.save_wav(audio_data)
            
            # 2. Transcribe (STT)
            user_text = self.stt.transcribe(audio_path)
            if not user_text:
                return

            # 3. Get AI Response (Memory + LLM)
            self.memory.add_message("user", user_text)
            msgs = self.memory.get_messages(PromptManager.get_voice_assistant_prompt())
            
            ai_response = self.llm.generate_response(msgs)
            self.memory.add_message("assistant", ai_response)
            
            # 4. Speak Response (TTS + Player)
            audio_response_path = self.tts.synthesize(ai_response)
            if audio_response_path:
                self.player.play(audio_response_path)
                
        except Exception as e:
            logger.error(f"Error in Voice Agent Cycle: {e}")

    def run(self):
        self.running = True
        logger.info("Starting Voice Agent loop...")
        try:
            while self.running:
                self.process_cycle()
        except KeyboardInterrupt:
            logger.info("Stopping Voice Agent...")
            self.running = False
