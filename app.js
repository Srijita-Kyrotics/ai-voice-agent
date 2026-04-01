document.addEventListener('DOMContentLoaded', () => {
    const micBtn = document.getElementById('mic-btn');
    const clearBtn = document.getElementById('clear-btn');
    const statusText = document.getElementById('status-text');
    const recordingIndicator = document.getElementById('recording-indicator');
    const conversationLog = document.getElementById('conversation-log');
    const visualizer = document.getElementById('visualizer');

    let isRecording = false;
    let recognition;
    let conversationHistory = []; // Conversational Memory

    // Initialize Speech Recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true; // Low-latency feedback
        recognition.lang = 'en-US';

        let finalTranscript = '';

        recognition.onstart = () => {
            isRecording = true;
            micBtn.classList.add('recording');
            statusText.textContent = "Listening...";
            recordingIndicator.classList.remove('hidden');
            visualizer.classList.remove('hidden');
            finalTranscript = '';
            
            // Interrupt AI if it's speaking
            if (window.speechSynthesis.speaking) {
                window.speechSynthesis.cancel();
            }
        };

        recognition.onresult = (event) => {
            let interimTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }
            
            // Fast visual feedback
            if (interimTranscript) {
                statusText.textContent = interimTranscript;
            }
        };

        recognition.onerror = (event) => {
            console.error(event.error);
            if (event.error !== 'no-speech') {
                statusText.textContent = "Error: " + event.error;
            }
            stopRecording();
        };

        recognition.onend = () => {
            stopRecording();
            if (finalTranscript.trim()) {
                addMessage(finalTranscript, 'user');
                handleAIResponse(finalTranscript);
            }
        };
    } else {
        statusText.textContent = "Speech recognition not supported.";
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

    // Clear Memory
    clearBtn.addEventListener('click', () => {
        conversationHistory = [];
        conversationLog.innerHTML = '<div class="message system">Memory cleared. I\'m ready to start fresh!</div>';
        addMessage("Memory cleared.", 'system');
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
        
        // Add to history
        conversationHistory.push({ role: 'user', content: userText });

        // Simulate Low-latency response processing
        setTimeout(async () => {
            const aiText = generateContextualResponse(userText);
            
            // Add to history
            conversationHistory.push({ role: 'assistant', content: aiText });
            
            addMessage(aiText, 'ai');
            speak(aiText);
            statusText.textContent = "Ready";
        }, 400); // Faster processing time for low-latency feel
    }

    function generateContextualResponse(text) {
        const lowerText = text.toLowerCase();
        
        // Basic memory check
        const namesInHistory = conversationHistory.filter(m => m.role === 'user' && m.content.toLowerCase().includes('my name is'));
        
        if (lowerText.includes('what is my name')) {
            if (namesInHistory.length > 0) {
                const lastEntry = namesInHistory[namesInHistory.length - 1].content;
                const match = lastEntry.match(/my name is (.*)/i);
                if (match) return `Your name is ${match[1]}, as you told me earlier!`;
            }
            return "I'm sorry, I don't remember your name yet. Could you tell me?";
        }

        if (lowerText.includes('hello')) return "Hi again! I remember our previous messages. How can I help further?";
        if (lowerText.includes('time')) return "It is currently " + new Date().toLocaleTimeString();
        
        return "I'm keeping track of our conversation. You said: '" + text + "'. I have " + conversationHistory.length + " messages in my memory.";
    }

    function speak(text) {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.1; // Slightly faster for lower "perceived" latency
            utterance.pitch = 1;
            
            const voices = window.speechSynthesis.getVoices();
            const premiumVoice = voices.find(v => v.name.includes('Google') || v.name.includes('Premium') || v.name.includes('Natural'));
            if (premiumVoice) utterance.voice = premiumVoice;

            window.speechSynthesis.speak(utterance);
        }
    }
});
