# 🚀 Running in GitHub Codespaces

This guide shows you how to run the Explainable Red Team Tool in GitHub Codespaces.

---

## Quick Start (3 Steps)

### Step 1: Install Dependencies

```bash
# Install Python dependencies
pip install -r backend/requirements.txt
```

**Note**: This may take 2-3 minutes. You'll see warnings about running as root - that's normal in Codespaces.

### Step 2: Configure API Keys (Optional but Recommended)

You have 2 options:

#### Option A: Use the UI (Recommended)
Skip this step and configure API keys directly in the web interface after starting the app.

#### Option B: Use Environment Variables
```bash
# Create .env file
cat > .env << 'EOF'
GOOGLE_API_KEY=your_gemini_api_key_here
HUGGINGFACE_TOKEN=your_hf_token_here
EOF
```

**Where to get API keys:**
- **Gemini API Key**: https://makersuite.google.com/app/apikey (Free, no credit card)
- **HuggingFace Token**: https://huggingface.co/settings/tokens (Free account)

### Step 3: Start the Server

```bash
# Start the FastAPI server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## 🌐 Accessing the Application

### In GitHub Codespaces:

1. **Automatic Port Forwarding**: When you start the server, Codespaces automatically detects port 8000
2. **Look for the notification**: A popup will appear saying "Your application running on port 8000 is available"
3. **Click "Open in Browser"** or **"Make Public"** to access the app

### Manual Port Forwarding:

If the popup doesn't appear:

1. Click the **"PORTS"** tab in the bottom panel (next to Terminal)
2. Find port `8000` in the list
3. Right-click and select **"Open in Browser"**
4. Or hover over the port and click the 🌐 globe icon

### Alternative: Use the Ports Panel

```bash
# After starting the server, check forwarded ports
# Look at the PORTS tab in VS Code bottom panel
# You'll see: 8000 | FastAPI | http://127.0.0.1:8000
```

---

## 🎨 Using the Application

### 1. Configure API Keys (First Time)

Once the app opens in your browser:

1. Click the **⚙️ Settings** button in the top-right
2. Enter your API keys:
   - **Gemini API Key**: From Google AI Studio
   - **HuggingFace Token**: From HuggingFace settings
3. Click **"Save Keys"** - They'll be stored in your browser's localStorage

### 2. Select Models

In the left sidebar:
- ✅ Check **Gemini 2.0 Flash** (recommended - fast and free)
- ✅ Check **Gemini 1.5 Pro** (for comparison)
- Optional: Check **HuggingFace models** (if you have a token)

### 3. Select Prompts

- Use the **Category** filter (Jailbreak, Bias, Harmful Content, etc.)
- Use the **Difficulty** filter (Easy, Medium, Hard)
- Or click **"Select All"** to test with all 102 prompts

### 4. Run Evaluation

1. Click **"Run Evaluation"** button
2. Watch the real-time progress bar
3. View results in the **Analysis** tab with interactive charts

---

## 🔧 Troubleshooting

### Issue 1: Port 8000 Already in Use

```bash
# Kill existing process
pkill -f uvicorn

# Or use a different port
uvicorn backend.main:app --host 0.0.0.0 --port 8080 --reload
```

### Issue 2: Module Not Found Errors

```bash
# Ensure you're in the project directory
cd /home/user/Explainable-Red-Team-Tool

# Reinstall dependencies
pip install -r backend/requirements.txt
```

### Issue 3: Permission Denied

```bash
# This shouldn't happen in Codespaces, but if it does:
chmod +x backend/main.py
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Issue 4: Can't Access the App

1. **Check the PORTS tab** - Make sure port 8000 is visible
2. **Make port public** - Right-click port 8000 → "Port Visibility" → "Public"
3. **Check firewall** - Codespaces should handle this automatically

### Issue 5: API Key Errors

If you see "Invalid API key" errors:
1. Verify your keys are correct at the provider websites
2. For Gemini: Make sure you're using the correct API key format (starts with `AIza`)
3. For HuggingFace: Make sure the token starts with `hf_`

