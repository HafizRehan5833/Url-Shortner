// Function to copy the shortened URL to clipboard
function copyToClipboard() {
  const shortUrlInput = document.getElementById('short-url');
  const copyButton = document.getElementById('copy-button');
  
  // Select the text
  shortUrlInput.select();
  shortUrlInput.setSelectionRange(0, 99999); // For mobile devices
  
  // Copy the text
  navigator.clipboard.writeText(shortUrlInput.value)
    .then(() => {
      // Update button text temporarily to indicate success
      const originalButtonText = copyButton.innerHTML;
      copyButton.innerHTML = '<i class="fas fa-check me-1"></i>Copied!';
      copyButton.classList.remove('btn-secondary');
      copyButton.classList.add('btn-success');
      
      // Reset button after 2 seconds
      setTimeout(() => {
        copyButton.innerHTML = originalButtonText;
        copyButton.classList.remove('btn-success');
        copyButton.classList.add('btn-secondary');
      }, 2000);
    })
    .catch(err => {
      console.error('Failed to copy text: ', err);
      alert('Failed to copy to clipboard. Please copy manually.');
    });
}

// Add event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Show tooltip on hover for the copy button
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function(tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Form submission handling
  const urlForm = document.getElementById('url-form');
  if (urlForm) {
    urlForm.addEventListener('submit', function(event) {
      const urlInput = document.getElementById('url');
      
      // Simple URL validation
      if (!isValidUrl(urlInput.value)) {
        event.preventDefault();
        showError('Please enter a valid URL including http:// or https://');
        return false;
      }
    });
  }
});

// URL validation helper function
function isValidUrl(string) {
  try {
    new URL(string);
    return true;
  } catch (_) {
    return false;
  }
}

// Error display helper function
function showError(message) {
  // Remove any existing error messages
  const existingAlert = document.querySelector('.alert-danger');
  if (existingAlert) {
    existingAlert.remove();
  }
  
  // Create new error message
  const errorDiv = document.createElement('div');
  errorDiv.className = 'alert alert-danger mt-3';
  errorDiv.role = 'alert';
  errorDiv.innerText = message;
  
  // Insert after the input group
  const inputGroup = document.querySelector('.input-group');
  inputGroup.parentNode.insertBefore(errorDiv, inputGroup.nextSibling);
}
