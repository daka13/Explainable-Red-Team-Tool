"""
FastAPI Backend for Explainable Red Team Tool
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
import sys
import os
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.append(str(Path(__file__).parent.parent))

from backend.routers import evaluation, models, prompts

# Create FastAPI app
app = FastAPI(
    title="Explainable Red Team Tool API",
    description="Multi-model adversarial testing with interpretability",
    version="2.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(evaluation.router, prefix="/api", tags=["evaluation"])
app.include_router(models.router, prefix="/api", tags=["models"])
app.include_router(prompts.router, prefix="/api", tags=["prompts"])

# Serve frontend static files
frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/assets", StaticFiles(directory=str(frontend_path / "assets")), name="assets")
app.mount("/css", StaticFiles(directory=str(frontend_path / "css")), name="css")
app.mount("/js", StaticFiles(directory=str(frontend_path / "js")), name="js")

@app.get("/")
async def read_root():
    """Serve the main HTML page"""
    return FileResponse(str(frontend_path / "index.html"))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "service": "Explainable Red Team Tool"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
