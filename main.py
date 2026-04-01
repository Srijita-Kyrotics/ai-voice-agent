import speech_recognition as sr
import os
import time
import requests
import json
from datetime import datetime

# You can use edge-tts or gTTS for better quality
# For this script we will use gTTS and a simple play command
from gtts import gTTS 
import playsound

class VoiceAgent:
    def __init__(self, name="AI Companion"):
        self.name = name
        self.recognizer = sr.Recognizer()
        self.history = []
        print(f"--- {self.name} Initialized ---")

    def speak(self, text):
        print(f"AI: {text}")
        try:
            tts = gTTS(text=text, lang='en')
            filename = "response.mp3"
            tts.save(filename)
            playsound.playsound(filename)
            os.remove(filename)
        except Exception as e:
            print(f"Error in TTS: {e}")

    def listen(self):
        with sr.Microphone() as source:
            print("\nListening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
            audio = self.recognizer.listen(source)
            
        try:
            print("Processing speech...")
            query = self.recognizer.recognize_google(audio)
            print(f"User: {query}")
            return query
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None

    def get_ai_response(self, user_input):
        # Add memory
        self.history.append({"role": "user", "content": user_input})
        
        # Simple logic for now (Connect to LLM API here)
        if "time" in user_input.lower():
            response = f"The current time is {datetime.now().strftime('%H:%M:%S')}"
        elif "your name" in user_input.lower():
            response = f"I am {self.name}, your voice assistant."
        elif "hello" in user_input.lower():
            response = "Hello! I remember our conversation. How can I help you?"
        else:
            response = f"I heard you say: {user_input}. I'm keeping this in my memory."
            
        self.history.append({"role": "assistant", "content": response})
        return response

    def run(self):
        self.speak("Hello, how can I help you today?")
        while True:
            user_input = self.listen()
            if user_input:
                if "exit" in user_input.lower() or "stop" in user_input.lower():
                    self.speak("Goodbye!")
                    break
                
                response = self.get_ai_response(user_input)
                self.speak(response)

if __name__ == "__main__":
    # Note: Requires 'pip install SpeechRecognition gTTS playsound PyAudio'
    agent = VoiceAgent()
    try:
        agent.run()
    except KeyboardInterrupt:
        print("\nAgent stopped.")
