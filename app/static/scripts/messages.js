// display latest messages in json
document.querySelector(".latest-messages-form").addEventListener("submit", function(event) {
    event.preventDefault();

    const limit = document.getElementById("messageLimit").value;

    fetch("/messages?limit=" + limit)
            .then(function(response) {
                return response.json();
            })
            .then(function(data) {
                console.log(data)
                const messagesList = document.querySelector(".messages-list");
                messagesList.innerHTML = '';

                data.messages.forEach(function(message) {
                    const li = document.createElement("li");
                    li.textContent = "Pressure: " + message.pressure + ", Temp: " + message.temperature + ", Velocity: " + message.velocity;
                    messagesList.appendChild(li);
                });
            })
            .catch(function(error) {
                console.error("Error fetching messages:", error);
                alert("Failed to load messages.");
            });
});
