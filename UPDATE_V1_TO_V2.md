# 🔄 Updating from v1.0 to v2.0 on Local Machine

This guide helps you update your local v1.0 installation to the new v2.0 web app version.

---

## 📋 Quick Update Commands

### Step 1: Check Your Current Status

```bash
# Navigate to your project directory
cd path/to/Explainable-Red-Team-Tool

# Check which branch you're on
git branch

# Check current status
git status
```

### Step 2: Save Any Local Changes (If You Have Them)

**If you have uncommitted changes:**
```bash
# Option A: Commit your changes
git add .
git commit -m "My local changes before v2.0 update"

# Option B: Stash your changes (temporary save)
git stash save "My local changes"
```

**If you have no changes (clean working directory):**
Skip this step and continue to Step 3.

### Step 3: Pull the Latest v2.0 Changes

```bash
# Fetch all latest changes from GitHub
git fetch origin

# Checkout the v2.0 branch
git checkout claude/red-team-tool-free-apis-01NnhtNhifWG3qiEm2iF4YY8

# Pull the latest changes
git pull origin claude/red-team-tool-free-apis-01NnhtNhifWG3qiEm2iF4YY8
```

**You should see:**
```
Updating 5a23c67..6ab8aa1
Fast-forward
 backend/main.py                    |   68 ++
 backend/requirements.txt           |   30 +
 backend/routers/evaluation.py      |  170 ++++
 frontend/index.html                |  386 +++++++
 frontend/css/style.css             |  543 ++++++++++
 frontend/js/app.js                 |  275 +++++
 data/prompts/jailbreaks.json       | 1308 +++++++++++++++++++++---
 ...
 18 files changed, 3981 insertions(+)
```

### Step 4: Install/Update Dependencies

The v2.0 requires FastAPI instead of Streamlit. Update your dependencies:

```bash
# If you're using a virtual environment (recommended):
# First, activate it
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate     # On Windows

# Install/update dependencies
pip install -r backend/requirements.txt
```

**Note:** This will install FastAPI, uvicorn, and other new dependencies.

---

## 🚀 Running v2.0 (Changed from v1.0!)

### v1.0 Used Streamlit (OLD - Don't Use):
```bash
# ❌ OLD WAY - Don't use this anymore
streamlit run src/app.py
```

### v2.0 Uses FastAPI (NEW - Use This):
```bash
# ✅ NEW WAY
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Then open your browser to: **http://localhost:8000**

---

## 🎨 What's Different in v2.0?

### Major Changes:
1. **No more Streamlit** → Now using **FastAPI backend + HTML/CSS/JS frontend**
2. **New animated UI** → Gradient mesh background with glassmorphism
3. **API keys in UI** → No need to edit `.env` file (optional)
4. **102 prompts** → Expanded from 25 prompts (+310% growth)
5. **Real-time streaming** → See evaluation progress live
6. **Custom prompts** → Add your own prompts via UI

### File Structure Changes:
```
NEW in v2.0:
✨ backend/                 # FastAPI application
✨ frontend/               # HTML/CSS/JS UI
✨ CODESPACES_SETUP.md    # GitHub Codespaces guide
✨ QUICKSTART.md          # Quick start guide
✨ DEPLOYMENT_GUIDE.md    # Cloud deployment guide

STILL THERE (from v1.0):
✓ src/                    # Core modules (API clients, evaluator)
✓ data/prompts/           # Prompt library (now 102 prompts!)
✓ tests/                  # Unit tests
✓ README.md              # Main documentation
```

---

## 🔧 Troubleshooting

### Issue 1: "ModuleNotFoundError: No module named 'fastapi'"

**Solution:**
```bash
# Make sure you're in the project directory
cd path/to/Explainable-Red-Team-Tool

# Install dependencies
pip install -r backend/requirements.txt
```

### Issue 2: Git Merge Conflicts

If you see merge conflicts:

```bash
# See which files have conflicts
git status

# Option A: Keep the v2.0 version (recommended if you didn't change much)
git checkout --theirs .
git add .
git commit -m "Resolved conflicts, keeping v2.0 changes"

