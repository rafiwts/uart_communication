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
                startBtn.style.backgroundColor = "green";
                startBtn.style.color = "white";
                startBtn.disabled = true;

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
                startBtn.style.backgroundColor = "";
                startBtn.style.color = "";
                startBtn.disabled = false;

                streamingIndicator.style.display = "none";
            }
            alert(data.message);
        })
        .catch(function (error) {
            console.error("Error starting streaming:", error);
        });

});
