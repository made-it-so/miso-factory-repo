document.addEventListener('DOMContentLoaded', function() {
    const chatHistory = document.getElementById('chat-history');
    const inputArea = document.getElementById('input-area');
    const clarityBar = document.getElementById('clarity-indicator-bar');
    
    const liveObjective = document.getElementById('live-objective');
    const liveOutputFormat = document.getElementById('live-output-format');
    const liveDataSource = document.getElementById('live-data-source');
    const finalActivationArea = document.getElementById('final-activation-area');

    let conversationState = {};

    function addMessage(sender, text, isHtml = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('chat-message', ${sender}-message);
        if (isHtml) {
            messageDiv.innerHTML = text;
        } else {
            messageDiv.textContent = text;
        }
        chatHistory.appendChild(messageDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function updateLivePrompt() {
        liveObjective.textContent = conversationState.objective || '...';
        liveOutputFormat.textContent = conversationState.output_format || '...';
        liveDataSource.textContent = conversationState.data_source || '...';
    }

    async function sendMessage(message) {
        if (message) {
            addMessage('user', message);
        }
        
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ state: conversationState, last_message: message })
            });
            const data = await response.json();
            
            conversationState = data.state;
            updateLivePrompt();
            updateClarity(data.clarity_score);
            renderMisoResponse(data);

        } catch (error) {
            console.error('Error with chat API:', error);
            addMessage('miso', 'Sorry, I encountered an error.');
        }
    }

    function renderMisoResponse(data) {
        addMessage('miso', data.response_text);

        switch(data.response_type) {
            case 'suggestions':
                const suggestionsHtml = data.options.map(opt => <button class='suggestion-btn' data-value=''></button>).join('');
                addMessage('miso', suggestionsHtml, true);
                document.querySelectorAll('.suggestion-btn').forEach(btn => {
                    btn.addEventListener('click', () => {
                        sendMessage(btn.dataset.value);
                    });
                });
                break;
            case 'file_upload':
                addMessage('miso', <input type='file' class='form-control mt-2'>, true);
                break;
            case 'final_prompt':
                finalActivationArea.innerHTML = 
                    <hr>
                    <form action="/submit_proposal" method="POST" class="mt-3">
                        <input type="hidden" name="objective" value="">
                        <button type="submit" class="btn btn-success w-100">Approve & Activate MISO</button>
                    </form>
                ;
                inputArea.innerHTML = '<p class="text-center text-success">Conversation complete. Please review and activate.</p>';
                break;
        }
    }

    function updateClarity(score) {
        clarityBar.style.width = ${score}%;
        clarityBar.textContent = ${score}% Complete;
        if (score < 50) clarityBar.className = 'progress-bar progress-bar-striped progress-bar-animated bg-danger';
        else if (score < 100) clarityBar.className = 'progress-bar progress-bar-striped progress-bar-animated bg-warning';
        else clarityBar.className = 'progress-bar bg-success';
    }

    inputArea.querySelector('form').addEventListener('submit', (e) => {
        e.preventDefault();
        const input = inputArea.querySelector('input');
        sendMessage(input.value);
        input.value = '';
    });

    sendMessage(null);
});
