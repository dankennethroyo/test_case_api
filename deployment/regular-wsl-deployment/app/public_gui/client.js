// Public Client Interface JavaScript
const API_BASE = window.location.origin;
let currentResults = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    setupEventListeners();
    setupDragDrop();
});

// Tab management
function initializeTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.dataset.tab;
            
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanels.forEach(p => p.classList.remove('active'));
            
            btn.classList.add('active');
            document.getElementById(target).classList.add('active');
        });
    });
}

// Setup event listeners
function setupEventListeners() {
    // Single form submit
    document.getElementById('singleForm').addEventListener('submit', handleSingleSubmit);
    
    // Batch form submit
    document.getElementById('batchForm').addEventListener('submit', handleBatchSubmit);
    
    // File browse button
    document.getElementById('browseBtn').addEventListener('click', () => {
        document.getElementById('fileInput').click();
    });
    
    // File input change
    document.getElementById('fileInput').addEventListener('change', handleFileSelect);
    
    // Remove file button
    document.getElementById('removeFile').addEventListener('click', clearFileSelection);
    
    // Result actions
    document.getElementById('copyBtn').addEventListener('click', copyResults);
    document.getElementById('downloadBtn').addEventListener('click', () => downloadResults('json'));
    document.getElementById('downloadTxtBtn').addEventListener('click', () => downloadResults('txt'));
    document.getElementById('clearBtn').addEventListener('click', clearResults);
}

// Setup drag and drop
function setupDragDrop() {
    const dropZone = document.getElementById('dropZone');
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect({ target: { files } });
        }
    });
    
    dropZone.addEventListener('click', () => {
        document.getElementById('fileInput').click();
    });
}

// Handle single requirement submission
async function handleSingleSubmit(e) {
    e.preventDefault();
    
    const requirementId = document.getElementById('requirementId').value.trim();
    const description = document.getElementById('description').value.trim();
    const category = document.getElementById('category').value;
    const parameterCategory = document.getElementById('parameterCategory').value.trim();
    const verificationPlan = document.getElementById('verificationPlan').value.trim();
    
    const requirement = {
        REQUIREMENTS_ID: requirementId,
        DESCRIPTION: description,
        CATEGORY: category
    };
    
    if (parameterCategory) {
        requirement.PARAMETER_CATEGORY = parameterCategory;
    }
    
    if (verificationPlan) {
        requirement.VERIFICATION_PLAN = verificationPlan;
    }
    
    showProgress('Generating Test Case...', 'Please wait while AI generates your test case');
    
    try {
        const response = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requirement)
        });
        
        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }
        
        const result = await response.json();
        currentResults = [result];
        displayResults([result], 1, 1);
        
    } catch (error) {
        hideProgress();
        showError('Failed to generate test case', error.message);
    }
}

// Handle batch file submission
async function handleBatchSubmit(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('fileInput');
    if (!fileInput.files.length) {
        showError('No file selected', 'Please select a JSON file to upload');
        return;
    }
    
    const file = fileInput.files[0];
    
    // Validate file type
    if (!file.name.endsWith('.json')) {
        showError('Invalid file type', 'Please upload a JSON file');
        return;
    }
    
    // Validate file size (10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
        showError('File too large', 'Maximum file size is 10MB');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    showProgress('Processing File...', `Uploading and processing ${file.name}`);
    
    try {
        const response = await fetch(`${API_BASE}/generate/file`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.results && result.results.length > 0) {
            const successfulResults = result.results
                .filter(r => r.status === 'success')
                .map(r => r.data);
            
            currentResults = successfulResults;
            displayResults(successfulResults, result.successful, result.total);
        } else {
            throw new Error('No results returned');
        }
        
    } catch (error) {
        hideProgress();
        showError('Failed to process file', error.message);
    }
}

// Handle file selection
function handleFileSelect(e) {
    const files = e.target.files;
    
    if (files.length > 0) {
        const file = files[0];
        document.getElementById('fileName').textContent = `📄 ${file.name} (${formatFileSize(file.size)})`;
        document.getElementById('fileInfo').style.display = 'flex';
        document.getElementById('uploadBtn').disabled = false;
    }
}

