(function () {
  const form            = document.getElementById('input-form');
  const fileInput       = document.getElementById('image-input');
  const symptomInput    = document.getElementById('symptom-input');
  const submitBtn       = document.getElementById('submit-btn');
  const loadingElem     = document.getElementById('loading');
  const resultContainer = document.getElementById('result-container');

  function showLoading(on) {
    if (on) {
      loadingElem.classList.remove('hidden');
      submitBtn.disabled = true;
    } else {
      loadingElem.classList.add('hidden');
      submitBtn.disabled = false;
    }
  }

  function renderResults(data) {
    let html = "";

    if (data.disease) {
      const conf = typeof data.accuracy === "number"
        ? (data.accuracy <= 1 ? (data.accuracy * 100).toFixed(2) + "%" : data.accuracy.toFixed(2) + "%")
        : "—";
      html += `<p><strong>Disease:</strong> ${data.disease}</p>`;
      html += `<p><strong>Confidence:</strong> ${conf}</p>`;
    }

    if (data.medicine) {
      html += `<p><strong>Suggested medicine:</strong> ${data.medicine}</p>`;
    }

    if (data.symptom_analysis) {
      html += `<hr><p><strong>Explanation (MedGemma):</strong></p><div>${data.symptom_analysis}</div>`;
    }

    if (!html) {
      html = "<p>No information available.</p>";
    }

    resultContainer.innerHTML = html;
    resultContainer.classList.remove('hidden');
  }

  function renderError(message) {
    resultContainer.innerHTML = `<p style="color:red;"><strong>Error:</strong> ${message}</p>`;
    resultContainer.classList.remove('hidden');
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const file = fileInput.files[0];
    const symptom = symptomInput.value || "";

    if (!file) {
      renderError("Please select an image.");
      return;
    }

    const formData = new FormData();

    formData.append('file', file);
    formData.append('symptom', symptom);

    resultContainer.classList.add('hidden');
    resultContainer.innerHTML = "";
    showLoading(true);

    try {
      const res = await fetch('/detect', { method: 'POST', body: formData });
      const raw = await res.text(); 

      if (!res.ok) {
        try {
          const err = JSON.parse(raw);
          renderError(err.message || `HTTP ${res.status}`);
        } catch {
          renderError(`HTTP ${res.status}: ${raw}`);
        }
        return;
      }

      let data;
      try {
        data = JSON.parse(raw);
      } catch {
        renderError("Server returned invalid JSON.");
        return;
      }

      renderResults(data);
    } catch (err) {
      renderError(`Network error: ${err.message}`);
    } finally {
      showLoading(false);
    }
  });
})();
