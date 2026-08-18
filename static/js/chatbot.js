console.log("Chatbot JS loaded");

function formatMarkdown(text) {
    if (!text) return "";

    let formatted = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

    // Strip all raw asterisks (**) to prevent raw star text
    formatted = formatted.replace(/\*\*/g, "").replace(/\*/g, "");

    const lines = formatted.split("\n");
    let htmlLines = [];

    lines.forEach(line => {
        const trimmed = line.trim();
        if (trimmed === "") return;

        if (/^\d+\.\s+/.test(trimmed)) {
            const itemText = trimmed.replace(/^\d+\.\s+/, "");
            htmlLines.push(`<div style="margin:4px 0 4px 6px;line-height:1.6;font-size:13.5px;"><span style="font-weight:700;color:#2563eb;margin-right:6px;">&bull;</span>${itemText}</div>`);
        } else if (trimmed.startsWith("- ") || trimmed.startsWith("• ")) {
            const itemText = trimmed.replace(/^[-•]\s*/, "");
            htmlLines.push(`<div style="margin:4px 0 4px 10px;line-height:1.6;font-size:13.5px;"><span style="font-weight:700;color:#475569;margin-right:6px;">-</span>${itemText}</div>`);
        } else if (trimmed.endsWith(":") && trimmed.length < 45) {
            htmlLines.push(`<div style="font-weight:800;color:#0f172a;margin:10px 0 4px;font-size:13.5px;letter-spacing:0.3px;">${trimmed}</div>`);
        } else {
            htmlLines.push(`<p style="margin:0 0 6px;line-height:1.65;font-size:13.5px;color:#334155;">${trimmed}</p>`);
        }
    });

    return htmlLines.join("");
}

function addMessage(text, type) {
    const chatBody = document.getElementById("chatBody");
    if (!chatBody) return;

    const div = document.createElement("div");
    div.className = "message " + type;
    const formattedContent = formatMarkdown(text);

    div.innerHTML = `<div class="bubble">${formattedContent}</div>`;
    chatBody.appendChild(div);
    chatBody.scrollTop = chatBody.scrollHeight;
}

async function sendMessage(overrideMessage = null) {
    const userInput = document.getElementById("userInput");
    const chatBody = document.getElementById("chatBody");

    const message = overrideMessage ? overrideMessage : (userInput ? userInput.value.trim() : "");
    if (message === "") return;

    if (!overrideMessage && userInput) {
        addMessage(message, "user-message");
        userInput.value = "";
    } else if (overrideMessage) {
        addMessage(overrideMessage, "user-message");
    }

    if (chatBody) {
        const typing = document.createElement("div");
        typing.className = "message ai-message";
        typing.id = "typing";
        typing.innerHTML = `<div class="bubble typing" style="font-size:12px;color:#64748b;">Assistant is typing...</div>`;
        chatBody.appendChild(typing);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

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
        if (typingBox) typingBox.remove();

        addMessage(data.reply, "ai-message");

    } catch (error) {
        console.error("Chatbot Error:", error);
        const typingBox = document.getElementById("typing");
        if (typingBox) typingBox.remove();
        addMessage("Connection issue. Please try again.", "ai-message");
    }
}

// Global Event Delegation (100% Reliable Click Binding)
document.addEventListener("click", function (e) {
    // 1. Floating Toggle Button
    if (e.target.closest("#chatToggle")) {
        const chatContainer = document.getElementById("chatContainer");
        const chatToggle = document.getElementById("chatToggle");
        if (chatContainer) chatContainer.classList.add("active");
        if (chatToggle) chatToggle.style.display = "none";
        return;
    }

    // 2. Close Chat Button
    if (e.target.closest("#closeChat")) {
        const chatContainer = document.getElementById("chatContainer");
        const chatToggle = document.getElementById("chatToggle");
        if (chatContainer) chatContainer.classList.remove("active");
        if (chatToggle) chatToggle.style.display = "flex";
        return;
    }

    // 3. Send Button
    if (e.target.closest("#sendBtn")) {
        sendMessage();
        return;
    }

    // 4. Quick Chips Click
    const chipBtn = e.target.closest(".chip-btn");
    if (chipBtn) {
        const prompt = chipBtn.dataset.prompt;
        if (prompt) {
            const userInput = document.getElementById("userInput");
            if (userInput) userInput.value = prompt;
            sendMessage(prompt);
        }
        return;
    }
});

// Keypress Listener for Input
document.addEventListener("keypress", function (e) {
    if (e.key === "Enter" && e.target && e.target.id === "userInput") {
        e.preventDefault();
        sendMessage();
    }
});