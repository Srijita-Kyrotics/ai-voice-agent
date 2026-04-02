class Memory:
    def __init__(self):
        self.messages = [
            {"role": "system", "content": "You are a voice assistant"}
        ]

    def add(self, role, content):
        self.messages.append({"role": role, "content": content})
        self.messages = self.messages[-6:]

    def get_context(self):
        return self.messages