// Clear file selection
function clearFileSelection() {
    document.getElementById('fileInput').value = '';
    document.getElementById('fileInfo').style.display = 'none';
    document.getElementById('uploadBtn').disabled = true;
}

// Format file size
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

// Display results
function displayResults(results, successful, total) {
    hideProgress();
    
    const section = document.getElementById('resultsSection');
    const statsDiv = document.getElementById('resultsStats');
    const contentDiv = document.getElementById('resultsContent');
    
    // Display statistics
    statsDiv.innerHTML = `
        <div class="stat-box">
            <div class="stat-value">${total}</div>
            <div class="stat-label">Total Processed</div>
        </div>
        <div class="stat-box">
            <div class="stat-value" style="color: var(--success)">${successful}</div>
            <div class="stat-label">Successful</div>
        </div>
        <div class="stat-box">
            <div class="stat-value" style="color: var(--danger)">${total - successful}</div>
            <div class="stat-label">Failed</div>
        </div>
    `;
    
    // Display results
    if (results.length === 1) {
        // Single result - show formatted
        const result = results[0];
        contentDiv.innerHTML = `
            <div class="test-case-card">
                <div class="test-case-header">
                    <div class="test-case-id">${result.REQUIREMENTS_ID || 'N/A'}</div>
                    <span class="test-case-category">${result.CATEGORY || 'N/A'}</span>
                </div>
                <div class="test-case-content">${result.Test_Case || 'No test case generated'}</div>
            </div>
        `;
    } else {
        // Multiple results - show JSON
        contentDiv.textContent = JSON.stringify(results, null, 2);
    }
    
    section.style.display = 'block';
    section.scrollIntoView({ behavior: 'smooth' });
}

// Show progress overlay
function showProgress(title, message) {
    const overlay = document.getElementById('progressOverlay');
    document.getElementById('progressTitle').textContent = title;
    document.getElementById('progressStatus').textContent = message;
    overlay.style.display = 'flex';
    
    // Disable form buttons
    document.getElementById('generateBtn').disabled = true;
    document.getElementById('uploadBtn').disabled = true;
}

// Hide progress overlay
function hideProgress() {
    document.getElementById('progressOverlay').style.display = 'none';
    
    // Re-enable form buttons
    document.getElementById('generateBtn').disabled = false;
    const fileInput = document.getElementById('fileInput');
    if (fileInput.files.length > 0) {
        document.getElementById('uploadBtn').disabled = false;
    }
}

// Copy results to clipboard
function copyResults() {
    if (!currentResults) return;
    
    const text = JSON.stringify(currentResults, null, 2);
    navigator.clipboard.writeText(text).then(() => {
        showSuccess('Copied to clipboard!');
    }).catch(() => {
        showError('Failed to copy', 'Could not copy to clipboard');
    });
}

// Download results
function downloadResults(format) {
    if (!currentResults) return;
    
    let content, filename, mimeType;
    
    if (format === 'json') {
        content = JSON.stringify(currentResults, null, 2);
        filename = `test_cases_${Date.now()}.json`;
        mimeType = 'application/json';
    } else {
        content = currentResults.map(r => {
            return `
${'='.repeat(80)}
Requirement ID: ${r.REQUIREMENTS_ID || 'N/A'}
Category: ${r.CATEGORY || 'N/A'}
Generated: ${r.Generated_At || 'N/A'}
${'='.repeat(80)}

${r.Test_Case || 'No test case'}

`;
        }).join('\n');
        filename = `test_cases_${Date.now()}.txt`;
        mimeType = 'text/plain';
    }
    
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showSuccess('Download started!');
}

// Clear results
function clearResults() {
    document.getElementById('resultsSection').style.display = 'none';
    currentResults = null;
}

// Show error message
function showError(title, message) {
    alert(`❌ ${title}\n\n${message}`);
}

// Show success message
function showSuccess(message) {
    // Create a toast notification
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--success);
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    toast.textContent = `✅ ${message}`;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Modal functions
function showHelp() {
    document.getElementById('helpModal').style.display = 'flex';
}

function showAbout() {
    document.getElementById('aboutModal').style.display = 'flex';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Close modal when clicking outside
window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.style.display = 'none';
    }
});
