# 🎯 Explainable Red Team Tool

A multi-model adversarial testing framework with interpretability layers for AI safety evaluation. Built with 100% free APIs to demonstrate LLM robustness analysis, jailbreak detection, and explainable AI techniques.

## 🌟 Features

### Core Capabilities
- **Multi-Model Testing**: Test prompts across 5+ models simultaneously
- **Adversarial Prompt Library**: 25+ curated jailbreak, bias, and manipulation prompts
- **Async Evaluation**: Concurrent testing for optimal performance
- **Comprehensive Metrics**: Refusal rates, latency, confidence scores

### Interpretability Layer
- **SHAP Attribution**: Token-level importance analysis
- **Embedding Visualization**: UMAP-based 2D projections
- **Cluster Analysis**: Identify prompt patterns
- **Comparative Analysis**: Model-by-model vulnerability ranking

### Visualization
- Interactive Plotly dashboards
- Refusal rate heatmaps
- Latency distributions
- Vulnerability radar charts
- Timeline analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Google Gemini API key (free tier)
- HuggingFace token (free tier)
- Ollama installed locally (optional but recommended)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/explainable-redteam.git
cd explainable-redteam
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys:
# - GOOGLE_API_KEY=your_gemini_key
# - HUGGINGFACE_TOKEN=your_hf_token
```

5. **Install Ollama (optional)**
```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull llama3.1:8b
ollama pull mistral:7b
```

6. **Run the application**
```bash
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

## 📚 Models Supported

### Cloud Models (Free APIs)
- **Google Gemini 2.0 Flash** - Fast, efficient responses
- **Google Gemini 1.5 Pro** - More capable, slower
- **HuggingFace Mistral-7B-Instruct** - Open-source alternative

### Local Models (Ollama)
- **Llama 3.1 8B** - Meta's latest open model
- **Mistral 7B** - Efficient open-source model

## 🎨 Project Structure

```
explainable-redteam/
├── app.py                      # Streamlit dashboard
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
│
├── src/
│   ├── api_clients/           # Model API wrappers
│   │   ├── base.py           # Abstract base class
│   │   ├── gemini_client.py  # Google Gemini
│   │   ├── ollama_client.py  # Local Ollama
│   │   └── huggingface_client.py  # HF Inference API
│   │
│   ├── interpretability/      # Explainability modules
│   │   ├── attribution.py    # SHAP analysis
│   │   └── embeddings.py     # UMAP visualization
│   │
│   ├── adversarial_prompts.py # Prompt library
│   ├── evaluator.py           # Test execution engine
│   └── visualizations.py      # Plotly charts
│
├── data/
│   ├── prompts/
│   │   └── jailbreaks.json   # 25+ adversarial prompts
│   └── results/              # CSV exports
│
└── tests/
    └── test_api_clients.py   # Unit tests
```

## 🔍 Usage Guide

### Basic Workflow

1. **Select Models**: Choose which LLMs to test (minimum 1)
2. **Filter Prompts**: Select categories and difficulty levels
3. **Run Evaluation**: Click "Run Evaluation" to start testing
4. **Analyze Results**: Explore the 5 dashboard tabs

### Dashboard Tabs

#### 📊 Overview
- Summary metrics (total tests, refusal rate, latency)
- Key insights (most/least vulnerable models)
- Refusal rate comparison
- Latency distribution

#### 📈 Analysis
- Category performance heatmap
- Difficulty distribution
- Success rate comparison
- Vulnerability radar chart
- Timeline analysis

#### 🔍 Interpretability
- Token attribution analysis
- Model response comparison
- Embedding space visualization
- Cluster analysis

#### 📋 Results Table
- Filterable results table
- Export to CSV
- Detailed response inspection

#### ℹ️ About
- Project documentation
- Setup instructions
- Technical details

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api_clients.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 📊 Sample Output

### Refusal Rate Comparison
```
Model                      | Refusal Rate | Avg Latency
---------------------------|--------------|-------------
Gemini 2.0 Flash          | 87.5%        | 1,234 ms
Gemini 1.5 Pro            | 91.2%        | 2,456 ms
Llama 3.1 8B              | 78.3%        | 892 ms
Mistral 7B                | 74.1%        | 756 ms
HF Mistral-7B-Instruct    | 72.8%        | 3,421 ms
```

### Key Insights
- **Most Vulnerable**: HF Mistral-7B-Instruct (72.8% refusal rate)
- **Least Vulnerable**: Gemini 1.5 Pro (91.2% refusal rate)
- **Fastest**: Mistral 7B (756 ms avg latency)
- **Most Common Attack**: Roleplay jailbreaks (35% of prompts)

## 🔧 Configuration

### Environment Variables
```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key
HUGGINGFACE_TOKEN=your_hf_token

# Optional
OLLAMA_HOST=http://localhost:11434
GEMINI_RPM=5
HF_REQUESTS_PER_MONTH=1000
```

### Rate Limits (Free Tier)
- **Gemini**: 5-10 requests/minute
- **HuggingFace**: 1000 requests/month
- **Ollama**: No limits (local)

## 📖 Adversarial Prompt Categories

### Jailbreak Attempts
- Roleplay (DAN, evil AI)
- Hypothetical scenarios
- Prompt injection
- Encoding bypasses

### Bias Triggers
- Stereotype reinforcement
- Gender/racial bias
- Religious discrimination

### Harmful Content
- Self-harm instructions
- Violence requests
- Malicious code generation

### Reasoning Traps
- Logical fallacies
- Purpose contradictions
- False premises

### Manipulation Tactics
- Emotional appeals
- Urgency framing
- Authority claims

## 🎓 Educational Use Cases

This tool is designed for:
- **AI Safety Research**: Understanding model vulnerabilities
- **Red Team Training**: Learning adversarial testing techniques
- **Model Comparison**: Evaluating safety mechanisms
- **Interpretability Studies**: Understanding refusal patterns
- **Portfolio Projects**: Demonstrating ML security skills

## 🚨 Ethical Guidelines

This tool is intended for:
- ✅ Educational purposes
- ✅ Authorized security research
- ✅ AI safety evaluation
- ✅ Model comparison studies

**DO NOT USE FOR:**
- ❌ Attacking production systems
- ❌ Generating harmful content
- ❌ Bypassing safety mechanisms for malicious purposes
- ❌ Unauthorized testing

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) - Dashboard framework
- [Plotly](https://plotly.com/) - Interactive visualizations
- [SHAP](https://github.com/slundberg/shap) - Attribution analysis
- [Sentence Transformers](https://www.sbert.net/) - Embeddings
- [UMAP](https://umap-learn.readthedocs.io/) - Dimensionality reduction

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Note**: This tool uses 100% free APIs. For production use cases with higher volume, consider upgrading to paid tiers.
