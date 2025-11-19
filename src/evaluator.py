"""
Evaluation engine for running adversarial prompts against multiple models.
"""

import asyncio
import uuid
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
from pathlib import Path
from tqdm import tqdm

from .api_clients import ModelClient
from .adversarial_prompts import AdversarialPrompt


class EvaluationResult:
    """Represents a single evaluation result"""

    def __init__(
        self,
        test_id: str,
        prompt: AdversarialPrompt,
        model_name: str,
        response: str,
        latency_ms: float,
        tokens: Optional[int],
        refused: bool,
        refusal_confidence: float,
        timestamp: str,
        error: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        self.test_id = test_id
        self.prompt = prompt
        self.model_name = model_name
        self.response = response
        self.latency_ms = latency_ms
        self.tokens = tokens
        self.refused = refused
        self.refusal_confidence = refusal_confidence
        self.timestamp = timestamp
        self.error = error
        self.metadata = metadata or {}

    def to_dict(self) -> Dict:
        """Convert to dictionary for export"""
        return {
            "test_id": self.test_id,
            "timestamp": self.timestamp,
            "prompt_id": self.prompt.id,
            "prompt_category": self.prompt.category,
            "prompt_difficulty": self.prompt.difficulty,
            "prompt_text": self.prompt.prompt,
            "prompt_description": self.prompt.description,
            "expected_behavior": self.prompt.expected_behavior,
            "model": self.model_name,
            "response": self.response,
            "refused": self.refused,
            "refusal_confidence": self.refusal_confidence,
            "latency_ms": self.latency_ms,
            "tokens": self.tokens,
            "error": self.error,
            "tags": ",".join(self.prompt.tags)
        }


class Evaluator:
    """Runs adversarial prompts against multiple models"""

    def __init__(self, clients: List[ModelClient]):
        """
        Initialize evaluator

        Args:
            clients: List of model clients to test
        """
        self.clients = clients
        self.results: List[EvaluationResult] = []

    async def evaluate_single(
        self,
        client: ModelClient,
        prompt: AdversarialPrompt,
        **kwargs
    ) -> EvaluationResult:
        """
        Evaluate a single prompt on a single model

        Args:
            client: Model client to use
            prompt: Adversarial prompt to test
            **kwargs: Additional generation parameters

        Returns:
            EvaluationResult object
        """
        # Generate response
        response_data = await client.generate_with_retry(
            prompt.prompt,
            max_retries=3,
            **kwargs
        )

        # Detect refusal
        refused, confidence = client.detect_refusal(response_data["response"])

        # Create result
        result = EvaluationResult(
            test_id=str(uuid.uuid4()),
            prompt=prompt,
            model_name=client.model_name,
            response=response_data["response"],
            latency_ms=response_data["latency_ms"],
            tokens=response_data.get("tokens"),
            refused=refused,
            refusal_confidence=confidence,
            timestamp=response_data["timestamp"],
            error=response_data.get("error"),
            metadata=response_data.get("metadata", {})
        )

        return result

    async def evaluate_batch(
        self,
        prompts: List[AdversarialPrompt],
        show_progress: bool = True,
        **kwargs
    ) -> List[EvaluationResult]:
        """
        Evaluate a batch of prompts against all models

        Args:
            prompts: List of prompts to test
            show_progress: Whether to show progress bar
            **kwargs: Additional generation parameters

        Returns:
            List of evaluation results
        """
        tasks = []

        # Create all evaluation tasks
        for client in self.clients:
            for prompt in prompts:
                tasks.append(self.evaluate_single(client, prompt, **kwargs))

        # Run all tasks concurrently with progress tracking
        if show_progress:
            results = []
            with tqdm(total=len(tasks), desc="Evaluating") as pbar:
                for coro in asyncio.as_completed(tasks):
                    result = await coro
                    results.append(result)
                    pbar.update(1)
        else:
            results = await asyncio.gather(*tasks)

        # Store results
        self.results.extend(results)

        return results

    def get_results_dataframe(self) -> pd.DataFrame:
        """
        Convert results to pandas DataFrame

        Returns:
            DataFrame with all results
        """
        if not self.results:
            return pd.DataFrame()

        data = [r.to_dict() for r in self.results]
        return pd.DataFrame(data)

    def export_to_csv(self, filepath: str):
        """
        Export results to CSV file

        Args:
            filepath: Path to output CSV file
        """
        df = self.get_results_dataframe()
        df.to_csv(filepath, index=False)
        print(f"Results exported to: {filepath}")

    def export_to_json(self, filepath: str):
        """
        Export results to JSON file

        Args:
            filepath: Path to output JSON file
        """
        import json

        data = [r.to_dict() for r in self.results]

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Results exported to: {filepath}")

    def get_summary_stats(self) -> Dict:
        """
        Get summary statistics of evaluation results

        Returns:
            Dictionary with summary statistics
        """
        if not self.results:
            return {}

        df = self.get_results_dataframe()

        stats = {
            "total_tests": len(df),
            "total_errors": df["error"].notna().sum(),
            "by_model": {},
            "by_category": {},
            "by_difficulty": {}
        }

        # Stats by model
        for model in df["model"].unique():
            model_df = df[df["model"] == model]
            stats["by_model"][model] = {
                "total": len(model_df),
                "refused": model_df["refused"].sum(),
                "refusal_rate": model_df["refused"].mean(),
                "avg_latency_ms": model_df["latency_ms"].mean(),
                "errors": model_df["error"].notna().sum()
            }

        # Stats by category
        for category in df["prompt_category"].unique():
            cat_df = df[df["prompt_category"] == category]
            stats["by_category"][category] = {
                "total": len(cat_df),
                "refused": cat_df["refused"].sum(),
                "refusal_rate": cat_df["refused"].mean()
            }

        # Stats by difficulty
        for difficulty in df["prompt_difficulty"].unique():
            diff_df = df[df["prompt_difficulty"] == difficulty]
            stats["by_difficulty"][difficulty] = {
                "total": len(diff_df),
                "refused": diff_df["refused"].sum(),
                "refusal_rate": diff_df["refused"].mean()
            }

        return stats

    def clear_results(self):
        """Clear all stored results"""
        self.results = []

    def get_model_comparison(self) -> pd.DataFrame:
        """
        Get model-by-model comparison

        Returns:
            DataFrame comparing models
        """
        stats = self.get_summary_stats()

        if not stats or "by_model" not in stats:
            return pd.DataFrame()

        comparison_data = []
        for model, model_stats in stats["by_model"].items():
            comparison_data.append({
                "Model": model,
                "Total Tests": model_stats["total"],
                "Refused": model_stats["refused"],
                "Refusal Rate": f"{model_stats['refusal_rate']:.1%}",
                "Avg Latency (ms)": f"{model_stats['avg_latency_ms']:.0f}",
                "Errors": model_stats["errors"]
            })

        return pd.DataFrame(comparison_data)

    def get_vulnerability_ranking(self) -> List[tuple]:
        """
        Rank models by vulnerability (lower refusal rate = more vulnerable)

        Returns:
            List of (model_name, refusal_rate) tuples, sorted by vulnerability
        """
        stats = self.get_summary_stats()

        if not stats or "by_model" not in stats:
            return []

        rankings = [
            (model, model_stats["refusal_rate"])
            for model, model_stats in stats["by_model"].items()
        ]

        # Sort by refusal rate (ascending = more vulnerable)
        return sorted(rankings, key=lambda x: x[1])
