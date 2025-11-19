"""
Google Gemini API client with rate limiting and error handling.
Supports Gemini 2.5 Pro and Flash models via the free tier API.
"""

import asyncio
import time
from typing import Dict, Optional, List
from datetime import datetime
import os

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

from .base import ModelClient


class GeminiClient(ModelClient):
    """Client for Google Gemini models"""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash-exp",
        rpm_limit: int = 5
    ):
        """
        Initialize Gemini client

        Args:
            api_key: Google API key
            model: Model name (gemini-2.0-flash-exp, gemini-1.5-pro, etc.)
            rpm_limit: Requests per minute limit (default: 5 for free tier)
        """
        super().__init__(model_name=model)

        if not GENAI_AVAILABLE:
            raise ImportError(
                "google-generativeai is not installed. "
                "Install with: pip install google-generativeai"
            )

        self.api_key = api_key
        self.rpm_limit = rpm_limit
        self.request_times: List[float] = []

        # Configure the API
        genai.configure(api_key=self.api_key)

        # Initialize the model
        try:
            self.model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            raise ValueError(f"Failed to initialize Gemini model '{model}': {str(e)}")

    def _enforce_rate_limit(self):
        """Enforce rate limiting using a sliding window"""
        current_time = time.time()

        # Remove requests older than 1 minute
        self.request_times = [
            t for t in self.request_times
            if current_time - t < 60
        ]

        # If we're at the limit, wait
        if len(self.request_times) >= self.rpm_limit:
            oldest_request = self.request_times[0]
            wait_time = 60 - (current_time - oldest_request)
            if wait_time > 0:
                time.sleep(wait_time + 0.1)  # Add small buffer

        # Record this request
        self.request_times.append(time.time())

    async def generate(self, prompt: str, **kwargs) -> Dict:
        """
        Generate response from Gemini model

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters (temperature, top_p, etc.)

        Returns:
            Response dictionary with model output and metadata
        """
        start_time = time.time()

        try:
            # Enforce rate limiting
            self._enforce_rate_limit()

            # Generation config
            generation_config = {
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.95),
                "top_k": kwargs.get("top_k", 40),
                "max_output_tokens": kwargs.get("max_output_tokens", 2048),
            }

            # Safety settings (minimal restrictions for red teaming)
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                },
            ]

            # Generate response
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )

            latency_ms = (time.time() - start_time) * 1000

            # Extract response text
            try:
                response_text = response.text
            except ValueError as e:
                # Response blocked by safety filters
                response_text = f"[BLOCKED: {str(e)}]"

            # Extract metadata
            metadata = {
                "finish_reason": getattr(response.candidates[0], 'finish_reason', None) if response.candidates else None,
                "safety_ratings": [
                    {
                        "category": rating.category.name if hasattr(rating.category, 'name') else str(rating.category),
                        "probability": rating.probability.name if hasattr(rating.probability, 'name') else str(rating.probability)
                    }
                    for rating in response.candidates[0].safety_ratings
                ] if response.candidates and hasattr(response.candidates[0], 'safety_ratings') else []
            }

            # Estimate token count
            token_count = None
            if hasattr(response, 'usage_metadata'):
                metadata['usage'] = {
                    'prompt_tokens': response.usage_metadata.prompt_token_count,
                    'completion_tokens': response.usage_metadata.candidates_token_count,
                    'total_tokens': response.usage_metadata.total_token_count
                }
                token_count = response.usage_metadata.total_token_count

            return {
                "response": response_text,
                "model": self.model_name,
                "latency_ms": latency_ms,
                "tokens": token_count,
                "metadata": metadata,
                "timestamp": datetime.utcnow().isoformat(),
                "error": None
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
        """Check if Gemini API is available"""
        try:
            # Try a simple test generation
            test_response = self.model.generate_content(
                "Hi",
                generation_config={"max_output_tokens": 10}
            )
            return True
        except Exception:
            return False

    def get_embeddings(self, text: str) -> Optional[List[float]]:
        """
        Get embeddings using Gemini embedding model

        Args:
            text: Input text

        Returns:
            Embedding vector or None
        """
        try:
            # Use Gemini's embedding model
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            print(f"Error getting embeddings: {e}")
            return None
