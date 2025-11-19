# ⚡ Quick Start Guide

## 🚀 Get Running in 3 Minutes

### Step 1: Clone & Setup (1 min)

```bash
git clone <your-repo-url>
cd Explainable-Red-Team-Tool
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
```

### Step 2: Launch App (30 seconds)

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Open Browser

Navigate to: **http://localhost:8000**

That's it! 🎉

---

## 🎯 First Evaluation (5 min total)

### 1. Get API Keys (2 min)

**Google Gemini** (free, no credit card):
- Visit: https://makersuite.google.com/app/apikey
- Click "Create API Key"
- Copy the key

**HuggingFace** (optional, free):
- Visit: https://huggingface.co/settings/tokens
- Click "New token"
- Select "Read" permissions
- Copy the token

### 2. Configure in UI (1 min)

1. Click **"Settings"** button (top right)
2. Paste your Gemini API key
3. Paste your HuggingFace token (optional)
4. Click **"Save Settings"**

### 3. Run First Test (2 min)

1. **Select a model**: Check "Gemini 2.0 Flash"
2. **Keep default prompts**: Already filtered to medium difficulty
3. Click **"Check Connections"** to verify
4. Click **"▶️ Run Evaluation"**
5. Watch real-time progress!

---

## 📊 What You'll See

- **Overview Tab**: Summary metrics, refusal rates, latency charts
- **Analysis Tab**: Heatmaps, vulnerability radar, category performance
- **Interpretability Tab**: Token attribution, embedding visualizations
- **Prompts Tab**: Browse 100+ adversarial prompts, add your own
- **Results Tab**: Detailed results table, export options

---

## 🎨 Features Tour

### ✨ Beautiful Animated Gradient Mesh
- Slow-moving organic gradient background
- Smooth gold & teal orbs floating across screen
- Professional glassmorphism UI

### 🤖 Multi-Model Testing
- **Gemini 2.0 Flash** - Fast Google model
- **Gemini 1.5 Pro** - More capable Google model
- **Llama 3.1 8B** - Local via Ollama
- **Mistral 7B** - Local via Ollama
- **HF Mistral** - Cloud HuggingFace

### 🎯 102+ Adversarial Prompts
- Jailbreak attempts (DAN, roleplay, etc.)
- Bias triggers
- Harmful content requests
- Manipulation tactics
- Reasoning traps
- And more!

### 🔍 Interpretability
- **SHAP Attribution**: See which tokens trigger refusal
- **UMAP Embeddings**: Visualize prompt clusters in 2D
- **Comparative Analysis**: Model-by-model vulnerability

---

## 💡 Pro Tips

### Testing Without Ollama
Use only cloud models (Gemini, HuggingFace) - no Ollama needed!

### Add Custom Prompts
1. Go to "Prompts" tab
2. Click "Add Custom Prompt"
3. Paste your jailbreak attempt
4. Select category & difficulty
5. It's added to your evaluation set!

### Export Results
- CSV for spreadsheet analysis
- JSON for programmatic processing
- Click export buttons in sidebar

### Dark/Light Mode
Click the moon/sun icon (top right) to toggle

---

## 🆘 Troubleshooting

### "Port 8000 already in use"
```bash
uvicorn backend.main:app --port 8001
```

### "ModuleNotFoundError"
```bash
# Make sure venv is activated
source venv/bin/activate
pip install -r backend/requirements.txt
```

### "Gemini API Error"
- Verify API key is correct (no extra spaces)
- Check you have free tier quota remaining
- Try clicking "Check Connections" to diagnose

### "Ollama not available"
Ollama is optional! Just don't select those models.

To use Ollama:
```bash
# Install: ollama.com/download
ollama pull llama3.1:8b
ollama serve
```

---

## 🎓 Next Steps

1. ✅ **Try different models** - Compare Gemini vs local models
2. ✅ **Explore prompt library** - 102 diverse adversarial prompts
3. ✅ **Add custom prompts** - Test your own jailbreaks
4. ✅ **Analyze results** - Use interpretability features
5. ✅ **Export data** - CSV/JSON for further analysis

---

## 📚 More Resources

- **Full README**: Feature details, architecture
- **SETUP_GUIDE**: Detailed installation (old Streamlit version)
- **DEPLOYMENT_GUIDE**: Deploy to cloud (Vercel, Render, Docker)

---

## ❤️ Enjoy Testing!

You're now ready to evaluate AI safety across multiple models with beautiful visualizations and explainability features.

Happy red teaming! 🎯
