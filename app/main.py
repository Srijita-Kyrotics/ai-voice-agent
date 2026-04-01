import time
from app.agents.voice_agent import VoiceAgent
from app.utils.logger import logger
from app.config.settings import AgentState

def main():
    print("\n" + "="*40)
    print("  AI VOICE AGENT: ONLINE")
    print("="*40)
    
    agent = VoiceAgent()
    running = True

    # Introductory message
    try:
        intro = "Hello! I am your AI Voice Agent. How can I help you today?"
        agent.speak(intro)
    except Exception as e:
        logger.error(f"Failed to play intro: {e}")

    while running:
        try:
            # Control Layer: Execute one conversational cycle
            agent.run()
            
            # Small delay to prevent tight loop if record() returns immediately
            time.sleep(0.1)
            
        except KeyboardInterrupt:
            print("\n" + "="*40)
            print("  SESSION ENDED BY USER")
            print("="*40)
            running = False
        except Exception as e:
            logger.error(f"Control Layer Error: {e}")
            agent.transition_to(AgentState.ERROR)
            time.sleep(2) # Give some time before retrying
            agent.transition_to(AgentState.IDLE)

if __name__ == "__main__":
    main()
