const { callSkiniveAPI } = require('../utils/skiniveClient');

const analyzeImage = async (req, res) => {
  const { base64Image } = req.body;

  if (!base64Image) {
    return res.status(400).json({ error: 'No image provided' });
  }

  try {
    const response = await callSkiniveAPI(base64Image);
    res.json(response);
  } catch (error) {
    console.error('Error analyzing image:', error.message);
    res.status(500).json({ error: 'Failed to analyze image' });
  }
};

module.exports = { analyzeImage };
