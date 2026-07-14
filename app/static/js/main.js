// KrishiSahay AI Frontend Interactions

document.addEventListener('DOMContentLoaded', function() {
    
    // Auto-dismiss alert boxes after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            // Check if bootstrap alert object exists and close it
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 6000);
    });

    // Handle Drag and Drop for Upload Portal
    const dropzone = document.getElementById('uploadDropzone');
    const fileInput = document.getElementById('documentFileInput');
    
    if (dropzone && fileInput) {
        // Trigger file input dialog on click
        dropzone.addEventListener('click', () => fileInput.click());

        // Highlight drop zone on drag over
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropzone.style.borderColor = '#2e7d32';
                dropzone.style.backgroundColor = '#e8f5e9';
            }, false);
        });

        // Remove highlights when dragging away
        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropzone.style.borderColor = '#8d6e63';
                dropzone.style.backgroundColor = '#ffffff';
            }, false);
        });

        // Handle file drop
        dropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                fileInput.files = files;
                updateDropzoneLabel(files[0].name);
            }
        });

        // Update name label when file selected manually
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                updateDropzoneLabel(fileInput.files[0].name);
            }
        });
    }

    function updateDropzoneLabel(fileName) {
        const textLabel = document.getElementById('dropzoneText');
        const iconLabel = document.getElementById('dropzoneIcon');
        const uploadForm = document.getElementById('uploadForm');
        
        if (textLabel) {
            textLabel.innerHTML = `<strong class="text-success">Selected File:</strong> ${fileName}<br><span class="text-muted">Click or drop another file to replace, or tap the Upload button.</span>`;
        }
        if (iconLabel) {
            iconLabel.className = 'fas fa-file-check text-success fa-3x mb-3';
        }
        
        // Show upload button/loader wrapper
        const actionWrapper = document.getElementById('uploadActionWrapper');
        if (actionWrapper) {
            actionWrapper.classList.remove('d-none');
        }
    }

    // Dynamic crops list formatting in registration (capitalizing input tokens)
    const cropInput = document.getElementById('crop_type');
    if (cropInput) {
        cropInput.addEventListener('blur', function() {
            const val = cropInput.value;
            if (val) {
                const formatted = val.split(',')
                                     .map(s => s.trim())
                                     .filter(s => s.length > 0)
                                     .join(', ');
                cropInput.value = formatted;
            }
        });
    }

    // Front-end registration forms checks
    const regForm = document.getElementById('registrationForm');
    if (regForm) {
        regForm.addEventListener('submit', function(e) {
            const age = parseInt(document.getElementById('age').value);
            const land = parseFloat(document.getElementById('land_size').value);
            const income = parseFloat(document.getElementById('annual_income').value);
            const mobile = document.getElementById('mobile_number').value;
            
            let validationFailed = false;
            let errorMsg = "";

            if (isNaN(age) || age < 18 || age > 110) {
                errorMsg = "Age must be at least 18 to register.";
                validationFailed = true;
            } else if (isNaN(land) || land < 0) {
                errorMsg = "Land size cannot be negative.";
                validationFailed = true;
            } else if (isNaN(income) || income < 0) {
                errorMsg = "Annual income cannot be negative.";
                validationFailed = true;
            } else if (!/^[0-9]{10,12}$/.test(mobile.replace(/[\s-+]/g, ''))) {
                errorMsg = "Please enter a valid 10-digit mobile number.";
                validationFailed = true;
            }

            if (validationFailed) {
                e.preventDefault();
                
                // Show visual validation alert
                const alertContainer = document.getElementById('validationAlertContainer');
                if (alertContainer) {
                    alertContainer.innerHTML = `
                        <div class="alert alert-danger alert-dismissible fade show" role="alert">
                            <i class="fas fa-exclamation-triangle me-2"></i> ${errorMsg}
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        </div>
                    `;
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                } else {
                    alert(errorMsg);
                }
            }
        });
    }
});

// Start simulated file scanning loading feedback
function startUploadLoader() {
    const uploadBtn = document.getElementById('uploadSubmitBtn');
    const spinner = document.getElementById('uploadSpinner');
    
    if (uploadBtn) {
        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Uploading File...';
    }
    if (spinner) {
        spinner.classList.remove('d-none');
    }
}
