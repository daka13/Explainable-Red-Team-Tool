# 🔧 Setup Guide - Explainable Red Team Tool

Complete step-by-step setup instructions for all components.

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Python Environment Setup](#python-environment-setup)
3. [API Key Configuration](#api-key-configuration)
4. [Ollama Installation](#ollama-installation)
5. [Troubleshooting](#troubleshooting)
6. [Verification](#verification)

## System Requirements

### Minimum Requirements
- **OS**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python**: 3.10 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 10GB free space (for models)
- **Internet**: Stable connection for API calls

### Optional (for Ollama)
- **RAM**: 8GB minimum for local models
- **Disk**: Additional 4-8GB per model

## Python Environment Setup

### Step 1: Check Python Version

```bash
python --version
# Should show Python 3.10.x or higher
```

If Python is not installed or version is too old:
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **macOS**: `brew install python@3.10`
- **Linux**: `sudo apt update && sudo apt install python3.10 python3.10-venv`

### Step 2: Clone Repository

```bash
git clone https://github.com/yourusername/explainable-redteam.git
cd explainable-redteam
```

### Step 3: Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows (Command Prompt):
venv\Scripts\activate.bat

# On Windows (PowerShell):
venv\Scripts\Activate.ps1
```

You should see `(venv)` in your terminal prompt.

### Step 4: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install all required packages. It may take 5-10 minutes.

## API Key Configuration

### Google Gemini API Key

1. **Get API Key**:
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Click "Create API Key"
   - Copy the key (starts with `AIza...`)

2. **Free Tier Limits**:
   - 60 requests per minute
   - 1500 requests per day
   - No credit card required

### HuggingFace Token

1. **Get Token**:
   - Go to [HuggingFace Settings](https://huggingface.co/settings/tokens)
   - Click "New token"
   - Select "Read" permissions
   - Copy the token (starts with `hf_...`)

2. **Free Tier Limits**:
   - 1000 requests per month
   - No credit card required

### Configure Environment File

1. **Copy template**:
```bash
cp .env.example .env
```

2. **Edit .env file**:
```bash
# Use your favorite editor
nano .env  # or vim, code, etc.
```

3. **Add your keys**:
```bash
GOOGLE_API_KEY=your_actual_gemini_api_key_here
HUGGINGFACE_TOKEN=your_actual_hf_token_here
OLLAMA_HOST=http://localhost:11434
GEMINI_RPM=5
HF_REQUESTS_PER_MONTH=1000
```

4. **Save and close** the file

**Important**: Never commit the `.env` file to git (it's in `.gitignore`)

## Ollama Installation

Ollama enables local model execution (optional but recommended).

### macOS Installation

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Or with Homebrew
brew install ollama
```

### Linux Installation

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows Installation

1. Download installer from [ollama.com](https://ollama.com/download)
2. Run the installer
3. Ollama will start automatically

### Starting Ollama Server

```bash
# The server should start automatically
# To manually start (if needed):
ollama serve
```

The server runs on `http://localhost:11434` by default.

### Downloading Models

```bash
# Llama 3.1 8B (~4.7GB download)
ollama pull llama3.1:8b

# Mistral 7B (~4.1GB download)
ollama pull mistral:7b
```

**Note**: Downloads may take 10-30 minutes depending on connection speed.

### Verify Installation

```bash
# List installed models
ollama list

# Should show:
# NAME              ID              SIZE
# llama3.1:8b      abc123...       4.7GB
# mistral:7b       def456...       4.1GB
```

## Verification

### Test Python Environment

```bash
# Activate venv if not already active
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Check installed packages
pip list | grep streamlit
# Should show: streamlit  1.30.0

pip list | grep google-generativeai
# Should show: google-generativeai  0.3.0
```

### Test API Keys

```bash
python << EOF
from dotenv import load_dotenv
import os

load_dotenv()

gemini_key = os.getenv("GOOGLE_API_KEY")
hf_token = os.getenv("HUGGINGFACE_TOKEN")

print(f"Gemini key: {'✓ Set' if gemini_key else '✗ Not set'}")
print(f"HF token: {'✓ Set' if hf_token else '✗ Not set'}")
EOF
```

### Test Ollama Connection

```bash
curl http://localhost:11434/api/tags
# Should return JSON with installed models
```

### Run Test Suite

```bash
pytest tests/ -v
```

All tests should pass or be skipped (if API keys not configured).

### Launch Application

```bash
streamlit run app.py
```

The dashboard should open at `http://localhost:8501`

## Troubleshooting

### Issue: Import Errors

**Symptom**: `ModuleNotFoundError: No module named 'streamlit'`

**Solution**:
```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

### Issue: Gemini API Errors

**Symptom**: `API key not valid` or `PERMISSION_DENIED`

**Solutions**:
1. Verify API key is correct in `.env`
2. Check you're using the right key (Gemini, not Maps/Cloud)
3. Ensure key has no extra spaces or quotes
4. Try regenerating the key

### Issue: Ollama Connection Failed

**Symptom**: `Connection refused` or `Ollama unavailable`

**Solutions**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve

# Check models are installed
ollama list
```

### Issue: HuggingFace Model Loading

**Symptom**: `Model loading` or 503 errors

**Solution**:
- HF models can take 20-30 seconds to load initially
- Wait and retry
- Check token permissions (should have "read" access)

### Issue: Out of Memory (Ollama)

**Symptom**: Ollama crashes or system freezes

**Solutions**:
1. Close other applications
2. Use smaller models (7B instead of 13B)
3. Increase system RAM or swap space
4. Use cloud models only (skip Ollama)

### Issue: Streamlit Port Already in Use

**Symptom**: `Port 8501 is already in use`

**Solution**:
```bash
# Use a different port
streamlit run app.py --server.port 8502
```

### Issue: Rate Limiting

**Symptom**: `Rate limit exceeded` errors

**Solutions**:
- **Gemini**: Wait 60 seconds, reduce RPM in `.env`
- **HuggingFace**: Check monthly quota, wait for reset
- **Ollama**: No rate limits (local)

## Advanced Configuration

### Custom Ollama Host

If running Ollama on a different machine:

```bash
# In .env
OLLAMA_HOST=http://192.168.1.100:11434
```

### Adjusting Rate Limits

```bash
# In .env
GEMINI_RPM=3  # Slower but safer
HF_REQUESTS_PER_MONTH=500  # Track usage
```

### Using Different Models

Edit `app.py` to add custom models:

```python
# In setup_clients() function
if "Custom Model" in selected_models:
    client = OllamaClient(model="your-model:tag")
    clients.append(client)
```

## Getting Help

If you encounter issues not covered here:

1. **Check logs**: Streamlit shows errors in the terminal
2. **Enable debug mode**: Run with `streamlit run app.py --logger.level debug`
3. **Check GitHub issues**: Search for similar problems
4. **Create an issue**: Provide error messages and system info

## Next Steps

Once setup is complete:

1. ✅ Run `streamlit run app.py`
2. ✅ Select at least one model
3. ✅ Choose prompt filters
4. ✅ Click "Run Evaluation"
5. ✅ Explore the dashboard tabs

Enjoy testing! 🎯