---

## 🎯 Quick Testing Without API Keys

You can explore the UI without API keys:
1. Browse the **Prompts** tab to see all 102 adversarial prompts
2. View the prompt categories and difficulties
3. Test the custom prompt input feature
4. Explore the UI design (animated gradient mesh background)

To actually run evaluations, you'll need at least one API key (Gemini is free and easiest).

---

## 📊 Features to Try

### 1. Test Refusal Detection
- Select prompts from the "Jailbreak" category
- Run evaluation against Gemini models
- See which prompts trigger refusals

### 2. Compare Models
- Select multiple models (Gemini 2.0 Flash vs 1.5 Pro)
- Run the same prompts against both
- Compare refusal rates in the Analysis tab

### 3. Custom Prompts
- Click **"Custom Prompt"** button
- Write your own test prompt
- Select category and difficulty
- Add to evaluation queue

### 4. Export Results
- After running evaluation, click **"Export to CSV"** or **"Export to JSON"**
- Download results for further analysis

### 5. Interactive Charts
- View refusal rates by model (bar chart)
- Analyze latency distributions (histogram)
- Explore category-wise performance (heatmap)
- Compare overall metrics (radar chart)

---

## 🐳 Alternative: Run with Docker (Advanced)

If you prefer Docker in Codespaces:

```bash
# Build the image
docker build -t red-team-tool .

# Run the container
docker run -p 8000:8000 \
  -e GOOGLE_API_KEY="your_key_here" \
  -e HUGGINGFACE_TOKEN="your_token_here" \
  red-team-tool
```

Then access via the PORTS tab as described above.

---

## 🛑 Stopping the Server

Press **CTRL+C** in the terminal where uvicorn is running.

Or to kill all uvicorn processes:
```bash
pkill -f uvicorn
```

---

## 💡 Pro Tips

### 1. Development Mode
The `--reload` flag automatically restarts the server when you edit code:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. View Logs
Server logs appear in the terminal. Watch for:
- API requests: `INFO: 127.0.0.1 - "POST /api/evaluate/stream HTTP/1.1" 200 OK`
- Errors: `ERROR: Exception in ASGI application`

### 3. API Documentation
Visit the auto-generated API docs:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 4. Health Check
Test if the server is running:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy","version":"2.0.0","service":"Explainable Red Team Tool"}
```

### 5. Keep Codespace Alive
Codespaces timeout after inactivity. To keep it alive:
- Keep the browser tab open
- Or use the terminal periodically

---

## 📝 Environment Details

**Your Codespace Environment:**
- **OS**: Linux (Ubuntu-based)
- **Python**: 3.11+
- **Architecture**: x86_64
- **Resources**: 2-4 cores, 8-16 GB RAM (depends on plan)

**Application Stack:**
- **Backend**: FastAPI (async Python web framework)
- **Frontend**: HTML/CSS/JavaScript (served by FastAPI)
- **API Clients**: Google Gemini, HuggingFace, Ollama (optional)

---

## 🎓 Learning Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Gemini API Docs**: https://ai.google.dev/docs
- **HuggingFace API**: https://huggingface.co/docs/api-inference
- **Project README**: See `README.md` in project root

---

## 🆘 Need Help?

1. **Check logs**: Look at the uvicorn output in the terminal
2. **Verify setup**: Run `python verify_setup.py` to check all files
3. **Read docs**: See `QUICKSTART.md` for general setup
4. **GitHub Issues**: Report bugs at the project repository

---

## 🎉 You're All Set!

Your Explainable Red Team Tool is now running in GitHub Codespaces. Start testing AI models for adversarial vulnerabilities!

**Next Steps:**
1. Get your free Gemini API key
2. Configure it in the Settings modal
3. Run your first evaluation
4. Explore the 102 adversarial prompts
5. Compare model behaviors

Happy testing! 🚀
