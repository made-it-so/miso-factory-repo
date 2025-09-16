
function Pomodoro() {
    let timerInterval = null;
    let timerRunning = false;

    function startTimer(pomodoroTime) {
        if (timerRunning) return; // Can't start another timer while one is running
        timerRunning = true;
        timerInterval = setInterval(() => {
            const remainingTime = pomodoroTime - 1;
            document.getElementById("pomodoro-time").innerText = `Pomodoro Time: ${remainingTime} seconds`;
            if (remainingTime === 0) {
                stopTimer();
            }
        }, 1000);
    }

    function stopTimer() {
        timerRunning = false;
        clearInterval(timerInterval);
        document.getElementById("pomodoro-time").innerText = "Pomodoro Time: 25 minutes";
    }

    function startPomodoro() {
        fetch('/start_pomodoro')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    startTimer(1500); // Start timer for 25 minutes
                } else {
                    alert('Failed to start pomodoro');
                }
            })
            .catch(error => console.error('Error:', error));
    }

    function stopPomodoro() {
        fetch('/stop_pomodoro')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    stopTimer();
                } else {
                    alert('Failed to stop pomodoro');
                }
            })
            .catch(error => console.error('Error:', error));
    }

    document.addEventListener('DOMContentLoaded', () => {
        const startPomodoroButton = document.getElementById("start-pomodoro-button");
        startPomodoroButton.addEventListener('click', startPomodoro);

        const stopPomodoroButton = document.getElementById("stop-pomodoro-button");
        stopPomodoroButton.addEventListener('click', stopPomodoro);
    });
}
