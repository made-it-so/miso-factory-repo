document.addEventListener('DOMContentLoaded', () => {
    // Tab functionality
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === button.dataset.tab) {
                    content.classList.add('active');
                }
            });
        });
    });

    // --- Create Project Tab ---
    const objectiveForm = document.getElementById('objective-form');
    const objectiveText = document.getElementById('objective-text');
    const submitBtn = document.getElementById('submit-btn');
    const logContainer = document.getElementById('log-container');
    let pollIntervalId;

    objectiveForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const objective = objectiveText.value.trim();
        if (!objective) return;

        submitBtn.disabled = true;
        submitBtn.textContent = 'MISO is working...';
        logContainer.style.display = 'block';
        logContainer.textContent = 'Initializing MISO pipeline...';

        try {
            const response = await fetch('/api/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ objective: objective })
            });
            const data = await response.json();
            if (data.task_id) {
                pollIntervalId = setInterval(() => pollStatus(data.task_id), 3000);
            } else {
                logContainer.textContent = `Error: ${data.error || 'Unknown error'}`;
                resetCreateUi();
            }
        } catch (error) {
            logContainer.textContent = `Error submitting task: ${error}`;
            resetCreateUi();
        }
    });

    async function pollStatus(taskId) {
        try {
            const response = await fetch(`/api/status/${taskId}`);
            const data = await response.json();
            logContainer.textContent = data.log_output || 'Waiting for log output...';
            logContainer.scrollTop = logContainer.scrollHeight;
            if (data.status === 'COMPLETE' || data.status === 'FAILED') {
                clearInterval(pollIntervalId);
                logContainer.textContent += `\n\n--- PIPELINE ${data.status} ---\n` + JSON.stringify(data.result, null, 2);
                logContainer.scrollTop = logContainer.scrollHeight;
                resetCreateUi();
            }
        } catch (error) {
            logContainer.textContent += `\nError polling status: ${error}`;
            clearInterval(pollIntervalId);
            resetCreateUi();
        }
    }

    function resetCreateUi() {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Make It So';
    }

    // --- Ask MISO Tab ---
    const queryForm = document.getElementById('query-form');
    const queryText = document.getElementById('query-text');
    const queryBtn = document.getElementById('query-btn');
    const queryResult = document.getElementById('query-result');

    queryForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const question = queryText.value.trim();
        if (!question) return;

        queryBtn.disabled = true;
        queryBtn.textContent = 'MISO is thinking...';
        queryResult.style.display = 'block';
        queryResult.textContent = 'Querying the Codex...';

        try {
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: question })
            });
            const data = await response.json();
            queryResult.textContent = data.answer || "Sorry, I couldn't find an answer.";
        } catch (error) {
            queryResult.textContent = `Error processing query: ${error}`;
        } finally {
            queryBtn.disabled = false;
            queryBtn.textContent = 'Ask Question';
        }
    });
});

