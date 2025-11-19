"""
HuggingFace Inference API client.
Supports free tier models like Mistral-7B-Instruct.
"""

import asyncio
import time
from typing import Dict, Optional, List
from datetime import datetime
import aiohttp

from .base import ModelClient


class HuggingFaceClient(ModelClient):
    """Client for HuggingFace Inference API"""

    def __init__(
        self,
        token: str,
        model: str = "mistralai/Mistral-7B-Instruct-v0.2",
        monthly_limit: int = 1000
    ):
        """
        Initialize HuggingFace client

        Args:
            token: HuggingFace API token
            model: Model identifier on HuggingFace
            monthly_limit: Request limit per month (free tier: 1000)
        """
        super().__init__(model_name=model)
        self.token = token
        self.monthly_limit = monthly_limit
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"
        self.embed_api_url = "https://api-inference.huggingface.co/pipeline/feature-extraction"

    async def generate(self, prompt: str, **kwargs) -> Dict:
        """
        Generate response from HuggingFace model

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Response dictionary with model output and metadata
        """
        start_time = time.time()

        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }

            payload = {
                "inputs": prompt,
                "parameters": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                    "max_new_tokens": kwargs.get("max_tokens", 512),
                    "return_full_text": False,
                    "do_sample": True,
                },
                "options": {
                    "wait_for_model": True,
                    "use_cache": False
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    latency_ms = (time.time() - start_time) * 1000

                    if response.status == 200:
                        data = await response.json()

                        # Extract response text
                        if isinstance(data, list) and len(data) > 0:
                            response_text = data[0].get("generated_text", "")
                        elif isinstance(data, dict):
                            response_text = data.get("generated_text", "")
                        else:
                            response_text = str(data)

                        return {
                            "response": response_text,
                            "model": self.model_name,
                            "latency_ms": latency_ms,
                            "tokens": None,  # HF API doesn't always return token counts
                            "metadata": {"raw_response": data},
                            "timestamp": datetime.utcnow().isoformat(),
                            "error": None
                        }

                    elif response.status == 503:
                        # Model is loading
                        error_data = await response.json()
                        estimated_time = error_data.get("estimated_time", "unknown")

                        return {
                            "response": "",
                            "model": self.model_name,
                            "latency_ms": latency_ms,
                            "tokens": None,
                            "metadata": {},
                            "timestamp": datetime.utcnow().isoformat(),
                            "error": f"Model loading (estimated time: {estimated_time}s)"
                        }

                    elif response.status == 429:
                        # Rate limited
                        return {
                            "response": "",
                            "model": self.model_name,
                            "latency_ms": latency_ms,
                            "tokens": None,
                            "metadata": {},
                            "timestamp": datetime.utcnow().isoformat(),
                            "error": "Rate limit exceeded"
                        }

                    else:
                        error_text = await response.text()
                        return {
                            "response": "",
                            "model": self.model_name,
                            "latency_ms": latency_ms,
                            "tokens": None,
                            "metadata": {},
                            "timestamp": datetime.utcnow().isoformat(),
                            "error": f"HTTP {response.status}: {error_text}"
                        }

        except asyncio.TimeoutError:
            latency_ms = (time.time() - start_time) * 1000
            return {
                "response": "",
                "model": self.model_name,
                "latency_ms": latency_ms,
                "tokens": None,
                "metadata": {},
                "timestamp": datetime.utcnow().isoformat(),
                "error": "Request timeout (>120s)"
            }

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return {
                "response": "",
                "model": self.model_name,
                "latency_ms": latency_ms,
                "tokens": None,
                "metadata": {},
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }

    def is_available(self) -> bool:
        """Check if HuggingFace API is available"""
        try:
            import requests

            headers = {"Authorization": f"Bearer {self.token}"}

            # Try to check model status
            response = requests.get(
                self.api_url,
                headers=headers,
                timeout=10
            )

            # 200 or 503 (loading) are both acceptable
            return response.status_code in [200, 503]

        except Exception:
            return False

    async def get_embeddings(self, text: str) -> Optional[List[float]]:
        """
        Get embeddings from HuggingFace model

        Args:
            text: Input text

        Returns:
            Embedding vector or None
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }

            # Use a dedicated embedding model
            embed_model = "sentence-transformers/all-MiniLM-L6-v2"
            url = f"https://api-inference.huggingface.co/models/{embed_model}"

            payload = {
                "inputs": text,
                "options": {"wait_for_model": True}
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Handle different response formats
                        if isinstance(data, list):
                            if isinstance(data[0], list):
                                return data[0]
                            else:
                                return data
                        return None
                    else:
                        return None

        except Exception as e:
            print(f"Error getting embeddings from HuggingFace: {e}")
            return None
