from app.agents.voice_agent import VoiceAgent
from app.utils.logger import logger

def main():
    try:
        agent = VoiceAgent()
        agent.run()
    except Exception as e:
        logger.error(f"Application crash: {e}")

if __name__ == "__main__":
    main()
