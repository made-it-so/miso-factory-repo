document.addEventListener('DOMContentLoaded', () => {
    const sendBtn = document.getElementById('send-btn');
    const userInput = document.getElementById('user-input');
    const chatLog = document.getElementById('chat-log');
    const mindmapContainer = document.getElementById('mindmap-container'); // Get the visualizer container

    const sendMessage = async () => {
        const message = userInput.value.trim();
        if (message === '') return;

        appendMessage('user', message);
        userInput.value = '';

        try {
            const response = await fetch('/ui/send_message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message }),
            });
            const data = await response.json();
            
            // Append the text response to the chat
            appendMessage('miso', data.response);

            // --- New logic to handle the live preview ---
            if (data.preview_url) {
                // Clear any previous content
                mindmapContainer.innerHTML = '';
                
                // Create an iframe to display the preview
                const iframe = document.createElement('iframe');
                iframe.src = data.preview_url;
                iframe.style.width = '100%';
                iframe.style.height = '100%';
                iframe.style.border = 'none';
                mindmapContainer.appendChild(iframe);
            }

        } catch (error) {
            console.error('Error sending message:', error);
            appendMessage('miso', 'Sorry, there was an error connecting to the agent.');
        }
    };
    
    // (The rest of the script.js, including appendMessage, event listeners, and voice recognition, remains the same)

    const appendMessage = (sender, text) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        messageElement.innerText = text;
        chatLog.appendChild(messageElement);
        chatLog.scrollTop = chatLog.scrollHeight;
    };

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // --- Voice recognition code from previous steps would go here ---
});
