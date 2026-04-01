# AI Voice Agent

A modern, high-quality conversational AI agent that takes spoken input and responds with spoken output. 

## Features

-   **Speech-to-Text (STT)**: Real-time voice recognition using the Web Speech API.
-   **Text-to-Speech (TTS)**: Natural voice synthesis with premium voice selection logic.
-   **Modern UI**: Premium dark mode experience with glassmorphism, smooth animations, and a voice visualizer.
-   **Zero Setup**: Runs entirely in the browser without requiring a backend for basic interaction.
-   **Extensible**: Easily connect to any LLM API (OpenAI, Gemini, Claude, etc.) to enhance the "brain".

## Getting Started

### Web Version (Premium UI)
1.  Open `index.html` in a modern web browser.
2.  Click the microphone button to start.

### Python Version (CLI)
1.  Install dependencies:
    ```bash
    pip install SpeechRecognition gTTS playsound PyAudio
    ```
2.  Run the agent:
    ```bash
    python main.py
    ```

## Project Structure

-   `index.html`, `style.css`, `app.js`: Web implementation.
-   `main.py`: Python implementation for CLI/Server use.

## LLM Integration

The application currently uses a mock response handler for demonstration. To connect a real AI model:

1.  Open `app.js`.
2.  Locate the `handleAIResponse` function.
3.  Replace the mock logic with a `fetch` request to your preferred LLM provider.

```javascript
async function handleAIResponse(userText) {
    // Replace with actual API call
    const response = await fetch('YOUR_LLM_API_ENDPOINT', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userText })
    });
    // ... process and display response
}
```

## Browser Support

-   Google Chrome (Full support)
-   Microsoft Edge (Full support)
-   Safari (Text-to-Speech support, limited Speech Recognition)
-   Firefox (Experimental support for Web Speech API)

---
  
