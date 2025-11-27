// Admin Dashboard JavaScript
const API_BASE = window.location.origin;
let activityLog = [];

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    loadConfig();
    checkHealth();
    loadModels();
    loadInstructions();
    
    // Set up event listeners
    setupEventListeners();
    
    // Auto-refresh health every 30 seconds
    setInterval(checkHealth, 30000);
});

// Tab management
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.dataset.tab;
            
            // Remove active class from all
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked
            button.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
            
            logActivity(`Switched to ${targetTab} tab`);
        });
    });
}

// Health check
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        
        const isHealthy = data.status === 'healthy';
        const ollamaConnected = data.ollama === 'connected';
        
        updateStatusIndicator('apiStatus', isHealthy, isHealthy ? 'API Online' : 'API Offline');
        updateStatusIndicator('ollamaStatus', ollamaConnected, ollamaConnected ? 'Ollama Connected' : 'Ollama Disconnected');
        
        document.getElementById('apiStatusDetail').textContent = isHealthy ? '✅ Online' : '❌ Offline';
        document.getElementById('ollamaStatusDetail').textContent = ollamaConnected ? '✅ Connected' : '❌ Disconnected';
        
        if (isHealthy) {
            logActivity('Health check: All systems operational');
        } else {
            logActivity('Health check: System issues detected', 'error');
        }
    } catch (error) {
        updateStatusIndicator('apiStatus', false, 'API Offline');
        updateStatusIndicator('ollamaStatus', false, 'Ollama Disconnected');
        document.getElementById('apiStatusDetail').textContent = '❌ Connection Error';
        document.getElementById('ollamaStatusDetail').textContent = '❌ Unknown';
        logActivity(`Health check failed: ${error.message}`, 'error');
    }
}

function updateStatusIndicator(elementId, online, text) {
    const element = document.getElementById(elementId);
    const dot = element.querySelector('.dot');
    dot.className = online ? 'dot online' : 'dot offline';
    element.childNodes[2].textContent = text;
}

// Load models
async function loadModels() {
    try {
        const response = await fetch(`${API_BASE}/models`);
        const data = await response.json();
        
        const models = data.models || [];
        const defaultModel = data.default_model || 'Unknown';
        
        document.getElementById('modelCount').textContent = models.length;
        document.getElementById('defaultModel').textContent = defaultModel;
        
        // Populate model selects
        populateModelSelects(models);
        
        // Display model list
        displayModelsList(models, defaultModel);
        
        logActivity(`Loaded ${models.length} models`);
    } catch (error) {
        document.getElementById('modelCount').textContent = 'Error';
        document.getElementById('defaultModel').textContent = 'Error';
        logActivity(`Failed to load models: ${error.message}`, 'error');
    }
}

function populateModelSelects(models) {
    const selects = ['modelSelect', 'fileModel', 'testModel'];
    
    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        // Keep the first option (Default or Select)
        const firstOption = select.options[0];
        select.innerHTML = '';
        select.appendChild(firstOption);
        
        models.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model;
            select.appendChild(option);
        });
    });
}

function displayModelsList(models, defaultModel) {
    const container = document.getElementById('modelsList');
    
    if (models.length === 0) {
        container.innerHTML = '<p class="text-muted">No models found</p>';
        return;
    }
    
    container.innerHTML = models.map(model => {
        const isDefault = model === defaultModel;
        return `
            <div class="model-card">
                <div class="model-name">${model} ${isDefault ? '⭐' : ''}</div>
                <div class="model-info">${isDefault ? 'Default Model' : 'Available'}</div>
            </div>
        `;
    }).join('');
}

// Load instructions
async function loadInstructions() {
    try {
        const response = await fetch(`${API_BASE}/instructions`);
        const data = await response.json();
        
        document.getElementById('instructionsText').value = data.instructions || '';
        logActivity('Loaded system instructions');
    } catch (error) {
        logActivity(`Failed to load instructions: ${error.message}`, 'error');
    }
}

// Setup event listeners
function setupEventListeners() {
    // Single requirement form
    document.getElementById('singleForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await generateSingle();
    });
    
    // File upload form
    document.getElementById('fileForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await generateFromFile();
    });
    
    // Instructions form
    document.getElementById('instructionsForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await saveInstructions();
    });
    
    // Reload instructions
    document.getElementById('reloadInstructions').addEventListener('click', loadInstructions);
    
    // Refresh models
    document.getElementById('refreshModels').addEventListener('click', loadModels);
    
    // Save config
    document.getElementById('saveConfig').addEventListener('click', saveConfig);
    
    // Copy result
    document.getElementById('copyResult').addEventListener('click', copyResult);
    
    // Download result
    document.getElementById('downloadResult').addEventListener('click', downloadResult);
    
    // Test model form
    document.getElementById('testModelForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await testModel();
    });
}

