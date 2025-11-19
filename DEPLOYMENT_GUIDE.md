# 🚀 Deployment Guide - Explainable Red Team Tool v2.0

## Quick Start (Local Development)

### Prerequisites
- Python 3.10+
- Node.js (optional, for frontend dev)
- Docker (optional)

### Local Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd Explainable-Red-Team-Tool

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Configure environment (optional - can use UI instead)
cp .env.example .env
# Edit .env with your API keys

# 5. Run the application
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 6. Open browser
# Navigate to: http://localhost:8000
```

The application will be available at `http://localhost:8000`.

---

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start
docker-compose up --build

# Run in background
docker-compose up -d

# Stop
docker-compose down
```

Application runs on `http://localhost:8000`.

### Using Dockerfile Only

```bash
# Build image
docker build -t red-team-tool .

# Run container
docker run -p 8000:8000 \
  -e GOOGLE_API_KEY=your_key \
  -e HUGGINGFACE_TOKEN=your_token \
  red-team-tool
```

---

## ☁️ Cloud Deployment Options

### Option 1: Vercel (Serverless)

**Best for**: Frontend-heavy, API endpoints

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Or link to GitHub and auto-deploy
vercel --prod
```

**Configuration**: Uses `vercel.json`

**Environment Variables**:
- Set in Vercel Dashboard > Settings > Environment Variables
- Add: `GOOGLE_API_KEY`, `HUGGINGFACE_TOKEN`

**Limitations**:
- Serverless functions have 10s timeout
- For long evaluations, use streaming endpoint

---

### Option 2: Render (Full-Stack)

**Best for**: Complete app with persistent storage

**Steps**:
1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. Click "New +" → "Web Service"
4. Connect your GitHub repo
5. Render auto-detects `render.yaml`
6. Add environment variables in dashboard
7. Deploy

**Environment Variables**:
```
GOOGLE_API_KEY=your_gemini_key
HUGGINGFACE_TOKEN=your_hf_token
```

**Cost**: Free tier available (spins down after inactivity)

---

### Option 3: Railway

**Best for**: Quick deployment with Docker

**Steps**:
1. Install Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```

2. Deploy:
   ```bash
   railway login
   railway init
   railway up
   ```

3. Add environment variables:
   ```bash
   railway variables set GOOGLE_API_KEY=your_key
   railway variables set HUGGINGFACE_TOKEN=your_token
   ```

**Cost**: $5/month starter plan

---

### Option 4: Fly.io

**Best for**: Global edge deployment

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Launch app
fly launch

# Deploy
fly deploy

# Set secrets
fly secrets set GOOGLE_API_KEY=your_key
fly secrets set HUGGINGFACE_TOKEN=your_token
```

---

### Option 5: AWS/GCP/Azure

**Using Docker**:

1. Build and push to registry:
   ```bash
   docker build -t red-team-tool .
   docker tag red-team-tool your-registry/red-team-tool
   docker push your-registry/red-team-tool
   ```

2. Deploy to:
   - **AWS**: ECS/Fargate or App Runner
   - **GCP**: Cloud Run
   - **Azure**: Container Instances or App Service

---

## 🔑 API Key Management

### Option A: Environment Variables (Server-side)

Create `.env` file:
```bash
GOOGLE_API_KEY=AIza...
HUGGINGFACE_TOKEN=hf_...
OLLAMA_HOST=http://localhost:11434
```

### Option B: UI Input (Client-side)

1. Click "Settings" button in app
2. Enter API keys
3. Keys stored in browser localStorage
4. Keys sent with API requests (not stored on server)

**Recommended**: Use UI input for security and flexibility.

---

## 🧪 Testing Deployment

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "service": "Explainable Red Team Tool"
}
```

### Test API Endpoints

```bash
# Get models
curl http://localhost:8000/api/models

# Get prompts
curl http://localhost:8000/api/prompts
```

---

## 📊 Performance Optimization

### For Production:

1. **Enable Gunicorn** (multi-worker):
   ```bash
   gunicorn backend.main:app \
     --workers 4 \
     --worker-class uvicorn.workers.UvicornWorker \
     --bind 0.0.0.0:8000
   ```

2. **Add Redis cache** (optional):
   ```python
   # For caching model responses
   REDIS_URL=redis://localhost:6379
   ```

3. **Use CDN** for static files:
   - Upload `frontend/` to CDN
   - Update paths in `main.py`

---

## 🔒 Security Best Practices

1. **Never commit** `.env` file
2. **Use HTTPS** in production (Vercel/Render provide this)
3. **Rate limiting**:
   ```python
   # Add to backend/main.py
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   ```

4. **CORS**: Update allowed origins in production:
   ```python
   allow_origins=["https://your-domain.com"]
   ```

---

## 🐛 Troubleshooting

### Port already in use:
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn backend.main:app --port 8001
```

### Import errors:
```bash
# Ensure PYTHONPATH includes project root
export PYTHONPATH=/path/to/Explainable-Red-Team-Tool
```

### Ollama not connecting:
- Ensure Ollama is running: `ollama serve`
- Check host in `.env`: `OLLAMA_HOST=http://localhost:11434`
- For Docker: use `http://host.docker.internal:11434`

---

## 📝 Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_API_KEY` | No* | - | Gemini API key |
| `HUGGINGFACE_TOKEN` | No* | - | HuggingFace token |
| `OLLAMA_HOST` | No | `http://localhost:11434` | Ollama server URL |
| `PORT` | No | `8000` | Server port |

*Can be provided via UI instead

---

## 🎉 Success!

Your Explainable Red Team Tool should now be running!

- **Local**: http://localhost:8000
- **Production**: Your deployed URL

For support, check the main README or create an issue.
