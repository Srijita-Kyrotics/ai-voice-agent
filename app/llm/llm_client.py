import requests
import openai
from app.utils.logger import logger
from app.config.settings import settings

class LLMClient:
    def __init__(self, provider=None):
        self.provider = provider or settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL
        
        if self.provider == "openai":
            logger.info("Initializing OpenAI client...")
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
    def generate_response(self, messages):
        """Generate a response using the appropriate provider."""
        logger.info(f"Generating AI response via {self.provider}...")
        
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=150 # Keeping responses short for voice
                )
                return response.choices[0].message.content.strip()
            
            elif self.provider == "local":
                logger.info(f"Requesting local LLM at {settings.LOCAL_LLM_URL}")
                # Compatible with Ollama / Llama.cpp OpenAI endpoints
                payload = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                }
                resp = requests.post(settings.LOCAL_LLM_URL, json=payload, timeout=60)
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"].strip()
                
        except Exception as e:
            logger.error(f"LLM interaction failed: {e}")
            return "Unexpected error in my thought process. Please try again."
