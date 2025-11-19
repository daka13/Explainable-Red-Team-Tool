"""
Prompts router - Handles adversarial prompt library
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys
from pathlib import Path

# Add parent directory to import src modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.adversarial_prompts import PromptLibrary, AdversarialPrompt

router = APIRouter()

# Load prompt library
try:
    prompt_library = PromptLibrary()
except Exception as e:
    print(f"Warning: Could not load prompt library: {e}")
    prompt_library = None

class PromptFilter(BaseModel):
    """Filter criteria for prompts"""
    categories: Optional[List[str]] = None
    difficulties: Optional[List[str]] = None
    tags: Optional[List[str]] = None

class CustomPrompt(BaseModel):
    """Custom user-provided prompt"""
    prompt: str
    category: str = "custom"
    difficulty: str = "medium"
    description: str = ""
    tags: List[str] = []

@router.get("/prompts")
async def get_all_prompts():
    """Get all prompts from the library"""
    if not prompt_library:
        raise HTTPException(status_code=500, detail="Prompt library not loaded")

    prompts = [p.to_dict() for p in prompt_library.get_all()]
    return {
        "total": len(prompts),
        "prompts": prompts
    }

@router.post("/prompts/filter")
async def filter_prompts(filters: PromptFilter):
    """Filter prompts by criteria"""
    if not prompt_library:
        raise HTTPException(status_code=500, detail="Prompt library not loaded")

    filtered = prompt_library.filter(
        categories=filters.categories,
        difficulties=filters.difficulties,
        tags=filters.tags
    )

    return {
        "total": len(filtered),
        "prompts": [p.to_dict() for p in filtered]
    }

@router.get("/prompts/metadata")
async def get_prompts_metadata():
    """Get metadata about available prompts"""
    if not prompt_library:
        raise HTTPException(status_code=500, detail="Prompt library not loaded")

    return {
        "total_prompts": len(prompt_library),
        "categories": prompt_library.get_categories(),
        "difficulties": prompt_library.get_difficulties(),
        "tags": prompt_library.get_tags()
    }

@router.post("/prompts/validate")
async def validate_custom_prompts(prompts: List[CustomPrompt]):
    """Validate custom user prompts"""
    validated = []

    for i, prompt in enumerate(prompts):
        validated.append({
            "id": f"custom_{i+1}",
            "category": prompt.category,
            "difficulty": prompt.difficulty,
            "prompt": prompt.prompt,
            "expected_behavior": "unknown",
            "description": prompt.description or f"Custom prompt {i+1}",
            "tags": prompt.tags + ["custom"]
        })

    return {
        "total": len(validated),
        "prompts": validated
    }

@router.get("/prompts/categories/{category}")
async def get_prompts_by_category(category: str):
    """Get all prompts in a specific category"""
    if not prompt_library:
        raise HTTPException(status_code=500, detail="Prompt library not loaded")

    prompts = prompt_library.get_by_category(category)

    if not prompts:
        raise HTTPException(status_code=404, detail=f"No prompts found in category: {category}")

    return {
        "category": category,
        "total": len(prompts),
        "prompts": [p.to_dict() for p in prompts]
    }
