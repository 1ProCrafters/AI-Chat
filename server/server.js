const express = require('express');
const fs = require('fs').promises;
const path = require('path');
const app = express();

app.use(express.json());
app.use(express.static('public')); // Serve your HTML file from here

const CONVERSATIONS_DIR = path.join(__dirname, 'conversations');

// Ensure conversations directory exists
async function ensureConversationsDir() {
    try {
        await fs.mkdir(CONVERSATIONS_DIR, { recursive: true });
    } catch (error) {
        console.error('Error creating conversations directory:', error);
    }
}

// List all conversations
app.get('/list-conversations', async (req, res) => {
    try {
        await ensureConversationsDir();
        const files = await fs.readdir(CONVERSATIONS_DIR);
        const conversations = await Promise.all(
            files.map(async (file) => {
                const content = await fs.readFile(
                    path.join(CONVERSATIONS_DIR, file),
                    'utf-8'
                );
                return JSON.parse(content);
            })
        );
        res.json(conversations);
    } catch (error) {
        console.error('Error listing conversations:', error);
        res.status(500).json({ error: 'Failed to list conversations' });
    }
});

// Save conversation
app.post('/save-conversation', async (req, res) => {
    try {
        await ensureConversationsDir();
        const conversation = req.body;
        await fs.writeFile(
            path.join(CONVERSATIONS_DIR, `${conversation.id}.json`),
            JSON.stringify(conversation, null, 2)
        );
        res.json({ success: true });
    } catch (error) {
        console.error('Error saving conversation:', error);
        res.status(500).json({ error: 'Failed to save conversation' });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});