/**
 * MISO Application Forge - Living Blueprint UI
 * script.js - v9.0 (Resizable & Collapsible Panels)
 */
(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', () => {
        // --- DOM Element Selection ---
        const chatInput = document.getElementById('chat-input');
        const sendButton = document.getElementById('send-button');
        const chatMessages = document.getElementById('chat-messages');
        const blueprintPanel = document.getElementById('blueprint-panel-content');
        const workspacePanel = document.getElementById('workspace-panel-content');
        const modalOverlay = document.getElementById('decision-modal-overlay');
        const modalCloseBtn = document.getElementById('modal-close-btn');

        // --- Initialize Resizable Panels ---
        Split(['#blueprint-panel', '#workspace-panel', '#chat-panel'], {
            sizes: [25, 45, 30],
            minSize: 40, // Minimum size in pixels
            gutterSize: 10,
            cursor: 'col-resize'
        });

        // --- Initialize Collapsible Panels ---
        const collapseButtons = document.querySelectorAll('.collapse-btn');
        collapseButtons.forEach(button => {
            button.addEventListener('click', () => {
                const panel = button.closest('.panel');
                panel.classList.toggle('collapsed');
            });
        });

        // --- Core Functions ---

        const addMessage = (sender, text) => {
            const messageElement = document.createElement('div');
            messageElement.classList.add('message', `${sender.toLowerCase()}-message`);
            
            const textSpan = document.createElement('span');
            textSpan.innerHTML = text;
            messageElement.innerHTML = `<strong class="sender">${sender}:</strong> `;
            messageElement.appendChild(textSpan);

            if (sender === 'MISO' && text.includes('<pre>')) {
                const copyBtn = document.createElement('button');
                copyBtn.textContent = 'Copy';
                copyBtn.className = 'copy-btn';
                
                copyBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const codeBlock = messageElement.querySelector('pre');
                    if (codeBlock) {
                        navigator.clipboard.writeText(codeBlock.textContent)
                            .then(() => {
                                copyBtn.textContent = 'Copied!';
                                setTimeout(() => { copyBtn.textContent = 'Copy'; }, 2000);
                            });
                    }
                });
                messageElement.appendChild(copyBtn);
            }
            
            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        };

        const renderMindMap = (markdown) => {
            if (window.mermaid) {
                blueprintPanel.innerHTML = `<div class="mermaid">${markdown}</div>`;
                mermaid.run({ nodes: [blueprintPanel.firstChild] });
            } else {
                blueprintPanel.innerHTML = "Error: Could not load Mind Map library.";
            }
        };

        const updatePanels = (blueprintContent, workspaceContent) => {
            if (blueprintContent && typeof blueprintContent === 'string') {
                const processedContent = blueprintContent.trim();
                if (processedContent.toUpperCase().startsWith('MERMAID_DATA:')) {
                    const mermaidText = processedContent.substring(13);
                    renderMindMap(mermaidText);
                } else {
                    blueprintPanel.innerHTML = blueprintContent;
                }
            }
            if (workspaceContent) {
                workspacePanel.innerHTML = workspaceContent;
            }
        };

        const processMisoResponse = async (userInput) => {
            // This function handles the new modal decision requests
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

            if (data.type === 'DECISION_REQUEST') {
                showDecisionModal(data);
            } else {
                addMessage('MISO', data.response);
                updatePanels(data.blueprint, data.workspace);
            }
        };

        const handleUserInput = () => {
            const userInput = chatInput.value.trim(); if (userInput === '') return;
            addMessage('User', userInput); chatInput.value = ''; chatInput.focus();
            processMisoResponse(userInput);
        };
        
        // --- Modal Functions ---
        const modalQuestion = document.getElementById('modal-question');
        const optionAContent = document.getElementById('modal-option-a-content');
        const optionBContent = document.getElementById('modal-option-b-content');
        const modalButtons = document.querySelectorAll('.modal-button');

        const showDecisionModal = (data) => {
            modalQuestion.textContent = data.question;
            optionAContent.innerHTML = data.options.option_a;
            optionBContent.innerHTML = data.options.option_b;
            modalOverlay.style.display = 'flex';
        };

        const hideDecisionModal = () => {
            modalOverlay.style.display = 'none';
        };

        const handleDecision = async (e) => {
            const choice = e.target.dataset.choice;
            addMessage('User', `Selected Option ${choice}`);
            hideDecisionModal();
            
            await fetch('/api/decision', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ choice: choice })
            });
        };

        // --- Event Listeners & Initialization ---
        sendButton.addEventListener('click', handleUserInput);
        chatInput.addEventListener('keypress', (event) => { if (event.key === 'Enter') handleUserInput(); });
        modalCloseBtn.addEventListener('click', hideDecisionModal);
        modalButtons.forEach(button => button.addEventListener('click', handleDecision));
        
        const initializeUI = () => {
            updatePanels("// Blueprint...", "");
            setTimeout(() => addMessage('MISO', 'Connection established.'), 500);
            chatInput.focus();
        };

        initializeUI();
    });

})();
