// fetch frequency and debug mode from metadata
const frequencyDisplay = document.querySelector(".frequency");
const debugModeDisplay = document.querySelector(".debug-mode");

function fetchConfigInfo() {
    fetch("/device")
        .then(response => response.json())
        .then(data => {
            console.log("Data rerfieved:", data)
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
document.addEventListener("DOMContentLoaded", function() {
    checkStreamingStatus();
    fetchConfigInfo();
});

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

// post new device configuration parameterss
// if streaming values do not update
document.querySelector(".config-form").addEventListener("submit", function(event) {
    event.preventDefault();

    const frequency = document.getElementById("frequency").value;
    const debug_mode = document.getElementById("debugMode").checked;

    // create a request parameters from form
    const requestData = {
        frequency: parseInt(frequency),
        debug_mode: debug_mode
    };

    fetch("/config", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        setTimeout(() => {
            location.reload();
        }, 2000); // workaround for now
    })
    .catch(error => {
        console.error("Error updating config:", error);
        alert("Error updating config");
    });
});

// fetch new data every 2 seconds
async function fetchSensorData() {
    try {
        const response = await fetch("/messages?limit=6");
        const data = await response.json();

        const dataList = document.querySelector(".data-list");
        dataList.innerHTML = '';

        data.messages.forEach((message) => {
            const li = document.createElement("li");
            li.textContent = `Pressure: ${message.pressure}, Temp: ${message.temperature}, Velocity: ${message.velocity}`;
            dataList.appendChild(li);
        });
    } catch (error) {
        console.error("Error fetching sensor data:", error);
    }
}

setInterval(fetchSensorData, 2000);

fetchSensorData();

// handle metadata and latest messages buttons
// new tab will be opened with json data
document.querySelector(".metadata-btn").addEventListener("click", function() {
    window.open("/device-display", "_blank");
});

document.querySelector(".latest-messages-btn").addEventListener("click", function() {
    window.open("/messages-display", "_blank");
});
