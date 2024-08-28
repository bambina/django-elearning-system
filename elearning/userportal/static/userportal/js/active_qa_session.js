const roomName = JSON.parse(document.getElementById("room-name").textContent);
const courseId = JSON.parse(document.getElementById("course-id").textContent);
const userName = JSON.parse(document.getElementById("user-name").textContent);
const hostName = JSON.parse(document.getElementById("host-name").textContent);
const isInstructor = JSON.parse(
  document.getElementById("is-instructor").textContent
);
const url = `ws://${hostName}/ws/course/${courseId}/live-qa-session/${roomName}/`;
const MESSAGE_TYPE_CLOSE = "close.connection";
const MESSAGE_TYPE_QUESTION = "question.message";
const MESSAGE_TYPE_QUESTION_LIST = "question.list";
const SESSION_TERMINATE_CODE = 4000;
const UNAUTHORIZED_ACCESS_CODE = 4001;
const MAX_RETRIES = 3;
const RECONNECT_INTERVAL = 1000 * 5;
const TOAST_DELAY = 5000;

class WebSocketClient {
  constructor(url) {
    this.url = url;
    this.ws = null;
    this.maxRetries = MAX_RETRIES;
    this.autoReconnectInterval = RECONNECT_INTERVAL;
    this.messageHandlers = new Map();
    this.toast = null;
    this.toastBody = null;
    this.initStatusToast();
  }

  connect() {
    this.ws = new WebSocket(this.url);
    this.ws.onopen = () => {
      if (this.maxRetries !== MAX_RETRIES) {
        this.showConnectionStatus("WebSocket connection restored.");
      }
      this.maxRetries = MAX_RETRIES;
      this.triggerHandler("open");
    };
    this.ws.onclose = (e) => {
      if (
        e.code === SESSION_TERMINATE_CODE ||
        e.code === UNAUTHORIZED_ACCESS_CODE
      ) {
        toggleFormElements(true);
      } else {
        if (!e.wasClean) {
          this.reconnect();
        }
      }
    };
    this.ws.onerror = (e) => {
      console.error("WebSocket error:", e);
      this.ws.close();
    };
    this.ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      this.triggerHandler("message", data);
    };
  }

  reconnect() {
    if (this.maxRetries > 0) {
      this.showConnectionStatus("WebSocket connection lost. Reconnecting...");
      setTimeout(() => {
        this.connect();
        this.maxRetries--;
      }, this.autoReconnectInterval);
    } else {
      this.showConnectionStatus(
        "WebSocket connection has been lost. Please try accessing from the course details page again, or wait a while before retrying."
      );
    }
  }

  send(message, sender) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          message: message,
          sender: sender,
        })
      );
    } else {
      this.showConnectionStatus("WebSocket connection is not open.");
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

  initStatusToast() {
    const toastEl = document.getElementById("status_toast");
    const toastBody = toastEl.querySelector(".toast-body");
    if (!toastEl || !toastBody) {
      return;
    }
    this.toast = new bootstrap.Toast(toastEl, {
      delay: TOAST_DELAY,
    });
    this.toastBody = toastBody;
  }

  showConnectionStatus(status) {
    if (this.toast && this.toastBody) {
      this.toastBody.textContent = status;
      this.toast.show();
    }
  }
}

const client = new WebSocketClient(url);

client.addHandler("open", () => {
  setupFormEventListeners();
  toggleFormElements(false);
});

client.addHandler("message", (data) => {
  if (data.type === MESSAGE_TYPE_CLOSE) {
    handleSessionEnd(data);
  } else if (data.type === MESSAGE_TYPE_QUESTION_LIST) {
    handleQuestionList(data.questions);
  } else if (data.type === MESSAGE_TYPE_QUESTION) {
    // Normal message
    createCard(data);
  }
});

function handleSessionEnd(data) {
  toggleFormElements(true);
  createCard(data);
}

function handleQuestionList(questions) {
  const questionList = document.getElementById("question-list");
  if (!questionList) {
    return;
  }
  questionList.innerHTML = "";
  questions.forEach(createCard);
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
  sender.textContent = question.sender || "Anonymous";
  cardBody.appendChild(sender);
  // Add the timestamp
  var timeStamp = document.createElement("p");
  timeStamp.className = "text-muted small";
  var options = { hour: "2-digit", minute: "2-digit" };
  timeStamp.textContent = `Posted on ${new Date(
    question.timestamp
  ).toLocaleTimeString([], options)}`;
  cardBody.appendChild(timeStamp);
  // Add the question message
  var newPost = document.createElement("p");
  newPost.className = "card-text";
  newPost.innerHTML = question.message.replace(/\n/g, "<br>");
  cardBody.appendChild(newPost);
  document.getElementById("question-list").prepend(card);
}

function sendMessage() {
  const messageInputDom = document.getElementById("message_input");
  const message = messageInputDom.value;
  let sender = userName;
  const anonymousCheckboxDom = document.getElementById("anonymous_checkbox");
  if (anonymousCheckboxDom && anonymousCheckboxDom.checked) {
    sender = "";
  }
  client.send(message, sender);
  messageInputDom.value = "";
}

function setupFormEventListeners() {
  let messageInput = document.getElementById("message_input");
  if (messageInput) {
    messageInput.onkeyup = function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    };
  }

  let postBtn = document.getElementById("post_question_btn");
  if (postBtn) {
    postBtn.onclick = function () {
      sendMessage();
    };
  }
}

function toggleFormElements(disable) {
  const elementIds = [
    "post_question_btn",
    "anonymous_checkbox",
    "message_input",
  ];

  elementIds.forEach((id) => {
    const element = document.getElementById(id);
    if (element) {
      element.disabled = disable;
    }
  });
}

client.connect();
