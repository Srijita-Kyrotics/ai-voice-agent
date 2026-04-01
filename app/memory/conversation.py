from app.utils.logger import logger
from app.config.settings import settings

class ConversationMemory:
    def __init__(self, system_prompt, max_messages=None):
        self.max_messages = max_messages or settings.MAX_MEMORY_MESSAGES
        self.history = []
        self.system_prompt = system_prompt
        logger.info(f"Memory initialized with max {self.max_messages} messages.")

    def add_message(self, role, content):
        """Add message and ensure memory stays within limits."""
        self.history.append({"role": role, "content": content})
        self._trim_memory()

    def get_context(self):
        """Return full context for LLM consumption."""
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.history)
        return messages

    def _trim_memory(self):
        """Intelligently trim memory, keeping last N assistant/user pairs."""
        if len(self.history) > self.max_messages:
            # We keep the most recent messages
            logger.info(f"Trimming conversation memory from {len(self.history)} to {self.max_messages}")
            self.history = self.history[-self.max_messages:]

    def clear(self):
        """Reset conversation."""
        self.history = []
        logger.info("Conversation memory cleared.")
