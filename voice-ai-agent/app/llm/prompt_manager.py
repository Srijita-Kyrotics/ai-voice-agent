class PromptManager:
    @staticmethod
    def get_voice_assistant_prompt():
        return (
            "You are a helpful AI voice assistant. Your responses should be concise, "
            "warm, and natural for speech. Avoid complex formatting like markdown tables "
            "or long lists. Keep it brief and conversational."
        )

    @staticmethod
    def format_input(text):
        # Add any preprocessing if needed
        return text.strip()
