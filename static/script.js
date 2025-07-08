document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("qaForm");
    const chat = document.getElementById("chat");
    const questionInput = document.getElementById("question");
    const imageInput = document.getElementById("imageInput");
    const imagePreview = document.getElementById("imagePreview");
    const submitButton = form.querySelector("button");

    // Show preview of uploaded image
    imageInput.addEventListener("change", () => {
        const file = imageInput.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                imagePreview.innerHTML = `<img src="${event.target.result}" class="preview-img" />`;
            };
            reader.readAsDataURL(file);
        }
    });

    // Handle form submission
    form.onsubmit = async (e) => {
        e.preventDefault();

        const imageFile = imageInput.files[0];
        const question = questionInput.value.trim();

        if (!imageFile || !question) {
            alert("Please upload an image and enter a question.");
            return;
        }

        appendMessage("🧑", question, "user");

        submitButton.disabled = true;
        showTyping();

        const formData = new FormData();
        formData.append("image", imageFile);
        formData.append("question", question);

        try {
            const response = await fetch("/ask", {
                method: "POST",
                body: formData
            });

            const data = await response.json();
            removeTyping();

            const answer = data.answer || "🤖: Sorry, I couldn't generate a response.";
            appendMessage("🤖", answer, "bot");
        } catch (error) {
            removeTyping();
            appendMessage("🤖", "An error occurred. Please try again.", "bot");
            console.error("Fetch error:", error);
        }

        submitButton.disabled = false;
        questionInput.value = "";
    };

    // Add a chat bubble
    function appendMessage(senderIcon, text, className) {
        const bubble = document.createElement("div");
        bubble.className = `chat-bubble ${className}`;
        bubble.innerHTML = `<strong>${senderIcon}</strong>: ${text}`;
        chat.appendChild(bubble);
        chat.scrollTop = chat.scrollHeight;
    }

    // Show typing animation
    function showTyping() {
        const typing = document.createElement("div");
        typing.id = "typingIndicator";
        typing.className = "chat-bubble bot";
        typing.textContent = "🤖 Typing...";
        chat.appendChild(typing);
        chat.scrollTop = chat.scrollHeight;
    }

    // Remove typing animation
    function removeTyping() {
        const typing = document.getElementById("typingIndicator");
        if (typing) typing.remove();
    }
});