// Generate single test case
async function generateSingle() {
    const reqId = document.getElementById('reqId').value;
    const description = document.getElementById('description').value;
    const category = document.getElementById('category').value;
    const paramCategory = document.getElementById('paramCategory').value;
    const model = document.getElementById('modelSelect').value;
    
    const payload = {
        REQUIREMENTS_ID: reqId,
        DESCRIPTION: description,
        CATEGORY: category,
        PARAMETER_CATEGORY: paramCategory
    };
    
    if (model) {
        payload.model = model;
    }
    
    logActivity(`Generating test case for ${reqId}...`);
    
    try {
        const response = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const result = await response.json();
        displayResult(result);
        logActivity(`✅ Generated test case for ${reqId}`);
    } catch (error) {
        logActivity(`❌ Failed to generate test case: ${error.message}`, 'error');
        alert(`Error: ${error.message}`);
    }
}

// Generate from file
async function generateFromFile() {
    const fileInput = document.getElementById('fileUpload');
    const model = document.getElementById('fileModel').value;
    
    if (!fileInput.files.length) {
        alert('Please select a file');
        return;
    }
    
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);
    if (model) {
        formData.append('model', model);
    }
    
    logActivity(`Uploading ${file.name}...`);
    
    try {
        const response = await fetch(`${API_BASE}/generate/file`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const result = await response.json();
        displayResult(result);
        logActivity(`✅ Processed ${file.name}: ${result.successful}/${result.total} successful`);
    } catch (error) {
        logActivity(`❌ Failed to process file: ${error.message}`, 'error');
        alert(`Error: ${error.message}`);
    }
}

// Display result
function displayResult(result) {
    const section = document.getElementById('resultsSection');
    const output = document.getElementById('resultOutput');
    
    output.textContent = JSON.stringify(result, null, 2);
    section.style.display = 'block';
    
    // Scroll to results
    section.scrollIntoView({ behavior: 'smooth' });
}

// Copy result
function copyResult() {
    const output = document.getElementById('resultOutput');
    navigator.clipboard.writeText(output.textContent).then(() => {
        logActivity('Copied result to clipboard');
        alert('Copied to clipboard!');
    });
}

// Download result
function downloadResult() {
    const output = document.getElementById('resultOutput');
    const blob = new Blob([output.textContent], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `test_case_${new Date().getTime()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    logActivity('Downloaded result');
}

// Save instructions
async function saveInstructions() {
    const instructions = document.getElementById('instructionsText').value;
    
    if (!instructions.trim()) {
        alert('Instructions cannot be empty');
        return;
    }
    
    logActivity('Saving system instructions...');
    
    try {
        const response = await fetch(`${API_BASE}/instructions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ instructions })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const result = await response.json();
        logActivity('✅ Instructions saved successfully');
        alert('Instructions saved successfully!');
    } catch (error) {
        logActivity(`❌ Failed to save instructions: ${error.message}`, 'error');
        alert(`Error: ${error.message}`);
    }
}

// Test model
async function testModel() {
    const model = document.getElementById('testModel').value;
    const prompt = document.getElementById('testPrompt').value;
    
    if (!model || !prompt) {
        alert('Please select a model and enter a prompt');
        return;
    }
    
    logActivity(`Testing model ${model}...`);
    
    const testReq = {
        REQUIREMENTS_ID: 'TEST-001',
        DESCRIPTION: prompt,
        CATEGORY: 'Functional',
        model: model
    };
    
    try {
        const response = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(testReq)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const result = await response.json();
        const output = document.getElementById('testModelResult');
        output.textContent = result.Test_Case || 'No output';
        output.style.display = 'block';
        logActivity(`✅ Model ${model} test completed`);
    } catch (error) {
        logActivity(`❌ Model test failed: ${error.message}`, 'error');
        alert(`Error: ${error.message}`);
    }
}

// Configuration management
function loadConfig() {
    document.getElementById('apiBaseUrl').value = localStorage.getItem('apiBaseUrl') || 'http://localhost:5000';
    document.getElementById('ollamaBaseUrl').value = localStorage.getItem('ollamaBaseUrl') || 'http://localhost:11434';
    document.getElementById('timeout').value = localStorage.getItem('timeout') || '180';
}

function saveConfig() {
    const apiBaseUrl = document.getElementById('apiBaseUrl').value;
    const ollamaBaseUrl = document.getElementById('ollamaBaseUrl').value;
    const timeout = document.getElementById('timeout').value;
    
    localStorage.setItem('apiBaseUrl', apiBaseUrl);
    localStorage.setItem('ollamaBaseUrl', ollamaBaseUrl);
    localStorage.setItem('timeout', timeout);
    
    logActivity('Configuration saved');
    alert('Configuration saved! Reload the page for changes to take effect.');
}

// Activity log
function logActivity(message, type = 'info') {
    const timestamp = new Date().toLocaleTimeString();
    const entry = { timestamp, message, type };
    activityLog.unshift(entry);
    
    // Keep only last 50 entries
    if (activityLog.length > 50) {
        activityLog = activityLog.slice(0, 50);
    }
    
    updateActivityLog();
}

function updateActivityLog() {
    const container = document.getElementById('activityLog');
    
    if (activityLog.length === 0) {
        container.innerHTML = '<p class="text-muted">No activity yet...</p>';
        return;
    }
    
    container.innerHTML = activityLog.map(entry => {
        const icon = entry.type === 'error' ? '❌' : '📝';
        const color = entry.type === 'error' ? '#ef4444' : '#6b7280';
        return `
            <div class="log-entry" style="color: ${color}">
                <span>${icon} [${entry.timestamp}]</span> ${entry.message}
            </div>
        `;
    }).join('');
}
