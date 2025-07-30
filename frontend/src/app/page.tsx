'use client';

import { useState, ChangeEvent } from 'react';

interface AnalysisResult {
  condition: string;
  confidence: number;
  recommendation: string;
}

export default function HomePage() {
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImageFile(file);
      setResult(null);
      setError(null);
    }
  };

  const handleSubmit = async () => {
    if (!imageFile) {
      setError('Please select an image first.');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('image', imageFile);

    try {
    const response = await fetch('http://localhost:3000/api/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to analyze image');
      }

      const data = await response.json();

      if (!data?.condition) {
        throw new Error('Invalid response from server.');
      }

      setResult({
        condition: data.condition,
        confidence: data.confidence,
        recommendation: data.recommendation,
      });
    } catch (err: any) {
      setError(err.message || 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-purple-700 to-indigo-900 flex flex-col items-center justify-center p-6">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
        <h1 className="text-3xl font-extrabold text-center mb-6 text-gray-800">
          AI-Powered Skin Symptom Checker
        </h1>

        <label
          htmlFor="file-upload"
          className="block mb-4 cursor-pointer border-2 border-dashed border-gray-400 rounded-md p-6 text-center hover:border-indigo-600 transition"
        >
          {imageFile ? (
            <span className="text-gray-700">{imageFile.name}</span>
          ) : (
            <span className="text-gray-400">Click to select an image or drag and drop</span>
          )}
          <input
            id="file-upload"
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="hidden"
          />
        </label>

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="w-full bg-indigo-600 text-white py-3 rounded-md font-semibold hover:bg-indigo-700 disabled:opacity-50 transition"
        >
          {loading ? 'Analyzing...' : 'Analyze Image'}
        </button>

        {error && (
          <p className="mt-4 text-red-600 font-medium text-center">{error}</p>
        )}

        {result && (
          
          <div className="mt-6 bg-gray-50 rounded-md p-4 border border-gray-200 shadow-sm text-black">
            <h2 className="text-xl font-semibold mb-2 text-purple-800">Analysis Result</h2>
            <p><strong>Condition:</strong> {result.condition}</p>
            <p><strong>Confidence:</strong> {result.confidence.toFixed(1)}%</p>
            <p><strong>Recommendation:</strong> {result.recommendation}</p>
          </div>
        )}
      </div>
    </main>
  );
}
