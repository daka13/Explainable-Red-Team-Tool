"""
Ollama client for running local models.
Supports Llama 3.1, Mistral, and other Ollama-compatible models.
"""

import asyncio
import time
from typing import Dict, Optional, List
from datetime import datetime
import aiohttp

from .base import ModelClient


class OllamaClient(ModelClient):
    """Client for Ollama local models"""

    def __init__(
        self,
        model: str = "llama3.1:8b",
        host: str = "http://localhost:11434"
    ):
        """
        Initialize Ollama client

        Args:
            model: Model name (llama3.1:8b, mistral:7b, etc.)
            host: Ollama server host URL
        """
        super().__init__(model_name=model)
        self.host = host.rstrip('/')
        self.api_url = f"{self.host}/api/generate"
        self.embed_url = f"{self.host}/api/embeddings"
        self.tags_url = f"{self.host}/api/tags"

    async def generate(self, prompt: str, **kwargs) -> Dict:
        """
        Generate response from Ollama model

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Response dictionary with model output and metadata
        """
        start_time = time.time()

        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                    "top_k": kwargs.get("top_k", 40),
                    "num_predict": kwargs.get("max_tokens", 2048),
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        latency_ms = (time.time() - start_time) * 1000

                        response_text = data.get("response", "")

                        # Extract metadata
                        metadata = {
                            "context": data.get("context"),
                            "total_duration": data.get("total_duration"),
                            "load_duration": data.get("load_duration"),
                            "prompt_eval_count": data.get("prompt_eval_count"),
                            "eval_count": data.get("eval_count"),
                            "eval_duration": data.get("eval_duration"),
                        }

                        # Calculate total tokens
                        prompt_tokens = data.get("prompt_eval_count", 0)
                        completion_tokens = data.get("eval_count", 0)
                        total_tokens = prompt_tokens + completion_tokens

                        return {
                            "response": response_text,
                            "model": self.model_name,
                            "latency_ms": latency_ms,
                            "tokens": total_tokens,
                            "metadata": metadata,
                            "timestamp": datetime.utcnow().isoformat(),
                            "error": None
                        }
                    else:
                        error_text = await response.text()
                        latency_ms = (time.time() - start_time) * 1000

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
        """Check if Ollama server is available and model is downloaded"""
        try:
            import requests

            # Check if server is running
            response = requests.get(self.tags_url, timeout=5)
            if response.status_code != 200:
                return False

            # Check if our specific model is available
            data = response.json()
            models = data.get("models", [])
            model_names = [m.get("name") for m in models]

            return self.model_name in model_names

        except Exception:
            return False

    async def get_embeddings(self, text: str) -> Optional[List[float]]:
        """
        Get embeddings from Ollama model

        Args:
            text: Input text

        Returns:
            Embedding vector or None
        """
        try:
            payload = {
                "model": self.model_name,
                "prompt": text
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.embed_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("embedding")
                    else:
                        return None

        except Exception as e:
            print(f"Error getting embeddings from Ollama: {e}")
            return None

    async def pull_model(self) -> bool:
        """
        Pull/download the model if not already available

        Returns:
            True if successful, False otherwise
        """
        try:
            pull_url = f"{self.host}/api/pull"
            payload = {"name": self.model_name}

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    pull_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=600)  # 10 min for downloads
                ) as response:
                    if response.status == 200:
                        # Stream the response to show progress
                        async for line in response.content:
                            # Could parse progress here if needed
                            pass
                        return True
                    else:
                        return False

        except Exception as e:
            print(f"Error pulling model: {e}")
            return False
