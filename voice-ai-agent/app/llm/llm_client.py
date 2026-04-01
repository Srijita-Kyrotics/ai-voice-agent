import requests
import openai
from app.utils.logger import logger
from app.config.settings import settings

class LLMClient:
    def __init__(self, provider=None):
        self.provider = provider or settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL
        
        if self.provider == "openai":
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
    def generate_response(self, messages):
        """Generate response from LLM given history."""
        logger.info(f"Generating LLM response using {self.provider} ({self.model})...")
        
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7
                )
                text = response.choices[0].message.content.strip()
                return text
            
            elif self.provider == "local":
                # Assuming Ollama or similar local API
                logger.info(f"Calling local LLM at {settings.LOCAL_LLM_URL}")
                payload = {
                    "model": "llama3", # Defaulting to llama3 for local
                    "messages": messages,
                    "stream": False
                }
                resp = requests.post(settings.LOCAL_LLM_URL, json=payload, timeout=30)
                resp.raise_for_status()
                # Assuming standard OpenAI format from local server
                text = resp.json()["choices"][0]["message"]["content"].strip()
                return text
                
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return "I apologize, but I encountered an error while processing your request."
