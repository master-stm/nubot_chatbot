function getArabicVoice() {
    const voices = window.speechSynthesis.getVoices();
    // Check for Arabic voice by language code
    for (let voice of voices) {
        if (voice.lang === 'ar-SA') {
            return voice;  // Return the Arabic voice if available
        }
    }
    return null;  // Return null if no Arabic voice is found
}

function getResponse(userText, lang) {
    const startTime = Date.now(); // Start timing on frontend
    
    fetch('/get_response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            text: userText,
            lang: lang
        })
    })
    .then(response => response.json())
    .then(data => {
        const { text, audio, timing } = data;
        
        // Display response and keep it visible
        displayResponse(text);
        
        // Log timing info
        console.log(`Response received in ${timing.total_time}s (TTS: ${timing.tts_time}s)`);
        
        if (audio) {
            const audioElement = new Audio(audio);
            audioElement.play();
        } else {
            if (lang === 'ar') {
                // Try to use the Arabic voice for speech synthesis
                const arabicVoice = getArabicVoice();
                if (arabicVoice) {
                    const utterance = new SpeechSynthesisUtterance(text);
                    utterance.voice = arabicVoice;  // Use the Arabic voice
                    window.speechSynthesis.speak(utterance);
                } else {
                    console.warn("No Arabic voice found. Using default.");
                    const utterance = new SpeechSynthesisUtterance(text);
                    window.speechSynthesis.speak(utterance);
                }
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        displayResponse("Oops! Something went wrong. Please try again.");
    });
}

// New function to display response and keep it visible
function displayResponse(text) {
    // Clear previous responses
    const chatContainer = document.querySelector('.chat-container') || document.getElementById('chat-container');
    if (chatContainer) {
        // Remove old responses but keep the current one
        const oldResponses = chatContainer.querySelectorAll('.nubot-response');
        oldResponses.forEach(response => response.remove());
    }
    
    // Add new response
    appendMessage(text, 'nubot');
    
    // Store the response text to keep it visible
    window.currentNubotResponse = text;
}
