const express = require('express');
const multer = require('multer');
const fs = require('fs');
const axios = require('axios');
const cors = require('cors');
const path = require('path');

const app = express();
const port = 3000;

app.use(cors());
const upload = multer({ dest: 'uploads/' });

app.post('/api/analyze', upload.single('image'), async (req, res) => {
    console.log('Request received'); // <=== add this

  if (!req.file) {
        console.log('No image file found'); // <=== add this
    return res.status(400).json({ error: 'No image provided.' });
  }

try {
  const imagePath = path.resolve(req.file.path);
      console.log('Image path:', imagePath); // <=== add this

  const imageBuffer = fs.readFileSync(imagePath);
      console.log('Image buffer length:', imageBuffer.length); // <=== add this


  const response = await axios.post(
    'https://api-inference.huggingface.co/models/pharmapsychotic/dermatology-disease-classifier',
    imageBuffer,
    {
      headers: {
        Authorization: `Bearer ***REMOVED***`,
        'Content-Type': 'application/octet-stream',
      },
    }
  );

  console.log('Raw HF API response data:', response.data);

  fs.unlinkSync(imagePath); // Delete uploaded file after use

  if (response.data && Array.isArray(response.data) && response.data.length > 0) {
    const topResult = response.data[0];

    return res.json({
      condition: topResult.label,
      confidence: topResult.score * 100,
      recommendation: 'Please consult a dermatologist for confirmation.',
    });
  } else {
    return res.status(500).json({ error: 'Invalid response from model.' });
  }
} catch (err) {
  console.error('Error details:', err.response?.data || err.message || err);
  return res.status(500).json({ error: 'Failed to analyze image.' });
}




});

app.listen(port, () => {
  console.log(`Backend running on http://localhost:${port}`);
});
