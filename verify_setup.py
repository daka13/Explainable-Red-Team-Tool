#!/usr/bin/env python3
"""
Verification script for Explainable Red Team Tool v2.0
Checks that all components are properly set up
"""

import os
import sys
from pathlib import Path
import json

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"✓ {description}: {filepath} ({size:,} bytes)")
        return True
    else:
        print(f"✗ {description}: {filepath} NOT FOUND")
        return False

def check_directory_structure():
    """Verify directory structure"""
    print("\n" + "="*60)
    print("DIRECTORY STRUCTURE VERIFICATION")
    print("="*60)

    required_dirs = [
        ("backend/", "Backend directory"),
        ("backend/routers/", "API routers"),
        ("backend/services/", "Backend services"),
        ("frontend/", "Frontend directory"),
        ("frontend/css/", "CSS styles"),
        ("frontend/js/", "JavaScript files"),
        ("src/", "Source modules"),
        ("src/api_clients/", "API clients"),
        ("data/prompts/", "Prompt library"),
        ("tests/", "Unit tests"),
    ]

    all_exist = True
    for dir_path, description in required_dirs:
        if os.path.exists(dir_path):
            print(f"✓ {description}: {dir_path}")
        else:
            print(f"✗ {description}: {dir_path} NOT FOUND")
            all_exist = False

    return all_exist

def check_backend_files():
    """Verify backend files"""
    print("\n" + "="*60)
    print("BACKEND FILES VERIFICATION")
    print("="*60)

    backend_files = [
        ("backend/main.py", "FastAPI main application"),
        ("backend/requirements.txt", "Backend dependencies"),
        ("backend/routers/__init__.py", "Routers init"),
        ("backend/routers/evaluation.py", "Evaluation router"),
        ("backend/routers/models.py", "Models router"),
        ("backend/routers/prompts.py", "Prompts router"),
    ]

    all_exist = True
    for filepath, description in backend_files:
        if not check_file_exists(filepath, description):
            all_exist = False

    return all_exist

def check_frontend_files():
    """Verify frontend files"""
    print("\n" + "="*60)
    print("FRONTEND FILES VERIFICATION")
    print("="*60)

    frontend_files = [
        ("frontend/index.html", "Main HTML file"),
        ("frontend/css/style.css", "Animated gradient mesh CSS"),
        ("frontend/js/api.js", "API communication"),
        ("frontend/js/charts.js", "Plotly visualizations"),
        ("frontend/js/app.js", "Main application logic"),
    ]

    all_exist = True
    for filepath, description in frontend_files:
        if not check_file_exists(filepath, description):
            all_exist = False

    return all_exist

def check_data_files():
    """Verify data files"""
    print("\n" + "="*60)
    print("DATA FILES VERIFICATION")
    print("="*60)

    data_files = [
        ("data/prompts/jailbreaks.json", "Adversarial prompts library"),
    ]

    all_exist = True
    for filepath, description in data_files:
        if not check_file_exists(filepath, description):
            all_exist = False
        else:
            # Count prompts
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        print(f"  → Contains {len(data)} prompts")
                        # Count categories
                        categories = set(p.get('category', 'unknown') for p in data)
                        print(f"  → {len(categories)} categories: {', '.join(sorted(categories))}")
            except Exception as e:
                print(f"  → Error reading prompts: {e}")

    return all_exist

def check_deployment_files():
    """Verify deployment configuration files"""
    print("\n" + "="*60)
    print("DEPLOYMENT FILES VERIFICATION")
    print("="*60)

    deployment_files = [
        ("Dockerfile", "Docker container configuration"),
        ("docker-compose.yml", "Docker Compose orchestration"),
        ("vercel.json", "Vercel deployment config"),
        ("render.yaml", "Render deployment config"),
    ]

    all_exist = True
    for filepath, description in deployment_files:
        if not check_file_exists(filepath, description):
            all_exist = False

    return all_exist

def check_documentation():
    """Verify documentation files"""
    print("\n" + "="*60)
    print("DOCUMENTATION VERIFICATION")
    print("="*60)

    doc_files = [
        ("README.md", "Main README"),
        ("QUICKSTART.md", "Quick start guide"),
        ("SETUP_GUIDE.md", "Detailed setup guide"),
        ("DEPLOYMENT_GUIDE.md", "Deployment guide"),
    ]

    all_exist = True
    for filepath, description in doc_files:
        if not check_file_exists(filepath, description):
            all_exist = False

    return all_exist

def check_code_metrics():
    """Calculate code metrics"""
    print("\n" + "="*60)
    print("CODE METRICS")
    print("="*60)

    total_lines = 0
    total_files = 0

    # Count Python files
    for ext in ['.py', '.js', '.html', '.css', '.json', '.md', '.yml', '.yaml']:
        count = 0
        lines = 0
        for root, dirs, files in os.walk('.'):
            # Skip venv, __pycache__, node_modules
            dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', 'node_modules', '.git']]
            for file in files:
                if file.endswith(ext):
                    count += 1
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            file_lines = len(f.readlines())
                            lines += file_lines
                    except:
                        pass

        if count > 0:
            print(f"  {ext:8s} files: {count:3d} ({lines:,} lines)")
            total_files += count
            total_lines += lines

    print(f"\n  Total files: {total_files}")
    print(f"  Total lines: {total_lines:,}")

def main():
    """Run all verifications"""
    print("\n" + "="*60)
    print("EXPLAINABLE RED TEAM TOOL v2.0 - VERIFICATION")
    print("="*60)

    os.chdir('/home/user/Explainable-Red-Team-Tool')

    results = []
    results.append(check_directory_structure())
    results.append(check_backend_files())
    results.append(check_frontend_files())
    results.append(check_data_files())
    results.append(check_deployment_files())
    results.append(check_documentation())

    check_code_metrics()

    # Final summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)

    if all(results):
        print("✓ ALL CHECKS PASSED!")
        print("\n✨ The Explainable Red Team Tool v2.0 is ready!")
        print("\nTo run the application:")
        print("  1. Install dependencies: pip install -r backend/requirements.txt")
        print("  2. Start server: uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000")
        print("  3. Open browser: http://localhost:8000")
        print("\nFor detailed setup: See QUICKSTART.md")
        print("For deployment: See DEPLOYMENT_GUIDE.md")
        return 0
    else:
        print("✗ Some checks failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
