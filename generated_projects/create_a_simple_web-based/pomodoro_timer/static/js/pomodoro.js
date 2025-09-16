
function startPomodoro() {
    let seconds = 0;
    let minutes = 25;
    let hours = 0;

    function updateTimerDisplay() {
        const timerDisplay = document.getElementById("timer-display");
        let timeString = `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
        timerDisplay.innerText = timeString;
    }

    function decreaseTimer() {
        if (seconds > 0) {
            seconds--;
        } else if (minutes > 0) {
            minutes--;
            seconds = 59;
        } else {
            hours++;
            minutes = 25;
            seconds = 0;
        }
        updateTimerDisplay();
    }

    function handleStartPomodoro() {
        const startButton = document.getElementById("start-button");
        startButton.addEventListener("click", () => {
            setInterval(decreaseTimer, 1000);
            startButton.disabled = true;
        });
    }

    function handleStopPomodoro() {
        const stopButton = document.getElementById("stop-button");
        stopButton.addEventListener("click", () => {
            clearInterval(intervalId);
            startButton.disabled = false;
        });
    }

    let intervalId;

    window.onload = () => {
        updateTimerDisplay();
        handleStartPomodoro();
        handleStopPomodoro();
    };