# Option B: Manually resolve conflicts
# Open the conflicted files in VS Code
# VS Code will show conflict markers - choose which version to keep
```

### Issue 3: Port 8000 Already in Use

```bash
# Find what's using port 8000
lsof -i :8000          # On Mac/Linux
netstat -ano | findstr :8000  # On Windows

# Kill the process or use a different port
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8080
```

### Issue 4: "Cannot Find Module 'backend.main'"

**Make sure you're in the project root directory:**
```bash
# Check current directory
pwd

# Should show something like: /Users/you/Explainable-Red-Team-Tool
# If not, navigate to it:
cd path/to/Explainable-Red-Team-Tool

# Then run uvicorn
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Issue 5: Python Version Issues

v2.0 requires **Python 3.10+**:

```bash
# Check your Python version
python --version

# Should show: Python 3.10.x or higher
# If not, upgrade Python or use a newer virtual environment
```

---

## 🔑 API Key Configuration

### Option 1: Use the UI (Recommended - NEW in v2.0!)

1. Start the server: `uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000`
2. Open browser: `http://localhost:8000`
3. Click **⚙️ Settings** button (top-right)
4. Enter your API keys:
   - **Gemini API Key**: From https://makersuite.google.com/app/apikey (free)
   - **HuggingFace Token**: From https://huggingface.co/settings/tokens (free)
5. Click **"Save Keys"**

The keys are stored in your browser's localStorage (client-side).

### Option 2: Use .env File (OLD way - still works)

```bash
# Create/edit .env file in project root
cat > .env << 'EOF'
GOOGLE_API_KEY=your_actual_gemini_key_here
HUGGINGFACE_TOKEN=your_actual_hf_token_here
EOF
```

---

## ✅ Verify the Update

Run the verification script to ensure everything is set up correctly:

```bash
python verify_setup.py
```

You should see:
```
✓ ALL CHECKS PASSED!
✨ The Explainable Red Team Tool v2.0 is ready!
```

---

## 📚 New Documentation to Read

After updating, check out these new guides:

1. **QUICKSTART.md** - 3-minute setup and first evaluation
2. **CODESPACES_SETUP.md** - Running in GitHub Codespaces
3. **DEPLOYMENT_GUIDE.md** - Deploy to Vercel, Render, Railway
4. **VERIFICATION_REPORT.md** - Complete v2.0 feature list

---

## 🎯 Quick Test After Update

### 1. Start the server:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Open browser to http://localhost:8000

### 3. You should see:
- ✨ **Animated gradient mesh background** (gold & teal gradients flowing)
- 🎨 **Glassmorphism cards** with blur effects
- 📊 **5 tabs**: Overview, Analysis, Interpretability, Prompts, Results
- ⚙️ **Settings button** for API keys
- 🎯 **102 prompts** in the Prompts tab

### 4. Test the UI:
- Click **Prompts** tab → See all 102 prompts
- Click **Settings** → Enter API keys (or skip for now)
- Select a model → Run evaluation

---

## 🔄 Rollback to v1.0 (If Needed)

If you want to go back to v1.0 for any reason:

```bash
# Checkout the v1.0 commit
git checkout 5a23c67

# Or checkout by tag if tagged
git checkout v1.0

# Reinstall v1.0 dependencies
pip install -r requirements.txt

# Run v1.0 (Streamlit)
streamlit run src/app.py
```

---

## 📞 Need Help?

1. **Run verification**: `python verify_setup.py`
2. **Check logs**: Look at terminal output when running uvicorn
3. **Read guides**: `QUICKSTART.md` and `CODESPACES_SETUP.md`
4. **View changes**: `git log --oneline` to see all commits

---

## 🎉 You're All Set!

Your local installation is now updated to v2.0! Enjoy the new features:
- 🎨 Beautiful animated UI
- ⚡ Faster async evaluation
- 📊 Real-time progress tracking
- 🚀 102 adversarial prompts
- 🔑 Easy API key management

Start testing: `uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000`

Happy testing! 🚀
