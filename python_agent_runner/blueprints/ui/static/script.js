/**
 * MISO Application Forge - Living Blueprint UI
 * script.js - v7.0 (Mermaid.js Implementation)
 */
document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.getElementById('chat-messages');
    const blueprintPanel = document.getElementById('blueprint-panel-content');
    const workspacePanel = document.getElementById('workspace-panel-content');

    // Initialize Mermaid.js
    mermaid.initialize({ startOnLoad: false, theme: 'dark' });

    const addMessage = (sender, text) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender.toLowerCase()}-message`);
        const textSpan = document.createElement('span'); textSpan.innerHTML = text;
        messageElement.innerHTML = `<strong class="sender">${sender}:</strong> `;
        messageElement.appendChild(textSpan);
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    const updatePanels = async (blueprintContent, workspaceContent) => {
        const MERMAID_PREFIX = "MERMAID_DATA:";
        if (blueprintContent && blueprintContent.startsWith(MERMAID_PREFIX)) {
            const mermaidText = blueprintContent.substring(MERMAID_PREFIX.length);
            blueprintPanel.innerHTML = `<div class="mermaid">${mermaidText}</div>`;
            await mermaid.run({ nodes: [blueprintPanel.firstChild] });
        } else if (blueprintContent) {
            blueprintPanel.innerHTML = blueprintContent;
        }
        if (workspaceContent) {
            workspacePanel.innerHTML = workspaceContent;
        }
    };

    const processMisoResponse = async (userInput) => {
        let data;
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userInput }),
            });
            if (!response.ok) throw new Error(`Server returned status ${response.status}`);
            data = await response.json();
        } catch (error) { addMessage('MISO', `Error: Failed to fetch response.`); return; }
        
        try {
            addMessage('MISO', data.response);
            await updatePanels(data.blueprint, data.workspace);
        } catch (error) {
            console.error("Error updating UI panels:", error);
            addMessage('MISO', `UI Error: Failed to render visuals.`);
        }
    };

    const handleUserInput = () => {
        const userInput = chatInput.value.trim(); if (userInput === '') return;
        addMessage('User', userInput); chatInput.value = ''; chatInput.focus();
        processMisoResponse(userInput);
    };

    sendButton.addEventListener('click', handleUserInput);
    chatInput.addEventListener('keypress', (event) => { if (event.key === 'Enter') handleUserInput(); });

    const initializeUI = () => {
        updatePanels("// Blueprint...", "");
        setTimeout(() => addMessage('MISO', 'Connection established.'), 500);
        chatInput.focus();
    };

    initializeUI();
});
