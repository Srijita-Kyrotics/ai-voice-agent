from abc import ABC, abstractmethod
from app.utils.logger import logger

class BaseAgent(ABC):
    @abstractmethod
    def record(self):
        """Record audio from the microphone."""
        pass

    @abstractmethod
    def transcribe(self, audio):
        """Transcribe audio to text."""
        pass

    @abstractmethod
    def is_valid_input(self, text):
        """Check if the transcribed text is valid for processing."""
        pass

    @abstractmethod
    def decide(self, text):
        """Decide whether to act on the text or ignore it."""
        pass

    @abstractmethod
    def generate_response(self, text):
        """Generate a response based on the text."""
        pass

    @abstractmethod
    def speak(self, response):
        """Convert response text to speech and play it."""
        pass

    @abstractmethod
    def update_memory(self, text, response):
        """Update the conversation memory with the interaction."""
        pass

    def run(self):
        """Execute a single conversational cycle."""
        try:
            print("Listening...")
            audio = self.record()
            
            if audio is None:
                return

            text = self.transcribe(audio)
            
            if not self.is_valid_input(text):
                return

            print("Thinking...")
            
            decision = self.decide(text)

            if decision == "ignore":
                return
            
            response = self.generate_response(text)
            
            self.speak(response)
            self.update_memory(text, response)
            
        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            raise e
