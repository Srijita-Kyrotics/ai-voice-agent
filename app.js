document.addEventListener('DOMContentLoaded', () => {
    const micBtn = document.getElementById('mic-btn');
    const statusText = document.getElementById('status-text');
    const recordingIndicator = document.getElementById('recording-indicator');
    const conversationLog = document.getElementById('conversation-log');
    const visualizer = document.getElementById('visualizer');

    let isRecording = false;
    let recognition;

    // Initialize Speech Recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            isRecording = true;
            micBtn.classList.add('recording');
            statusText.textContent = "Listening...";
            recordingIndicator.classList.remove('hidden');
            visualizer.classList.remove('hidden');
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            addMessage(transcript, 'user');
            handleAIResponse(transcript);
        };

        recognition.onerror = (event) => {
            console.error(event.error);
            statusText.textContent = "Error: " + event.error;
            stopRecording();
        };

        recognition.onend = () => {
            stopRecording();
        };
    } else {
        statusText.textContent = "Speech recognition not supported in this browser.";
        micBtn.disabled = true;
    }

    // Microphone toggle
    micBtn.addEventListener('click', () => {
        if (isRecording) {
            recognition.stop();
        } else {
            recognition.start();
        }
    });

    function stopRecording() {
        isRecording = false;
        micBtn.classList.remove('recording');
        statusText.textContent = "Click the microphone to start";
        recordingIndicator.classList.add('hidden');
        visualizer.classList.add('hidden');
    }

    function addMessage(text, role) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;
        msgDiv.textContent = text;
        conversationLog.appendChild(msgDiv);
        
        // Auto-scroll
        const container = document.getElementById('transcript-container');
        container.scrollTop = container.scrollHeight;
    }

    async function handleAIResponse(userText) {
        statusText.textContent = "Thinking...";
        
        // Mocking AI delay
        setTimeout(async () => {
            // Replace this with actual LLM API call
            const aiText = generateMockResponse(userText);
            addMessage(aiText, 'ai');
            speak(aiText);
            statusText.textContent = "Ready";
        }, 800);
    }

    function generateMockResponse(text) {
        const lowerText = text.toLowerCase();
        if (lowerText.includes('hello')) return "Hello there! I am your voice-enabled AI companion. How can I help you today?";
        if (lowerText.includes('time')) return "The current time is " + new Date().toLocaleTimeString();
        if (lowerText.includes('who are you')) return "I am a conversational AI agent designed to interact with you via speech.";
        return "I heard you say: '" + text + "'. That's very interesting!";
    }

    function speak(text) {
        if ('speechSynthesis' in window) {
            // Cancel current speaking
            window.speechSynthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1;
            utterance.pitch = 1;
            utterance.volume = 1;
            
            // Try to find a nice premium voice
            const voices = window.speechSynthesis.getVoices();
            const premiumVoice = voices.find(v => v.name.includes('Google') || v.name.includes('Premium') || v.name.includes('Natural'));
            if (premiumVoice) utterance.voice = premiumVoice;

            window.speechSynthesis.speak(utterance);
        }
    }
});
