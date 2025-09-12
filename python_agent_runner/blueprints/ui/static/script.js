// Initialize the Mermaid library
mermaid.initialize({ startOnLoad: true });

var entityMap = {}; // Global map to store entity file paths

function handleExplainClick(entityName) {
    const filePath = entityMap[entityName];
    if (filePath) {
        const command = `explain ${entityName} in ${filePath}`;
        document.getElementById('user-input').value = command;
        document.getElementById('send-btn').click();
    } else {
        console.error(`File path for entity '${entityName}' not found.`);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // (User ID prompt and other element getters remain the same)
    const sendBtn = document.getElementById('send-btn');
    const userInput = document.getElementById('user-input');
    const chatLog = document.getElementById('chat-log');
    const mindmapContainer = document.getElementById('mindmap-container');

    const sendMessage = async () => {
        const message = userInput.value.trim();
        if (message === '') return;
        appendMessage('user', message);
        userInput.value = '';
        try {
            const response = await fetch('/send_message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message, user_id: sessionStorage.getItem('miso_user_id') }),
            });
            const data = await response.json();
            appendMessage('miso', data.response);

            if (data.entity_map) {
                entityMap = data.entity_map;
            }

            if (data.visualization_data) {
                const vizElement = document.createElement('div');
                vizElement.className = 'mermaid';
                vizElement.textContent = data.visualization_data;
                mindmapContainer.innerHTML = '';
                mindmapContainer.appendChild(vizElement);
                await mermaid.run({ nodes: [vizElement] });

                // --- Corrected Logic: Find nodes by their text content ---
                setTimeout(() => {
                    if (entityMap) {
                        const textElements = mindmapContainer.querySelectorAll('text');
                        textElements.forEach(textEl => {
                            const entityName = textEl.textContent.trim();
                            if (entityMap[entityName]) {
                                const parentNode = textEl.closest('g');
                                if (parentNode) {
                                    parentNode.style.cursor = 'pointer';
                                    parentNode.addEventListener('click', () => {
                                        handleExplainClick(entityName);
                                    });
                                }
                            }
                        });
                    }
                }, 100); // A small delay to ensure rendering is complete
            }
        } catch (error) {
            console.error('Error sending message:', error);
            appendMessage('miso', 'Sorry, there was an error connecting to the agent.');
        }
    };

    const appendMessage = (sender, text) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        messageElement.innerText = text;
        chatLog.appendChild(messageElement);
        chatLog.scrollTop = chatLog.scrollHeight;
    };

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    });
});
