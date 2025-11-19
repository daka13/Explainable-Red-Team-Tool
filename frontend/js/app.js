/**
 * Main Application Logic
 */

// Application state
const AppState = {
    models: {},
    selectedModels: [],
    prompts: [],
    selectedPrompts: [],
    results: [],
    apiKeys: {
        gemini: localStorage.getItem('gemini_api_key') || '',
        huggingface: localStorage.getItem('hf_token') || ''
    }
};

// Initialize application
document.addEventListener('DOMContentLoaded', async () => {
    await loadModels();
    await loadPrompts();
    setupEventListeners();
    loadSavedSettings();
});

// Load available models
async function loadModels() {
    try {
        AppState.models = await API.getModels();
        renderModelSelection();
    } catch (error) {
        showError('Failed to load models');
    }
}

// Render model selection checkboxes
function renderModelSelection() {
    const container = document.getElementById('modelSelection');
    container.innerHTML = '';

    Object.entries(AppState.models).forEach(([type, models]) => {
        models.forEach(model => {
            const div = document.createElement('div');
            div.className = 'form-check mb-2';
            div.innerHTML = `
                <input class="form-check-input" type="checkbox"
                       value="${type}|${model.name}"
                       id="model_${type}_${model.name.replace(/[^a-z0-9]/gi, '_')}"
                       data-requires-key="${model.requires_key}">
                <label class="form-check-label" for="model_${type}_${model.name.replace(/[^a-z0-9]/gi, '_')}">
                    <strong>${model.display_name}</strong><br>
                    <small class="text-muted">${model.description}</small>
                </label>
            `;
            container.appendChild(div);
        });
    });

    // Add change listeners
    container.querySelectorAll('input[type="checkbox"]').forEach(cb => {
        cb.addEventListener('change', updateSelectedModels);
    });
}

// Update selected models
function updateSelectedModels() {
    const checkboxes = document.querySelectorAll('#modelSelection input:checked');
    AppState.selectedModels = Array.from(checkboxes).map(cb => {
        const [type, name] = cb.value.split('|');
        return { type, name };
    });
    updateRunButton();
}

// Load prompts
async function loadPrompts() {
    try {
        const metadata = await API.getPromptsMetadata();

        // Populate category filter
        const categoryFilter = document.getElementById('categoryFilter');
        categoryFilter.innerHTML = metadata.categories.map(cat =>
            `<option value="${cat}" selected>${cat}</option>`
        ).join('');

        // Load initial prompts
        await filterPrompts();
    } catch (error) {
        showError('Failed to load prompts');
    }
}

// Filter prompts
async function filterPrompts() {
    try {
        const categories = Array.from(document.getElementById('categoryFilter').selectedOptions).map(o => o.value);
        const difficulties = Array.from(document.getElementById('difficultyFilter').selectedOptions).map(o => o.value);

        const response = await API.filterPrompts(
            categories.length > 0 ? categories : null,
            difficulties.length > 0 ? difficulties : null
        );

        AppState.selectedPrompts = response.prompts;
        document.getElementById('promptCount').textContent = `${response.total} prompts selected`;
        renderPromptsTable();
        updateRunButton();
    } catch (error) {
        showError('Failed to filter prompts');
    }
}

// Render prompts table
function renderPromptsTable() {
    const container = document.getElementById('promptsTable');
    if (!container) return;

    const html = `
        <table class="table table-glass">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Category</th>
                    <th>Difficulty</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
                ${AppState.selectedPrompts.map(p => `
                    <tr>
                        <td><code>${p.id}</code></td>
                        <td><span class="badge bg-secondary">${p.category}</span></td>
                        <td><span class="badge bg-${p.difficulty === 'hard' ? 'danger' : p.difficulty === 'medium' ? 'warning' : 'success'}">${p.difficulty}</span></td>
                        <td>${p.description}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    container.innerHTML = html;
}

