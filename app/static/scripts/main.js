// fetch frequency and debug mode from metadata
const frequencyDisplay = document.querySelector(".frequency");
const debugModeDisplay = document.querySelector(".debug-mode");

function fetchConfigInfo() {
    fetch("/device")
        .then(response => response.json())
        .then(data => {
            console.log("Data rerfieved:", data)
            console.log(data.curr_config.frequency)
            frequencyDisplay.textContent = data.curr_config.frequency;
            debugModeDisplay.textContent = data.curr_config.debug ? "ON" : "OFF";
        })
        .catch(error => console.error("Error fetching config info:", error));
}

// function to check streaming status on page load
function checkStreamingStatus() {
    fetch("/status")
        .then(response => response.json())
        .then(data => {
            if (data.streaming) {
                console.log(data);
                startBtn.classList.add("streaming");
                startBtn.disabled = true;
                stopBtn.disabled = false;
                streamingIndicator.style.display = "block";
            } else {
                startBtn.classList.remove("streaming");
                startBtn.disabled = false;
                stopBtn.disabled = true;
                streamingIndicator.style.display = "none";
            }
            fetchConfigInfo();
        })
        .catch(error => console.error("Error checking streaming status:", error));
}

// add this function when page loads so the state is remembered
document.addEventListener("DOMContentLoaded", checkStreamingStatus);

// start and stop streaming
const startBtn = document.querySelector(".start-btn");
const stopBtn = document.querySelector(".stop-btn");
const streamingIndicator = document.querySelector(".streaming-indicator");

startBtn.addEventListener("click", function () {
    fetch("/start")
        .then(function (response) {
            return response.json();
        })
        .then(function(data) {
            if (data.message === "Data streaming started") {
                startBtn.classList.add("streaming");
                startBtn.disabled = true;
                stopBtn.disabled = false;
                streamingIndicator.style.display = "block";
            }
            alert(data.message);
        })
        .catch(function (error) {
            console.error("Error starting streaming:", error);
        });
});

stopBtn.addEventListener("click", function () {
    fetch("/stop")
        .then(function (response) {
            return response.json();
        })
        .then(function(data) {
            if (data.message === "Data streaming stopped") {
                startBtn.classList.remove("streaming");
                startBtn.disabled = false;
                stopBtn.disabled = true;
                streamingIndicator.style.display = "None";
            }
            alert(data.message);
        })
        .catch(function (error) {
            console.error("Error starting streaming:", error);
        });

});
