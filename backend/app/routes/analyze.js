// routes/analyze.js
const express = require('express');
const multer = require('multer');
const { callSkiniveAPI } = require('../skiniveClient');

const router = express.Router();
const upload = multer({ limits: { fileSize: 5 * 1024 * 1024 } }); // max 5MB

router.post('/', upload.single('image'), async (req, res) => {
  try {
    const imageBuffer = req.file.buffer;
    const base64Image = imageBuffer.toString('base64');

    const result = await callSkiniveAPI(base64Image);

    res.json({ success: true, analysis: result });
  } catch (error) {
    console.error('Error analyzing image:', error.message);
    res.status(500).json({ success: false, error: 'Failed to analyze image' });
  }
});

module.exports = router;