// Check model connections
async function checkModels() {
    document.getElementById('checkModelsBtn').disabled = true;
    document.getElementById('checkModelsBtn').innerHTML = '<i class="fas fa-spinner fa-spin"></i> Checking...';

    for (const model of AppState.selectedModels) {
        const apiKey = model.type === 'gemini' ? AppState.apiKeys.gemini :
                      model.type === 'huggingface' ? AppState.apiKeys.huggingface : null;

        try {
            const status = await API.checkModel(model.type, model.name, apiKey);
            const checkbox = document.querySelector(`input[value="${model.type}|${model.name}"]`);
            const label = checkbox.nextElementSibling;

            if (status.available) {
                label.innerHTML += ' <span class="badge bg-success">✓ Connected</span>';
            } else {
                label.innerHTML += ` <span class="badge bg-danger">✗ ${status.error}</span>`;
            }
        } catch (error) {
            console.error(`Error checking ${model.name}:`, error);
        }
    }

    document.getElementById('checkModelsBtn').disabled = false;
    document.getElementById('checkModelsBtn').innerHTML = '<i class="fas fa-plug"></i> Check Connections';
}

// Run evaluation
async function runEvaluation() {
    if (AppState.selectedModels.length === 0 || AppState.selectedPrompts.length === 0) {
        showError('Please select at least one model and one prompt');
        return;
    }

    // Prepare models with API keys
    const models = AppState.selectedModels.map(m => ({
        type: m.type,
        name: m.name,
        api_key: m.type === 'gemini' ? AppState.apiKeys.gemini :
                m.type === 'huggingface' ? AppState.apiKeys.huggingface : null
    }));

    // Show progress
    const progressBar = document.getElementById('progressBar');
    const statusText = document.getElementById('statusText');
    const runBtn = document.getElementById('runEvaluationBtn');

    progressBar.style.display = 'block';
    runBtn.disabled = true;
    AppState.results = [];

    try {
        await API.runEvaluationStream(
            models,
            AppState.selectedPrompts,
            (info) => {
                statusText.textContent = `Running ${info.total_tests} tests...`;
            },
            (result, progress) => {
                AppState.results.push(result);
                const percent = (progress * 100).toFixed(0);
                progressBar.querySelector('.progress-bar').style.width = `${percent}%`;
                statusText.textContent = `Progress: ${percent}%`;
            },
            (total) => {
                progressBar.style.display = 'none';
                statusText.textContent = `✅ Completed ${total} tests`;
                updateDashboard();
                enableExportButtons();
            },
            (error) => {
                showError(error);
                progressBar.style.display = 'none';
                runBtn.disabled = false;
            }
        );
    } catch (error) {
        showError('Evaluation failed: ' + error.message);
    } finally {
        runBtn.disabled = false;
    }
}

// Update dashboard with results
function updateDashboard() {
    if (AppState.results.length === 0) return;

    // Update metrics
    document.getElementById('totalTests').textContent = AppState.results.length;

    const refused = AppState.results.filter(r => r.refused).length;
    document.getElementById('refusalRate').textContent = `${((refused / AppState.results.length) * 100).toFixed(1)}%`;

    const avgLatency = AppState.results.reduce((sum, r) => sum + r.latency_ms, 0) / AppState.results.length;
    document.getElementById('avgLatency').textContent = `${avgLatency.toFixed(0)}ms`;

    const errors = AppState.results.filter(r => r.error).length;
    document.getElementById('totalErrors').textContent = errors;

    // Update charts
    Charts.plotRefusalRateByModel(AppState.results);
    Charts.plotLatency(AppState.results);
    Charts.plotCategoryHeatmap(AppState.results);
    Charts.plotSuccessRateByCategory(AppState.results);
    Charts.plotVulnerabilityRadar(AppState.results);

    // Update results table
    renderResultsTable();
}

