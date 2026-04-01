from app.utils.logger import logger
from app.config.settings import settings

class ConversationMemory:
    def __init__(self, system_prompt, max_messages=8):
        self.max_messages = max_messages
        self.history = []
        self.system_prompt = system_prompt

    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})
        self._trim_memory()

    def get_context(self):
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.history)
        return messages

    def _trim_memory(self):
        if len(self.history) > self.max_messages:
            self.history = self.history[-self.max_messages:]

    def get_history_string(self):
        """Returns the conversation as a single string for summarization."""
        return "\n".join([f"{m['role'].upper()}: {m['content']}" for m in self.history])

    def clear(self):
        self.history = []
