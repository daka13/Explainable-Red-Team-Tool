"""
Models router - Handles model availability and configuration
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import sys
from pathlib import Path

# Add parent directory to import src modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.api_clients import GeminiClient, OllamaClient, HuggingFaceClient

router = APIRouter()

class ModelCheck(BaseModel):
    """Request to check model availability"""
    model_type: str  # "gemini", "ollama", "huggingface"
    model_name: str
    api_key: Optional[str] = None

class ModelStatus(BaseModel):
    """Model availability status"""
    model_name: str
    model_type: str
    available: bool
    error: Optional[str] = None

@router.get("/models")
async def get_available_models():
    """Get list of all available models"""
    models = {
        "gemini": [
            {
                "name": "gemini-2.0-flash-exp",
                "display_name": "Gemini 2.0 Flash",
                "description": "Fast, efficient responses",
                "requires_key": True
            },
            {
                "name": "gemini-1.5-pro",
                "display_name": "Gemini 1.5 Pro",
                "description": "More capable, slower",
                "requires_key": True
            },
            {
                "name": "gemini-1.5-flash",
                "display_name": "Gemini 1.5 Flash",
                "description": "Balanced speed and capability",
                "requires_key": True
            }
        ],
        "ollama": [
            {
                "name": "llama3.1:8b",
                "display_name": "Llama 3.1 8B",
                "description": "Meta's latest open model",
                "requires_key": False
            },
            {
                "name": "mistral:7b",
                "display_name": "Mistral 7B",
                "description": "Efficient open-source model",
                "requires_key": False
            }
        ],
        "huggingface": [
            {
                "name": "mistralai/Mistral-7B-Instruct-v0.2",
                "display_name": "HF Mistral-7B-Instruct",
                "description": "Open-source via HuggingFace",
                "requires_key": True
            }
        ]
    }

    return models

@router.post("/models/check")
async def check_model_availability(request: ModelCheck) -> ModelStatus:
    """Check if a specific model is available"""
    try:
        if request.model_type == "gemini":
            if not request.api_key:
                return ModelStatus(
                    model_name=request.model_name,
                    model_type=request.model_type,
                    available=False,
                    error="API key required"
                )

            try:
                client = GeminiClient(api_key=request.api_key, model=request.model_name)
                available = client.is_available()
                return ModelStatus(
                    model_name=request.model_name,
                    model_type=request.model_type,
                    available=available,
                    error=None if available else "Model not accessible"
                )
            except Exception as e:
                return ModelStatus(
                    model_name=request.model_name,
                    model_type=request.model_type,
                    available=False,
                    error=str(e)
                )

        elif request.model_type == "ollama":
            try:
                client = OllamaClient(model=request.model_name)
                available = client.is_available()
                return ModelStatus(
                    model_name=request.model_name,
                    model_type=request.model_type,
                    available=available,
                    error=None if available else "Ollama server not running or model not downloaded"
                )
            except Exception as e:
                return ModelStatus(
                    model_name=request.model_name,
                    model_type=request.model_type,
                    available=False,
                    error=str(e)
                )

        elif request.model_type == "huggingface":
            if not request.api_key:
                return ModelStatus(
                    model_name=request.model_name,
                    model_type=request.model_type,
                    available=False,
                    error="API token required"
                )

            try:
                client = HuggingFaceClient(token=request.api_key, model=request.model_name)
                available = client.is_available()
                return ModelStatus(
                    model_name=request.model_name,
                    model_type=request.model_type,
                    available=available,
                    error=None if available else "Model not accessible"
                )
            except Exception as e:
                return ModelStatus(
                    model_name=request.model_name,
                    model_type=request.model_type,
                    available=False,
                    error=str(e)
                )
        else:
            raise HTTPException(status_code=400, detail="Invalid model type")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
