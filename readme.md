# AI Voice Agent

A modern, high-quality conversational AI agent that takes spoken input and responds with spoken output. 

## Features

-   **Speech-to-Text (STT)**: Real-time voice recognition using the Web Speech API.
-   **Text-to-Speech (TTS)**: Natural voice synthesis with premium voice selection logic.
-   **Modern UI**: Premium dark mode experience with glassmorphism, smooth animations, and a voice visualizer.
-   **Zero Setup**: Runs entirely in the browser without requiring a backend for basic interaction.
-   **Extensible**: Easily connect to any LLM API (OpenAI, Gemini, Claude, etc.) to enhance the "brain".

## Getting Started

1.  Clone or download this repository.
2.  Open `index.html` in a modern web browser (Chrome, Edge, Safari).
3.  Click the microphone button to start a conversation.
    -   *Note: You may need to grant browser permission for the microphone.*

## Project Structure

-   `index.html`: Main layout and structural elements.
-   `style.css`: Modern visual design system and animations.
-   `app.js`: Core logic for speech processing and conversation handling.

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

