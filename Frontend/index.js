const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const chatMessages = document.getElementById('chat-messages');

// Function to add a message to the chat
function addMessage(content, role) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;

    const messageContainer = document.createElement('div');
    messageContainer.className = 'message-container';

    messageContainer.innerHTML = `
                <div class="message-role">${role === 'user' ? 'You' : 'Assistant'}</div>
                <div class="message-content">${content}</div>
            `;

    messageDiv.appendChild(messageContainer);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Function to handle sending a message
function sendMessage() {
    const message = messageInput.value.trim();
    if (message) {
        // Add user message
        addMessage(message, 'user');

        // Simulate AI response (replace this with actual AI integration)
        setTimeout(() => {
            const aiResponse = `This is a simulated response to: "${message}"`;
            addMessage(aiResponse, 'assistant');
        }, 500);

        // Clear input
        messageInput.value = '';
        messageInput.style.height = '24px';
    }
}

// Auto-expand textarea
messageInput.addEventListener('input', function () {
    this.style.height = '24px';
    this.style.height = (this.scrollHeight) + 'px';
});

// Send message on button click
sendButton.addEventListener('click', sendMessage);

// Send message on Enter (but new line on Shift+Enter)
messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});