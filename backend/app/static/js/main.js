document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const dragZone = document.getElementById('dragZone');
    const fileInput = document.getElementById('fileInput');
    const fileDetails = document.getElementById('fileDetails');
    const fileNameText = document.getElementById('fileName');
    const fileSizeText = document.getElementById('fileSize');
    const removeFileBtn = document.getElementById('removeFileBtn');
    const submitBtn = document.getElementById('submitBtn');
    const btnSpinner = document.getElementById('btnSpinner');
    const uploadForm = document.getElementById('uploadForm');
    
    // Modal Elements
    const errorModal = document.getElementById('errorModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalMessage = document.getElementById('modalMessage');
    const closeModalBtn = document.getElementById('closeModalBtn');

    // Modal helper functions
    const showError = (title, message) => {
        if (modalTitle && modalMessage && errorModal) {
            modalTitle.textContent = title;
            modalMessage.textContent = message;
            errorModal.classList.remove('hidden');
        }
    };

    const hideError = () => {
        if (errorModal) {
            errorModal.classList.add('hidden');
        }
    };

    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', hideError);
    }
    if (errorModal) {
        errorModal.addEventListener('click', (e) => {
            if (e.target === errorModal) {
                hideError();
            }
        });
    }
    
    // Result panels
    const placeholderCard = document.getElementById('resultsPlaceholder');
    const loadingCard = document.getElementById('resultsLoading');
    const resultsDashboard = document.getElementById('resultsDashboard');
    
    // Action buttons
    const downloadPdfBtn = document.getElementById('downloadPdfBtn');
    
    let selectedFile = null;
    let parsedProfileId = null;

    // Helper: format file size
    const formatBytes = (bytes, decimals = 2) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    };

    // Helper: validate file extension
    const isValidFile = (file) => {
        if (!file) return false;
        const ext = file.name.split('.').pop().toLowerCase();
        return ['pdf'].includes(ext);
    };

    // UI Updates: Set file details
    const handleFileSelect = (file) => {
        if (!file) return;
        
        if (!isValidFile(file)) {
            showError('Invalid File Format', 'Please upload a valid PDF resume. Other formats are currently not supported.');
            clearSelection();
            return;
        }

        selectedFile = file;
        fileNameText.textContent = file.name;
        fileSizeText.textContent = formatBytes(file.size);
        
        fileDetails.classList.remove('hidden');
        submitBtn.disabled = false;
    };

    const clearSelection = () => {
        selectedFile = null;
        fileInput.value = '';
        fileDetails.classList.add('hidden');
        submitBtn.disabled = true;
    };

    // Drag and Drop Events
    ['dragenter', 'dragover'].forEach(eventName => {
        dragZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dragZone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'dragend', 'drop'].forEach(eventName => {
        dragZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dragZone.classList.remove('dragover');
        }, false);
    });

    dragZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });

    dragZone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });

    removeFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        clearSelection();
    });

    // Form submission & backend extraction call
    uploadForm.addEventListener('submit', (e) => {
        e.preventDefault();
        if (!selectedFile) return;

        // Set Loading State
        submitBtn.disabled = true;
        btnSpinner.classList.remove('hidden');
        
        placeholderCard.classList.add('hidden');
        resultsDashboard.classList.add('hidden');
        loadingCard.classList.remove('hidden');

        const formData = new FormData();
        formData.append('file', selectedFile);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || 'Server error occurred') });
            }
            return response.json();
        })
        .then(data => {
            parsedProfileId = data.id;
            renderResults(data);
            
            // Show dashboard, hide loading
            loadingCard.classList.add('hidden');
            resultsDashboard.classList.remove('hidden');
        })
        .catch(err => {
            console.error('Error parsing resume:', err);
            showError('Processing Failed', err.message || 'An unexpected error occurred while parsing the resume. Please check if the file is readable and try again.');
            
            // Reset to placeholder
            loadingCard.classList.add('hidden');
            placeholderCard.classList.remove('hidden');
        })
        .finally(() => {
            submitBtn.disabled = false;
            btnSpinner.classList.add('hidden');
        });
    });

    // Render results in dashboard cards and JSON preview
    const renderResults = (response) => {
        void response;
    };

    // Download PDF Action Trigger
    downloadPdfBtn.addEventListener('click', () => {
        if (!parsedProfileId) return;
        window.location.href = `/download_pdf?id=${parsedProfileId}`;
    });
});
