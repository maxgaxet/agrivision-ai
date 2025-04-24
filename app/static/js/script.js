document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const submitBtn = document.getElementById('submit-btn');
    const loadingSpinner = document.getElementById('loading');
    const resultContainer = document.getElementById('result-container');
    const resultLabel = document.getElementById('result-label');
    const resultConfidence = document.getElementById('result-confidence');
    const resultImage = document.getElementById('result-image');
    
    const previewContainer = document.getElementById('image-preview-container');
    const previewImage = document.getElementById('image-preview');
  
    // Show image preview when file is selected
    fileInput.addEventListener('change', () => {
      const file = fileInput.files[0];
      if (file) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
          previewImage.src = e.target.result; // Set the preview image source
          previewContainer.style.display = 'block'; // Show the preview container
        };
        
        reader.readAsDataURL(file);
      } else {
        previewContainer.style.display = 'none'; // Hide if no file is selected
      }
    });
  
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
  
      const file = fileInput.files[0];
      if (!file) return;
  
      // UI updates
      submitBtn.disabled = true;
      loadingSpinner.style.display = 'block';
      resultContainer.style.display = 'none';
  
      const formData = new FormData();
      formData.append('file', file);
  
      try {
        const res = await fetch('/predict', {
          method: 'POST',
          body: formData
        });
  
        const data = await res.json();
        loadingSpinner.style.display = 'none';
        submitBtn.disabled = false;
  
        if (data.prediction) {
          resultLabel.textContent = `🧠 Prediction: ${data.prediction}`;
          resultConfidence.textContent = parseFloat(data.confidence).toFixed(2);
          resultImage.src = data.img_path;
          resultContainer.style.display = 'block';
        } else {
          alert('Error: ' + (data.error || 'Unknown error'));
        }
      } catch (err) {
        loadingSpinner.style.display = 'none';
        submitBtn.disabled = false;
        alert('An error occurred. Please try again.');
      }
    });
  
    window.resetForm = () => {
      form.reset();
      fileInput.value = '';
      previewContainer.style.display = 'none'; // Hide preview on reset
      resultContainer.style.display = 'none';
    };
  });
  