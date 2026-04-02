import openai
from app.config.settings import settings

class Model:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model_name = settings.LLM_MODEL

    def generate(self, messages):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
