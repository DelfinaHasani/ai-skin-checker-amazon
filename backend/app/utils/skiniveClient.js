// skiniveClient.js

// This mock version simulates a response from the Skinive API.
// Replace this code with the real API request once you have the actual API key.

const callSkiniveAPI = async (base64Image) => {
  // Simulate network delay
  await new Promise((res) => setTimeout(res, 1000));

  // Return mock analysis result
  return {
    status: 'success',
    result: {
      diagnosis: 'Benign mole',
      confidence: '92%',
      recommendation: 'Monitor regularly. No treatment needed unless changes occur.',
    },
  };
};

module.exports = { callSkiniveAPI };
