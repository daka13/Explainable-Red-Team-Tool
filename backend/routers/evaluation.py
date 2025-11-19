"""
Evaluation router - Handles adversarial testing execution
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to import src modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.api_clients import GeminiClient, OllamaClient, HuggingFaceClient, ModelClient
from src.adversarial_prompts import AdversarialPrompt
from src.evaluator import Evaluator
import pandas as pd

router = APIRouter()

class ModelConfig(BaseModel):
    """Configuration for a model"""
    type: str  # "gemini", "ollama", "huggingface"
    name: str
    api_key: Optional[str] = None

class PromptData(BaseModel):
    """Prompt to evaluate"""
    id: str
    category: str
    difficulty: str
    prompt: str
    expected_behavior: str
    description: str
    tags: List[str]

class EvaluationRequest(BaseModel):
    """Request to run evaluation"""
    models: List[ModelConfig]
    prompts: List[PromptData]
    api_keys: Optional[Dict[str, str]] = None

class EvaluationResponse(BaseModel):
    """Response from evaluation"""
    status: str
    total_tests: int
    results: List[Dict[str, Any]]

def create_client(model_config: ModelConfig) -> ModelClient:
    """Create appropriate model client based on config"""
    if model_config.type == "gemini":
        if not model_config.api_key:
            raise ValueError("API key required for Gemini")
        return GeminiClient(api_key=model_config.api_key, model=model_config.name)

    elif model_config.type == "ollama":
        return OllamaClient(model=model_config.name)

    elif model_config.type == "huggingface":
        if not model_config.api_key:
            raise ValueError("API token required for HuggingFace")
        return HuggingFaceClient(token=model_config.api_key, model=model_config.name)

    else:
        raise ValueError(f"Unknown model type: {model_config.type}")

def prompt_dict_to_object(prompt_data: PromptData) -> AdversarialPrompt:
    """Convert prompt dict to AdversarialPrompt object"""
    return AdversarialPrompt(
        id=prompt_data.id,
        category=prompt_data.category,
        difficulty=prompt_data.difficulty,
        prompt=prompt_data.prompt,
        expected_behavior=prompt_data.expected_behavior,
        description=prompt_data.description,
        tags=prompt_data.tags
    )

@router.post("/evaluate")
async def run_evaluation(request: EvaluationRequest):
    """Run adversarial evaluation"""
    try:
        # Create clients
        clients = []
        for model_config in request.models:
            try:
                client = create_client(model_config)
                clients.append(client)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to initialize {model_config.name}: {str(e)}"
                )

        if not clients:
            raise HTTPException(status_code=400, detail="No valid models configured")

        # Convert prompts
        prompts = [prompt_dict_to_object(p) for p in request.prompts]

        if not prompts:
            raise HTTPException(status_code=400, detail="No prompts provided")

        # Create evaluator
        evaluator = Evaluator(clients)

        # Run evaluation
        results = await evaluator.evaluate_batch(prompts, show_progress=False)

        # Convert results to dict
        results_dict = [r.to_dict() for r in results]

        return EvaluationResponse(
            status="completed",
            total_tests=len(results_dict),
            results=results_dict
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluate/stream")
async def run_evaluation_stream(request: EvaluationRequest):
    """Run evaluation with streaming results"""
    async def event_generator():
        try:
            # Create clients
            clients = []
            for model_config in request.models:
                try:
                    client = create_client(model_config)
                    clients.append(client)
                    yield f"data: {json.dumps({'type': 'status', 'message': f'Connected to {model_config.name}'})}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'type': 'error', 'message': f'Failed to connect to {model_config.name}: {str(e)}'})}\n\n"

            # Convert prompts
            prompts = [prompt_dict_to_object(p) for p in request.prompts]

            total_tests = len(clients) * len(prompts)
            yield f"data: {json.dumps({'type': 'info', 'total_tests': total_tests})}\n\n"

            # Create evaluator
            evaluator = Evaluator(clients)

            # Run evaluation with progress updates
            completed = 0
            for client in clients:
                for prompt in prompts:
                    result = await evaluator.evaluate_single(client, prompt)
                    completed += 1

                    # Send result
                    yield f"data: {json.dumps({'type': 'result', 'data': result.to_dict(), 'progress': completed / total_tests})}\n\n"

            # Send completion
            yield f"data: {json.dumps({'type': 'complete', 'total': completed})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/evaluate/export")
async def export_results(results: List[Dict[str, Any]], format: str = "csv"):
    """Export evaluation results"""
    try:
        df = pd.DataFrame(results)

        if format == "csv":
            csv_data = df.to_csv(index=False)
            return StreamingResponse(
                iter([csv_data]),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
            )
        elif format == "json":
            json_data = df.to_json(orient="records", indent=2)
            return StreamingResponse(
                iter([json_data]),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"}
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Use 'csv' or 'json'")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
