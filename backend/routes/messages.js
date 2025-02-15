const express = require('express');
const mongoose = require('mongoose');
const router = express.Router();

// Define a Message schema
const messageSchema = new mongoose.Schema({
  text: {
    type: String,
    required: true,
  },
});

// Create a Message model
const Message = mongoose.model('Message', messageSchema);

// Get all messages
router.get('/', async (req, res) => {
  try {
    const messages = await Message.find();
    res.json(messages);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Post a new message
router.post('/', async (req, res) => {
  const { text } = req.body;
  if (!text) {
    return res.status(400).json({ error: 'Text is required' });
  }

  try {
    const message = new Message({ text });
    await message.save();
    res.status(201).json(message);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
