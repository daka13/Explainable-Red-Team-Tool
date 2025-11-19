"""
Visualization utilities for displaying evaluation results.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Optional


def plot_refusal_rates_by_model(df: pd.DataFrame) -> go.Figure:
    """
    Create bar chart of refusal rates by model

    Args:
        df: Results DataFrame

    Returns:
        Plotly figure
    """
    if df.empty:
        return go.Figure()

    # Calculate refusal rates
    refusal_rates = df.groupby("model")["refused"].agg(["mean", "count"]).reset_index()
    refusal_rates.columns = ["Model", "Refusal Rate", "Total Tests"]
    refusal_rates["Refusal Rate"] = refusal_rates["Refusal Rate"] * 100

    # Create bar chart
    fig = px.bar(
        refusal_rates,
        x="Model",
        y="Refusal Rate",
        text="Refusal Rate",
        title="Refusal Rate by Model",
        labels={"Refusal Rate": "Refusal Rate (%)"},
        color="Refusal Rate",
        color_continuous_scale="RdYlGn"
    )

    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(showlegend=False, height=500)

    return fig


def plot_latency_by_model(df: pd.DataFrame) -> go.Figure:
    """
    Create box plot of response latency by model

    Args:
        df: Results DataFrame

    Returns:
        Plotly figure
    """
    if df.empty:
        return go.Figure()

    fig = px.box(
        df,
        x="model",
        y="latency_ms",
        title="Response Latency by Model",
        labels={"model": "Model", "latency_ms": "Latency (ms)"},
        color="model"
    )

    fig.update_layout(showlegend=False, height=500)

    return fig


def plot_category_performance_heatmap(df: pd.DataFrame) -> go.Figure:
    """
    Create heatmap of refusal rates by model and category

    Args:
        df: Results DataFrame

    Returns:
        Plotly figure
    """
    if df.empty:
        return go.Figure()

    # Calculate refusal rates by model and category
    pivot = df.pivot_table(
        values="refused",
        index="prompt_category",
        columns="model",
        aggfunc="mean"
    ) * 100

    fig = px.imshow(
        pivot,
        title="Refusal Rate Heatmap: Model vs Category",
        labels=dict(x="Model", y="Category", color="Refusal Rate (%)"),
        color_continuous_scale="RdYlGn",
        aspect="auto"
    )

    fig.update_layout(height=600)

    return fig


def plot_difficulty_distribution(df: pd.DataFrame) -> go.Figure:
    """
    Create stacked bar chart of refusal rates by difficulty

    Args:
        df: Results DataFrame

    Returns:
        Plotly figure
    """
    if df.empty:
        return go.Figure()

    # Group by difficulty and refusal status
    difficulty_refusal = df.groupby(["prompt_difficulty", "refused"]).size().reset_index(name="count")

    fig = px.bar(
        difficulty_refusal,
        x="prompt_difficulty",
        y="count",
        color="refused",
        title="Refusal Distribution by Difficulty",
        labels={"prompt_difficulty": "Difficulty", "count": "Number of Tests", "refused": "Refused"},
        barmode="stack",
        category_orders={"prompt_difficulty": ["easy", "medium", "hard"]}
    )

    fig.update_layout(height=500)

    return fig


def plot_success_rate_comparison(df: pd.DataFrame) -> go.Figure:
    """
    Create grouped bar chart comparing success rates across models

    Args:
        df: Results DataFrame

    Returns:
        Plotly figure
    """
    if df.empty:
        return go.Figure()

    # Calculate success rate (1 - refusal rate) by model and category
    success_rates = df.groupby(["model", "prompt_category"]).agg({
        "refused": lambda x: (1 - x.mean()) * 100
    }).reset_index()
    success_rates.columns = ["Model", "Category", "Success Rate"]

    fig = px.bar(
        success_rates,
        x="Category",
        y="Success Rate",
        color="Model",
        title="Jailbreak Success Rate by Category (Lower is Better)",
        labels={"Success Rate": "Success Rate (%)"},
        barmode="group"
    )

    fig.update_layout(height=500)

    return fig


def plot_response_time_vs_refusal(df: pd.DataFrame) -> go.Figure:
    """
    Create scatter plot of latency vs refusal confidence

    Args:
        df: Results DataFrame

    Returns:
        Plotly figure
    """
    if df.empty:
        return go.Figure()

    fig = px.scatter(
        df,
        x="latency_ms",
        y="refusal_confidence",
        color="model",
        size="tokens",
        hover_data=["prompt_category", "prompt_difficulty"],
        title="Response Latency vs Refusal Confidence",
        labels={
            "latency_ms": "Latency (ms)",
            "refusal_confidence": "Refusal Confidence",
            "model": "Model"
        }
    )

    fig.update_layout(height=600)

    return fig


def plot_model_vulnerability_radar(df: pd.DataFrame) -> go.Figure:
    """
    Create radar chart showing model vulnerability across categories

    Args:
        df: Results DataFrame

    Returns:
        Plotly figure
    """
    if df.empty:
        return go.Figure()

    # Calculate vulnerability (1 - refusal_rate) by model and category
    vulnerability = df.groupby(["model", "prompt_category"]).agg({
        "refused": lambda x: (1 - x.mean()) * 100
    }).reset_index()

    models = vulnerability["model"].unique()
    categories = vulnerability["prompt_category"].unique()

    fig = go.Figure()

    for model in models:
        model_data = vulnerability[vulnerability["model"] == model]

        # Ensure all categories are represented
        values = []
        for cat in categories:
            cat_data = model_data[model_data["prompt_category"] == cat]
            if len(cat_data) > 0:
                values.append(cat_data.iloc[0]["refused"])
            else:
                values.append(0)

        values.append(values[0])  # Close the radar chart

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=list(categories) + [categories[0]],
            fill='toself',
            name=model
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        title="Model Vulnerability Radar (Higher = More Vulnerable)",
        height=600
    )

    return fig


def create_summary_metrics(df: pd.DataFrame) -> Dict[str, any]:
    """
    Calculate summary metrics for display

    Args:
        df: Results DataFrame

    Returns:
        Dictionary of summary metrics
    """
    if df.empty:
        return {}

    metrics = {
        "total_tests": len(df),
        "total_prompts": df["prompt_id"].nunique(),
        "total_models": df["model"].nunique(),
        "overall_refusal_rate": df["refused"].mean(),
        "avg_latency_ms": df["latency_ms"].mean(),
        "total_errors": df["error"].notna().sum(),
        "most_vulnerable_model": None,
        "least_vulnerable_model": None
    }

    # Find most and least vulnerable models
    model_refusal_rates = df.groupby("model")["refused"].mean().sort_values()

    if len(model_refusal_rates) > 0:
        metrics["most_vulnerable_model"] = model_refusal_rates.index[0]
        metrics["least_vulnerable_model"] = model_refusal_rates.index[-1]

    return metrics


def plot_timeline(df: pd.DataFrame) -> go.Figure:
    """
    Create timeline of tests showing refusal patterns over time

    Args:
        df: Results DataFrame

    Returns:
        Plotly figure
    """
    if df.empty:
        return go.Figure()

    df_copy = df.copy()
    df_copy["timestamp"] = pd.to_datetime(df_copy["timestamp"])
    df_copy = df_copy.sort_values("timestamp")

    # Add sequence number
    df_copy["sequence"] = range(len(df_copy))

    fig = px.scatter(
        df_copy,
        x="sequence",
        y="model",
        color="refused",
        symbol="prompt_category",
        hover_data=["prompt_id", "latency_ms", "refusal_confidence"],
        title="Test Timeline: Refusal Patterns",
        labels={"sequence": "Test Sequence", "model": "Model", "refused": "Refused"}
    )

    fig.update_layout(height=500)

    return fig
