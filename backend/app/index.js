require('dotenv').config({ path: '../.env' }); // Load .env from one level up

const express = require('express');
const app = express();

const PORT = process.env.PORT || 3000;
const API_KEY = process.env.SKINIVE_API_KEY;

app.get('/', (req, res) => {
  res.send(`Your API key is: ${API_KEY}`);
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
