const roomName = JSON.parse(document.getElementById('room-name').textContent);
const userName = JSON.parse(document.getElementById('user-name').textContent);
const hostName = JSON.parse(document.getElementById('host-name').textContent)
const isInstructor = JSON.parse(document.getElementById('is-instructor').textContent);

var ws = new WebSocket('ws://' + hostName + '/ws/live-qa-session/' + roomName + '/');

ws.onmessage = function (event) {
    console.log('Message received:', event.data);
    var question = JSON.parse(event.data);
    var card = createCard(question);
    document.getElementById("question-list").prepend(card);
};

document.querySelector('#chat-message-input').onkeyup = function (e) {
    if (e.keyCode === 13 && !e.shiftKey) {
        e.preventDefault();
        sendQuestion();
    }
};

document.getElementById('post-question-btn').onclick = function () {
    sendQuestion();
}

function sendQuestion() {
    const messageInputDom = document.getElementById('chat-message-input');
    const message = messageInputDom.value;
    let sender = userName;
    if (!isInstructor) {
        const anonymousCheckboxDom = document.getElementById('anonymous-checkbox');
        sender = anonymousCheckboxDom.checked ? 'Anonymous' : userName;
    }
    ws.send(JSON.stringify({
        'message': message,
        'sender': sender,
        'timestamp': new Date().toISOString()
    }));
    messageInputDom.value = '';
}

function createCard(question) {
    // Create a new card element
    var card = document.createElement("div");
    card.className = "card mb-3";
    var cardBody = document.createElement("div");
    cardBody.className = "card-body";
    card.appendChild(cardBody);
    // Add the sender name
    var sender = document.createElement("h5");
    sender.className = "card-title";
    sender.textContent = question.sender;
    cardBody.appendChild(sender);
    // Add the timestamp
    var timeStamp = document.createElement("p");
    timeStamp.className = "text-muted small";
    var options = { hour: "2-digit", minute: "2-digit" };
    timeStamp.textContent = `Posted on ${new Date(question.timestamp).toLocaleTimeString([], options)}`;
    cardBody.appendChild(timeStamp);
    // Add the question message
    var newPost = document.createElement("p");
    newPost.className = "card-text";
    newPost.innerHTML = question.message.replace(/\n/g, '<br>');
    cardBody.appendChild(newPost);
    return card;
}

ws.onopen = function () {
    console.log('Connection opened');
};

ws.onerror = function (error) {
    console.error('WebSocket Error:', error);
};

ws.onclose = function (event) {
    console.log('Connection closed', event.reason);
};