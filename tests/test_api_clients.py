"""
Unit tests for API clients
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from src.api_clients import ModelClient, GeminiClient, OllamaClient, HuggingFaceClient


class TestBaseClient:
    """Test the base ModelClient abstract class"""

    def test_detect_refusal_positive(self):
        """Test refusal detection with clear refusal patterns"""

        class DummyClient(ModelClient):
            async def generate(self, prompt, **kwargs):
                return {}

            def is_available(self):
                return True

        client = DummyClient("test-model")

        # Test various refusal patterns
        test_cases = [
            ("I cannot help with that request.", True),
            ("I'm sorry, but I can't assist with that.", True),
            ("I must decline to answer this question.", True),
            ("This is against my ethical guidelines.", True),
            ("As an AI, I cannot provide that information.", True),
        ]

        for response, expected_refused in test_cases:
            refused, confidence = client.detect_refusal(response)
            assert refused == expected_refused, f"Failed for: {response}"
            assert confidence > 0.5, f"Low confidence for: {response}"

    def test_detect_refusal_negative(self):
        """Test refusal detection with compliant responses"""

        class DummyClient(ModelClient):
            async def generate(self, prompt, **kwargs):
                return {}

            def is_available(self):
                return True

        client = DummyClient("test-model")

        # Test non-refusal responses
        test_cases = [
            "Here's how you can solve this problem:",
            "The answer to your question is 42.",
            "Let me help you with that task.",
        ]

        for response in test_cases:
            refused, confidence = client.detect_refusal(response)
            assert refused == False, f"False positive for: {response}"


class TestGeminiClient:
    """Test GeminiClient"""

    @pytest.mark.skipif(
        True,  # Skip by default unless API key is configured
        reason="Requires GOOGLE_API_KEY environment variable"
    )
    def test_initialization(self):
        """Test Gemini client initialization"""
        client = GeminiClient(api_key="test-key", model="gemini-2.0-flash-exp")
        assert client.model_name == "gemini-2.0-flash-exp"
        assert client.api_key == "test-key"
        assert client.rpm_limit == 5

    def test_rate_limiting_logic(self):
        """Test rate limiting enforcement"""
        import time

        client = GeminiClient(api_key="test-key", model="gemini-2.0-flash-exp", rpm_limit=2)

        # Simulate rate limiting
        for i in range(2):
            client.request_times.append(time.time())

        # Should have 2 requests
        assert len(client.request_times) == 2

        # After cleanup, old requests should be removed
        client.request_times = [time.time() - 61]  # 61 seconds ago
        client._enforce_rate_limit()
        assert len(client.request_times) == 1  # Old one removed, new one added


class TestOllamaClient:
    """Test OllamaClient"""

    def test_initialization(self):
        """Test Ollama client initialization"""
        client = OllamaClient(model="llama3.1:8b")
        assert client.model_name == "llama3.1:8b"
        assert client.host == "http://localhost:11434"
        assert client.api_url == "http://localhost:11434/api/generate"

    def test_custom_host(self):
        """Test custom host configuration"""
        client = OllamaClient(model="mistral:7b", host="http://custom:8080")
        assert client.host == "http://custom:8080"
        assert client.api_url == "http://custom:8080/api/generate"

    @pytest.mark.asyncio
    async def test_generate_error_handling(self):
        """Test error handling in generate method"""
        client = OllamaClient(model="test-model")

        # This should return an error response, not raise an exception
        result = await client.generate("test prompt")

        assert "error" in result
        assert result["response"] == ""
        assert result["model"] == "test-model"


class TestHuggingFaceClient:
    """Test HuggingFaceClient"""

    def test_initialization(self):
        """Test HuggingFace client initialization"""
        client = HuggingFaceClient(token="test-token")
        assert client.token == "test-token"
        assert "mistralai/Mistral-7B-Instruct" in client.model_name
        assert client.monthly_limit == 1000

    def test_api_url_construction(self):
        """Test API URL is constructed correctly"""
        client = HuggingFaceClient(token="test-token", model="test/model")
        assert "test/model" in client.api_url
        assert client.api_url.startswith("https://api-inference.huggingface.co/")


class TestRetryLogic:
    """Test retry logic in base client"""

    @pytest.mark.asyncio
    async def test_retry_on_failure(self):
        """Test that retries happen on failure"""

        class FailingClient(ModelClient):
            def __init__(self):
                super().__init__("failing-model")
                self.attempt_count = 0

            async def generate(self, prompt, **kwargs):
                self.attempt_count += 1
                if self.attempt_count < 3:
                    # Fail first 2 attempts
                    return {"error": "Temporary failure"}
                else:
                    # Succeed on 3rd attempt
                    return {
                        "response": "Success",
                        "model": self.model_name,
                        "latency_ms": 100.0,
                        "tokens": 10,
                        "metadata": {},
                        "timestamp": "2024-01-01T00:00:00",
                        "error": None
                    }

            def is_available(self):
                return True

        client = FailingClient()
        result = await client.generate_with_retry("test", max_retries=3, backoff_factor=0.01)

        assert client.attempt_count == 3
        assert result["response"] == "Success"
        assert result["error"] is None

    @pytest.mark.asyncio
    async def test_retry_exhaustion(self):
        """Test behavior when all retries are exhausted"""

        class AlwaysFailingClient(ModelClient):
            async def generate(self, prompt, **kwargs):
                return {"error": "Permanent failure"}

            def is_available(self):
                return True

        client = AlwaysFailingClient("always-failing")
        result = await client.generate_with_retry("test", max_retries=2, backoff_factor=0.01)

        assert "error" in result
        assert "Failed after 2 attempts" in result["error"]


def test_prompt_library_loading():
    """Test that prompt library loads correctly"""
    from src.adversarial_prompts import PromptLibrary

    library = PromptLibrary()

    assert len(library) > 0
    assert len(library.get_categories()) > 0
    assert len(library.get_difficulties()) > 0
    assert len(library.get_tags()) > 0


def test_prompt_filtering():
    """Test prompt filtering functionality"""
    from src.adversarial_prompts import PromptLibrary

    library = PromptLibrary()

    # Filter by category
    jailbreak_prompts = library.get_by_category("roleplay")
    assert all(p.category == "roleplay" for p in jailbreak_prompts)

    # Filter by difficulty
    hard_prompts = library.get_by_difficulty("hard")
    assert all(p.difficulty == "hard" for p in hard_prompts)

    # Combined filter
    filtered = library.filter(
        categories=["roleplay"],
        difficulties=["medium", "hard"]
    )
    assert all(p.category == "roleplay" for p in filtered)
    assert all(p.difficulty in ["medium", "hard"] for p in filtered)


def test_evaluator_initialization():
    """Test Evaluator initialization"""
    from src.evaluator import Evaluator

    class DummyClient(ModelClient):
        async def generate(self, prompt, **kwargs):
            return {
                "response": "Test response",
                "model": "test-model",
                "latency_ms": 100.0,
                "tokens": 10,
                "metadata": {},
                "timestamp": "2024-01-01T00:00:00",
                "error": None
            }

        def is_available(self):
            return True

    clients = [DummyClient("model1"), DummyClient("model2")]
    evaluator = Evaluator(clients)

    assert len(evaluator.clients) == 2
    assert len(evaluator.results) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