// Render results table
function renderResultsTable() {
    const tbody = document.getElementById('resultsTableBody');
    tbody.innerHTML = AppState.results.map(r => `
        <tr>
            <td>${r.model}</td>
            <td><small>${r.prompt_text.substring(0, 50)}...</small></td>
            <td><span class="badge bg-secondary">${r.prompt_category}</span></td>
            <td><span class="badge ${r.refused ? 'badge-refused' : 'badge-complied'}">${r.refused ? 'Refused' : 'Complied'}</span></td>
            <td>${r.refusal_confidence.toFixed(2)}</td>
            <td>${r.latency_ms.toFixed(0)}ms</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="viewResponse('${r.test_id}')">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

// Export functions
async function exportCSV() {
    if (AppState.results.length === 0) {
        showError('No results to export');
        return;
    }
    try {
        await API.exportResults(AppState.results, 'csv');
    } catch (error) {
        showError('Export failed');
    }
}

async function exportJSON() {
    if (AppState.results.length === 0) {
        showError('No results to export');
        return;
    }
    try {
        await API.exportResults(AppState.results, 'json');
    } catch (error) {
        showError('Export failed');
    }
}

// Enable export buttons
function enableExportButtons() {
    document.getElementById('exportCSV').disabled = false;
    document.getElementById('exportJSON').disabled = false;
}

// Settings management
function loadSavedSettings() {
    document.getElementById('geminiApiKey').value = AppState.apiKeys.gemini;
    document.getElementById('hfToken').value = AppState.apiKeys.huggingface;
}

function saveSettings() {
    AppState.apiKeys.gemini = document.getElementById('geminiApiKey').value;
    AppState.apiKeys.huggingface = document.getElementById('hfToken').value;

    localStorage.setItem('gemini_api_key', AppState.apiKeys.gemini);
    localStorage.setItem('hf_token', AppState.apiKeys.huggingface);

    const modal = bootstrap.Modal.getInstance(document.getElementById('settingsModal'));
    modal.hide();

    showSuccess('Settings saved successfully');
}

// Dark mode toggle
function toggleDarkMode() {
    document.body.classList.toggle('light-mode');
    const icon = document.querySelector('#darkModeToggle i');
    icon.className = document.body.classList.contains('light-mode') ? 'fas fa-sun' : 'fas fa-moon';
}

// Custom prompt
function addCustomPrompt() {
    const modal = new bootstrap.Modal(document.getElementById('customPromptModal'));
    modal.show();
}

function saveCustomPrompt() {
    const text = document.getElementById('customPromptText').value;
    const category = document.getElementById('customPromptCategory').value;
    const difficulty = document.getElementById('customPromptDifficulty').value;
    const description = document.getElementById('customPromptDescription').value;

    if (!text) {
        showError('Please enter a prompt');
        return;
    }

    const customPrompt = {
        id: `custom_${Date.now()}`,
        category,
        difficulty,
        prompt: text,
        expected_behavior: 'unknown',
        description: description || 'Custom prompt',
        tags: ['custom']
    };

    AppState.selectedPrompts.push(customPrompt);
    document.getElementById('promptCount').textContent = `${AppState.selectedPrompts.length} prompts selected`;

    const modal = bootstrap.Modal.getInstance(document.getElementById('customPromptModal'));
    modal.hide();

    // Clear form
    document.getElementById('customPromptText').value = '';
    document.getElementById('customPromptDescription').value = '';

    showSuccess('Custom prompt added');
    renderPromptsTable();
}

// Utility functions
function updateRunButton() {
    const btn = document.getElementById('runEvaluationBtn');
    btn.disabled = AppState.selectedModels.length === 0 || AppState.selectedPrompts.length === 0;
}

function showError(message) {
    // Could use toast notifications
    alert('Error: ' + message);
}

function showSuccess(message) {
    // Could use toast notifications
    console.log('Success:', message);
}

// Setup event listeners
function setupEventListeners() {
    document.getElementById('settingsBtn').addEventListener('click', () => {
        const modal = new bootstrap.Modal(document.getElementById('settingsModal'));
        modal.show();
    });

    document.getElementById('saveSettings').addEventListener('click', saveSettings);
    document.getElementById('darkModeToggle').addEventListener('click', toggleDarkMode);
    document.getElementById('checkModelsBtn').addEventListener('click', checkModels);
    document.getElementById('runEvaluationBtn').addEventListener('click', runEvaluation);
    document.getElementById('exportCSV').addEventListener('click', exportCSV);
    document.getElementById('exportJSON').addEventListener('click', exportJSON);
    document.getElementById('addCustomPrompt').addEventListener('click', addCustomPrompt);
    document.getElementById('saveCustomPrompt').addEventListener('click', saveCustomPrompt);

    document.getElementById('categoryFilter').addEventListener('change', filterPrompts);
    document.getElementById('difficultyFilter').addEventListener('change', filterPrompts);

    // Toggle password visibility
    document.getElementById('toggleGemini').addEventListener('click', () => {
        const input = document.getElementById('geminiApiKey');
        input.type = input.type === 'password' ? 'text' : 'password';
    });

    document.getElementById('toggleHF').addEventListener('click', () => {
        const input = document.getElementById('hfToken');
        input.type = input.type === 'password' ? 'text' : 'password';
    });
}
