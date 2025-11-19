/**
 * API Communication Module
 * Handles all backend API calls
 */

const API_BASE = window.location.origin + '/api';

class API {
    /**
     * Get available models
     */
    static async getModels() {
        try {
            const response = await fetch(`${API_BASE}/models`);
            if (!response.ok) throw new Error('Failed to fetch models');
            return await response.json();
        } catch (error) {
            console.error('Error fetching models:', error);
            throw error;
        }
    }

    /**
     * Check model availability
     */
    static async checkModel(modelType, modelName, apiKey = null) {
        try {
            const response = await fetch(`${API_BASE}/models/check`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model_type: modelType,
                    model_name: modelName,
                    api_key: apiKey
                })
            });
            if (!response.ok) throw new Error('Failed to check model');
            return await response.json();
        } catch (error) {
            console.error('Error checking model:', error);
            throw error;
        }
    }

    /**
     * Get all prompts
     */
    static async getPrompts() {
        try {
            const response = await fetch(`${API_BASE}/prompts`);
            if (!response.ok) throw new Error('Failed to fetch prompts');
            return await response.json();
        } catch (error) {
            console.error('Error fetching prompts:', error);
            throw error;
        }
    }

    /**
     * Filter prompts
     */
    static async filterPrompts(categories = null, difficulties = null, tags = null) {
        try {
            const response = await fetch(`${API_BASE}/prompts/filter`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    categories,
                    difficulties,
                    tags
                })
            });
            if (!response.ok) throw new Error('Failed to filter prompts');
            return await response.json();
        } catch (error) {
            console.error('Error filtering prompts:', error);
            throw error;
        }
    }

    /**
     * Get prompts metadata
     */
    static async getPromptsMetadata() {
        try {
            const response = await fetch(`${API_BASE}/prompts/metadata`);
            if (!response.ok) throw new Error('Failed to fetch metadata');
            return await response.json();
        } catch (error) {
            console.error('Error fetching metadata:', error);
            throw error;
        }
    }

    /**
     * Validate custom prompts
     */
    static async validatePrompts(prompts) {
        try {
            const response = await fetch(`${API_BASE}/prompts/validate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(prompts)
            });
            if (!response.ok) throw new Error('Failed to validate prompts');
            return await response.json();
        } catch (error) {
            console.error('Error validating prompts:', error);
            throw error;
        }
    }

    /**
     * Run evaluation
     */
    static async runEvaluation(models, prompts) {
        try {
            const response = await fetch(`${API_BASE}/evaluate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    models,
                    prompts
                })
            });
            if (!response.ok) throw new Error('Failed to run evaluation');
            return await response.json();
        } catch (error) {
            console.error('Error running evaluation:', error);
            throw error;
        }
    }

    /**
     * Run evaluation with streaming results
     */
    static async runEvaluationStream(models, prompts, onProgress, onResult, onComplete, onError) {
        try {
            const response = await fetch(`${API_BASE}/evaluate/stream`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    models,
                    prompts
                })
            });

            if (!response.ok) throw new Error('Failed to start evaluation');

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = JSON.parse(line.slice(6));

                        switch (data.type) {
                            case 'status':
                                console.log('Status:', data.message);
                                break;
                            case 'info':
                                if (onProgress) onProgress(data);
                                break;
                            case 'result':
                                if (onResult) onResult(data.data, data.progress);
                                break;
                            case 'complete':
                                if (onComplete) onComplete(data.total);
                                break;
                            case 'error':
                                if (onError) onError(data.message);
                                break;
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Error in streaming evaluation:', error);
            if (onError) onError(error.message);
            throw error;
        }
    }

    /**
     * Export results
     */
    static async exportResults(results, format = 'csv') {
        try {
            const response = await fetch(`${API_BASE}/evaluate/export?format=${format}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(results)
            });

            if (!response.ok) throw new Error('Failed to export results');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `results_${new Date().getTime()}.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error('Error exporting results:', error);
            throw error;
        }
    }
}

// Export for use in other modules
window.API = API;
