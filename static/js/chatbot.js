console.log("Chatbot JS loaded");

const sendBtn = document.getElementById("sendBtn");
const userInput = document.getElementById("userInput");
const chatBody = document.getElementById("chatBody");

function addMessage(text, type) {
    if (!chatBody) return;

    const div = document.createElement("div");
    div.className = "message " + type;

    div.innerHTML = `
        <div class="bubble">
            ${text}
        </div>
    `;

    chatBody.appendChild(div);
    chatBody.scrollTop = chatBody.scrollHeight;
}

async function sendMessage() {
    if (!userInput) return;

    const message = userInput.value.trim();
    if (message === "") return;

    // Show user message
    addMessage(message, "user-message");
    userInput.value = "";

    // Typing indicator
    const typing = document.createElement("div");
    typing.className = "message ai-message";
    typing.id = "typing";
    typing.innerHTML = `
        <div class="bubble typing">
            AI is typing...
        </div>
    `;

    chatBody.appendChild(typing);
    chatBody.scrollTop = chatBody.scrollHeight;

    try {
        const csrfTokenElement = document.querySelector("[name=csrfmiddlewaretoken]");
        const csrfToken = csrfTokenElement ? csrfTokenElement.value : "";

        const response = await fetch("/chatbot/api/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({
                message: message
            })
        });

        const data = await response.json();

        const typingBox = document.getElementById("typing");
        if (typingBox) {
            typingBox.remove();
        }

        addMessage(data.reply, "ai-message");

    } catch (error) {
        console.error("Chatbot Error:", error);

        const typingBox = document.getElementById("typing");
        if (typingBox) {
            typingBox.remove();
        }

        addMessage("Connection issue. Please try again.", "ai-message");
    }
}

// Button click
if (sendBtn) {
    sendBtn.addEventListener("click", sendMessage);
}

// Enter key
if (userInput) {
    userInput.addEventListener("keypress", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            sendMessage();
        }
    });
}

// Floating Chat Open / Close
const chatToggle = document.getElementById("chatToggle");
const chatContainer = document.getElementById("chatContainer");
const closeChat = document.getElementById("closeChat");

if (chatToggle && chatContainer) {
    chatToggle.addEventListener("click", function () {
        chatContainer.classList.add("active");
        chatToggle.style.display = "none";
    });
}

if (closeChat && chatContainer && chatToggle) {
    closeChat.addEventListener("click", function () {
        chatContainer.classList.remove("active");
        chatToggle.style.display = "flex";
    });
}