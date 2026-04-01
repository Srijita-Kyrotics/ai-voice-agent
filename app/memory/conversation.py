from app.utils.logger import logger
from app.config.settings import settings

class ConversationMemory:
    def __init__(self, max_messages=None):
        self.max_messages = max_messages or settings.MAX_MEMORY_MESSAGES
        self.history = []
        # Initial system message
        self.system_prompt = "You are a helpful, low-latency voice assistant."

    def add_message(self, role, content):
        """Add user or assistant message to history."""
        self.history.append({"role": role, "content": content})
        self._trim_memory()

    def get_messages(self, system_prompt=None):
        """Return full history including system prompt."""
        msgs = [{"role": "system", "content": system_prompt or self.system_prompt}]
        msgs.extend(self.history)
        return msgs

    def _trim_memory(self):
        """Keep only the latest N messages."""
        if len(self.history) > self.max_messages:
            logger.info(f"Trimming memory. Removing {len(self.history) - self.max_messages} messages.")
            self.history = self.history[-self.max_messages:]

    def clear(self):
        self.history = []
        logger.info("Memory cleared.")
