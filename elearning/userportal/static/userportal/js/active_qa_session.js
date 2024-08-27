const roomName = JSON.parse(document.getElementById('room-name').textContent);
const userName = JSON.parse(document.getElementById('user-name').textContent);
const hostName = JSON.parse(document.getElementById('host-name').textContent)
const isInstructor = JSON.parse(document.getElementById('is-instructor').textContent);

class WebSocketClient {
    constructor(url) {
        this.url = url;
        this.ws = null;
        this.maxRetries = 5;
        this.autoReconnectInterval = 1000 * 3;
        this.messageHandlers = new Map();
    }

    connect() {
        this.ws = new WebSocket(this.url);
        this.ws.onopen = () => {
            console.log('WebSocket connection opened');
            this.maxRetries = 5;
            this.triggerHandler('open');
        }
        this.ws.onclose = (e) => {
            console.log('WebSocket connection closed:', e.reason);
            if (e.code === 4000) {
                console.log('The instructor has ended the session.');
                return;
            }
            if (!e.wasClean) {
                this.reconnect();
            }
        }
        this.ws.onerror = (e) => {
            console.error('WebSocket error:', e);
        }
        this.ws.onmessage = (e) => {
            console.log('Message received:', e.data);
            const data = JSON.parse(e.data);
            this.triggerHandler('message', data);
        }
    }

    reconnect() {
        if (this.maxRetries > 0) {
            setTimeout(() => {
                console.log('Reconnecting...');
                this.connect();
                this.maxRetries--;
            }, this.autoReconnectInterval);
        } else {
            console.error('Max retries reached. Could not reconnect to server.');
        }
    }

    addHandler(event, handler) {
        if (!this.messageHandlers.has(event)) {
            this.messageHandlers.set(event, new Set());
        }
        this.messageHandlers.get(event).add(handler);
    }

    triggerHandler(event, data) {
        const handlers = this.messageHandlers.get(event) || new Set();
        for (const handler of handlers) {
            handler(data);
        }
    }
}

url = 'ws://' + hostName + '/ws/live-qa-session/' + roomName + '/';
const client = new WebSocketClient(url);

client.addHandler('open', () => {
    setupFormEventListeners();
});

client.addHandler('message', (data) => {
    if (data.type === 'session.end.notice') {
        handleSessionEnd(data);
    } else if (data.type === 'question.list') {
        handleQuestionList(data.questions);
    } else {
        // Normal message
        createCard(data);
    }
});

function handleSessionEnd(data) {
    disableFormElements();
    createCard(data);
}

function handleQuestionList(questions) {
    const questionList = document.getElementById("question-list");
    if (!questionList) {
        return;
    }
    questionList.innerHTML = '';
    questions.forEach(createCard);
}

function sendQuestion() {
    const messageInputDom = document.getElementById('chat-message-input');
    const message = messageInputDom.value;
    let sender = userName;
    if (!isInstructor) {
        const anonymousCheckboxDom = document.getElementById('anonymous-checkbox');
        sender = anonymousCheckboxDom.checked ? 'Anonymous' : userName;
    }
    client.ws.send(JSON.stringify({
        'message': message,
        'sender': sender
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
    document.getElementById("question-list").prepend(card);
}

function setupFormEventListeners() {
    let messageInput = document.getElementById('chat-message-input');
    if (messageInput) {
        messageInput.onkeyup = function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendQuestion();
            }
        };
    }

    let postBtn = document.getElementById('post-question-btn');
    if (postBtn) {
        postBtn.onclick = function () {
            sendQuestion();
        };
    }
}

function disableFormElements() {
    const elementIds = [
        'post-question-btn',
        'anonymous-checkbox',
        'chat-message-input'
    ];

    elementIds.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.disabled = true;
        }
    });
}

client.connect();
