console.log("Chatbot JS loaded");

const sendBtn = document.getElementById("sendBtn");
const userInput = document.getElementById("userInput");
const chatBody = document.getElementById("chatBody");

console.log("Send Button:", sendBtn);


function addMessage(text, type) {

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

    console.log("Send button clicked");


    const message = userInput.value.trim();


    if (message === "") {
        return;
    }


    // Show user message
    addMessage(message, "user-message");


    userInput.value = "";


    // Typing message
    const typing = document.createElement("div");

    typing.className = "message ai-message";
    typing.id = "typing";

    typing.innerHTML = `
        <div class="bubble">
            🤖 AI is typing...
        </div>
    `;


    chatBody.appendChild(typing);


    try {


        const csrfToken = document.querySelector(
            "[name=csrfmiddlewaretoken]"
        ).value;



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



        document.getElementById("typing").remove();



        addMessage(
            "🤖 " + data.reply,
            "ai-message"
        );



    } catch(error) {


        console.log(error);


        const typingBox = document.getElementById("typing");

        if(typingBox){
            typingBox.remove();
        }


        addMessage(
            "❌ Server se connection nahi ho saka.",
            "ai-message"
        );

    }

}




// Button click

if(sendBtn){

    sendBtn.addEventListener(
        "click",
        sendMessage
    );

}



// Enter key

if(userInput){

    userInput.addEventListener(
        "keypress",
        function(e){

            if(e.key === "Enter"){

                sendMessage();

            }

        }
    );

}
// =============================
// Floating Chat Open / Close
// =============================

const chatToggle = document.getElementById("chatToggle");
const chatContainer = document.getElementById("chatContainer");
const closeChat = document.getElementById("closeChat");

if(chatToggle){

    chatToggle.addEventListener("click", function(){

        chatContainer.classList.add("active");

        chatToggle.style.display = "none";

    });

}

if(closeChat){

    closeChat.addEventListener("click", function(){

        chatContainer.classList.remove("active");

        chatToggle.style.display = "block";

    });

}