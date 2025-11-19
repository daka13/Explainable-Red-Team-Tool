"""
Explainable Red Team Tool - Streamlit Dashboard
Multi-model adversarial testing with interpretability layers
"""

import streamlit as st
import asyncio
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

# Import project modules
from src.api_clients import GeminiClient, OllamaClient, HuggingFaceClient
from src.adversarial_prompts import PromptLibrary
from src.evaluator import Evaluator
from src.visualizations import (
    plot_refusal_rates_by_model,
    plot_latency_by_model,
    plot_category_performance_heatmap,
    plot_difficulty_distribution,
    plot_success_rate_comparison,
    plot_model_vulnerability_radar,
    create_summary_metrics,
    plot_timeline
)
from src.interpretability import AttributionAnalyzer, EmbeddingAnalyzer

# Page config
st.set_page_config(
    page_title="Explainable Red Team Tool",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'evaluator' not in st.session_state:
        st.session_state.evaluator = None
    if 'results_df' not in st.session_state:
        st.session_state.results_df = None
    if 'prompt_library' not in st.session_state:
        st.session_state.prompt_library = None


def load_prompt_library():
    """Load the adversarial prompt library"""
    try:
        library = PromptLibrary()
        st.session_state.prompt_library = library
        return library
    except Exception as e:
        st.error(f"Failed to load prompt library: {e}")
        return None


def setup_clients(selected_models):
    """Setup model clients based on user selection"""
    clients = []

    # Google Gemini
    if "Gemini 2.0 Flash" in selected_models:
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            try:
                client = GeminiClient(api_key=api_key, model="gemini-2.0-flash-exp")
                if client.is_available():
                    clients.append(client)
                    st.sidebar.success("✓ Gemini 2.0 Flash connected")
                else:
                    st.sidebar.warning("⚠ Gemini 2.0 Flash unavailable")
            except Exception as e:
                st.sidebar.error(f"Gemini 2.0 Flash error: {e}")
        else:
            st.sidebar.error("❌ GOOGLE_API_KEY not set")

    if "Gemini 1.5 Pro" in selected_models:
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            try:
                client = GeminiClient(api_key=api_key, model="gemini-1.5-pro")
                if client.is_available():
                    clients.append(client)
                    st.sidebar.success("✓ Gemini 1.5 Pro connected")
                else:
                    st.sidebar.warning("⚠ Gemini 1.5 Pro unavailable")
            except Exception as e:
                st.sidebar.error(f"Gemini 1.5 Pro error: {e}")

    # Ollama models
    if "Llama 3.1 8B" in selected_models:
        try:
            client = OllamaClient(model="llama3.1:8b")
            if client.is_available():
                clients.append(client)
                st.sidebar.success("✓ Llama 3.1 8B connected")
            else:
                st.sidebar.warning("⚠ Llama 3.1 8B not available (install with: ollama pull llama3.1:8b)")
        except Exception as e:
            st.sidebar.error(f"Llama 3.1 8B error: {e}")

    if "Mistral 7B" in selected_models:
        try:
            client = OllamaClient(model="mistral:7b")
            if client.is_available():
                clients.append(client)
                st.sidebar.success("✓ Mistral 7B connected")
            else:
                st.sidebar.warning("⚠ Mistral 7B not available (install with: ollama pull mistral:7b)")
        except Exception as e:
            st.sidebar.error(f"Mistral 7B error: {e}")

    # HuggingFace
    if "HF Mistral-7B-Instruct" in selected_models:
        token = os.getenv("HUGGINGFACE_TOKEN")
        if token:
            try:
                client = HuggingFaceClient(token=token)
                if client.is_available():
                    clients.append(client)
                    st.sidebar.success("✓ HF Mistral-7B-Instruct connected")
                else:
                    st.sidebar.warning("⚠ HF Mistral-7B-Instruct unavailable")
            except Exception as e:
                st.sidebar.error(f"HF Mistral-7B-Instruct error: {e}")
        else:
            st.sidebar.error("❌ HUGGINGFACE_TOKEN not set")

    return clients


async def run_evaluation(clients, prompts, progress_bar, status_text):
    """Run the evaluation asynchronously"""
    evaluator = Evaluator(clients)

    status_text.text(f"Running {len(prompts)} prompts across {len(clients)} models...")

    results = await evaluator.evaluate_batch(
        prompts,
        show_progress=False
    )

    return evaluator


def main():
    """Main application"""
    initialize_session_state()

    # Header
    st.markdown('<div class="main-header">🎯 Explainable Red Team Tool</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Multi-Model Adversarial Testing with Interpretability</div>', unsafe_allow_html=True)

    # Sidebar - Configuration
    st.sidebar.title("⚙️ Configuration")

    # Model selection
    st.sidebar.subheader("Select Models")
    available_models = [
        "Gemini 2.0 Flash",
        "Gemini 1.5 Pro",
        "Llama 3.1 8B",
        "Mistral 7B",
        "HF Mistral-7B-Instruct"
    ]

    selected_models = st.sidebar.multiselect(
        "Choose models to test:",
        available_models,
        default=["Gemini 2.0 Flash"]
    )

    # Load prompt library
    if st.session_state.prompt_library is None:
        library = load_prompt_library()
    else:
        library = st.session_state.prompt_library

    if library is None:
        st.error("Failed to load prompt library. Please check the installation.")
        return

    # Prompt filtering
    st.sidebar.subheader("Filter Prompts")

    categories = st.sidebar.multiselect(
        "Categories:",
        library.get_categories(),
        default=library.get_categories()
    )

    difficulties = st.sidebar.multiselect(
        "Difficulty:",
        library.get_difficulties(),
        default=library.get_difficulties()
    )

    # Filter prompts
    filtered_prompts = library.filter(
        categories=categories if categories else None,
        difficulties=difficulties if difficulties else None
    )

    st.sidebar.info(f"📝 {len(filtered_prompts)} prompts selected")

    # Run evaluation button
    if st.sidebar.button("▶️ Run Evaluation", type="primary"):
        if not selected_models:
            st.sidebar.error("Please select at least one model")
        elif len(filtered_prompts) == 0:
            st.sidebar.error("No prompts match the selected filters")
        else:
            # Setup clients
            clients = setup_clients(selected_models)

            if not clients:
                st.error("No models are available. Please check your API keys and connections.")
            else:
                # Run evaluation
                progress_bar = st.progress(0)
                status_text = st.empty()

                try:
                    evaluator = asyncio.run(
                        run_evaluation(clients, filtered_prompts, progress_bar, status_text)
                    )

                    st.session_state.evaluator = evaluator
                    st.session_state.results_df = evaluator.get_results_dataframe()

                    progress_bar.progress(100)
                    status_text.text("✅ Evaluation complete!")

                    st.rerun()

                except Exception as e:
                    st.error(f"Evaluation failed: {e}")
                    import traceback
                    st.code(traceback.format_exc())

    # Export options
    if st.session_state.results_df is not None:
        st.sidebar.subheader("📤 Export Results")

        if st.sidebar.button("Export to CSV"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/results/results_{timestamp}.csv"
            Path("data/results").mkdir(parents=True, exist_ok=True)
            st.session_state.results_df.to_csv(filename, index=False)
            st.sidebar.success(f"Exported to {filename}")

    # Main content area
    if st.session_state.results_df is not None:
        df = st.session_state.results_df

        # Tabs for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview",
            "📈 Analysis",
            "🔍 Interpretability",
            "📋 Results Table",
            "ℹ️ About"
        ])

        with tab1:
            st.header("Overview")

            # Summary metrics
            metrics = create_summary_metrics(df)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Tests", metrics.get("total_tests", 0))
            with col2:
                st.metric("Overall Refusal Rate", f"{metrics.get('overall_refusal_rate', 0):.1%}")
            with col3:
                st.metric("Avg Latency", f"{metrics.get('avg_latency_ms', 0):.0f} ms")
            with col4:
                st.metric("Total Errors", metrics.get("total_errors", 0))

            # Key insights
            st.subheader("🔑 Key Insights")
            col1, col2 = st.columns(2)
            with col1:
                if metrics.get("most_vulnerable_model"):
                    st.info(f"**Most Vulnerable:** {metrics['most_vulnerable_model']}")
            with col2:
                if metrics.get("least_vulnerable_model"):
                    st.success(f"**Least Vulnerable:** {metrics['least_vulnerable_model']}")

            # Main charts
            col1, col2 = st.columns(2)

            with col1:
                st.plotly_chart(
                    plot_refusal_rates_by_model(df),
                    use_container_width=True
                )

            with col2:
                st.plotly_chart(
                    plot_latency_by_model(df),
                    use_container_width=True
                )

        with tab2:
            st.header("Detailed Analysis")

            # Heatmap
            st.plotly_chart(
                plot_category_performance_heatmap(df),
                use_container_width=True
            )

            col1, col2 = st.columns(2)

            with col1:
                st.plotly_chart(
                    plot_difficulty_distribution(df),
                    use_container_width=True
                )

            with col2:
                st.plotly_chart(
                    plot_success_rate_comparison(df),
                    use_container_width=True
                )

            # Vulnerability radar
            st.plotly_chart(
                plot_model_vulnerability_radar(df),
                use_container_width=True
            )

            # Timeline
            st.plotly_chart(
                plot_timeline(df),
                use_container_width=True
            )

        with tab3:
            st.header("Interpretability Analysis")

            st.info("🔬 This section provides insights into why models refuse or comply with prompts")

            # Attribution Analysis
            st.subheader("Token Attribution")

            prompt_ids = df["prompt_id"].unique()
            selected_prompt_id = st.selectbox("Select a prompt to analyze:", prompt_ids)

            if selected_prompt_id:
                prompt_data = df[df["prompt_id"] == selected_prompt_id].iloc[0]

                st.text_area("Prompt:", prompt_data["prompt_text"], height=100)

                try:
                    from src.interpretability import calculate_simple_attribution

                    # Show responses from different models
                    st.subheader("Model Responses")
                    prompt_results = df[df["prompt_id"] == selected_prompt_id]

                    for _, row in prompt_results.iterrows():
                        with st.expander(f"{row['model']} - {'✅ Refused' if row['refused'] else '❌ Complied'}"):
                            st.write(f"**Confidence:** {row['refusal_confidence']:.2f}")
                            st.write(f"**Latency:** {row['latency_ms']:.0f} ms")
                            st.write(f"**Response:**")
                            st.write(row['response'][:500] + "..." if len(row['response']) > 500 else row['response'])

                except Exception as e:
                    st.error(f"Attribution analysis error: {e}")

            # Embedding Analysis
            st.subheader("Embedding Space Analysis")

            if st.button("Generate Embedding Visualization"):
                try:
                    analyzer = EmbeddingAnalyzer()
                    df_with_embeddings = analyzer.analyze_results_dataframe(df, use_prompts=True)

                    st.plotly_chart(
                        analyzer.plot_embedding_space(
                            df_with_embeddings,
                            color_by="refused",
                            symbol_by="model"
                        ),
                        use_container_width=True
                    )

                    st.session_state.df_with_embeddings = df_with_embeddings

                except Exception as e:
                    st.error(f"Embedding analysis error: {e}")

        with tab4:
            st.header("Results Table")

            # Add filters
            col1, col2, col3 = st.columns(3)

            with col1:
                filter_model = st.multiselect(
                    "Filter by model:",
                    df["model"].unique(),
                    default=df["model"].unique()
                )

            with col2:
                filter_category = st.multiselect(
                    "Filter by category:",
                    df["prompt_category"].unique(),
                    default=df["prompt_category"].unique()
                )

            with col3:
                filter_refused = st.radio(
                    "Filter by refusal:",
                    ["All", "Refused", "Complied"]
                )

            # Apply filters
            filtered_df = df[df["model"].isin(filter_model) & df["prompt_category"].isin(filter_category)]

            if filter_refused == "Refused":
                filtered_df = filtered_df[filtered_df["refused"] == True]
            elif filter_refused == "Complied":
                filtered_df = filtered_df[filtered_df["refused"] == False]

            # Display table
            st.dataframe(
                filtered_df[[
                    "prompt_id", "model", "prompt_category", "prompt_difficulty",
                    "refused", "refusal_confidence", "latency_ms", "error"
                ]],
                use_container_width=True,
                height=400
            )

            st.caption(f"Showing {len(filtered_df)} of {len(df)} results")

        with tab5:
            st.header("About")

            st.markdown("""
            ## Explainable Red Team Tool

            This tool performs adversarial testing on multiple LLMs to evaluate their safety mechanisms
            and provide interpretability insights.

            ### Features:
            - **Multi-Model Testing**: Test prompts across Gemini, Ollama, and HuggingFace models
            - **Adversarial Prompt Library**: 25+ curated jailbreak and bias prompts
            - **Async Evaluation**: Concurrent testing for speed
            - **Interpretability**: SHAP attribution and embedding analysis
            - **Visualization**: Comprehensive charts and analysis

            ### Models Supported:
            - Google Gemini (2.0 Flash, 1.5 Pro)
            - Ollama (Llama 3.1, Mistral)
            - HuggingFace Inference API (Mistral-7B-Instruct)

            ### Tech Stack:
            - Python 3.10+
            - Streamlit
            - Plotly
            - SHAP & Transformers
            - Sentence Transformers & UMAP

            ### Setup:
            1. Install dependencies: `pip install -r requirements.txt`
            2. Copy `.env.example` to `.env` and add API keys
            3. For Ollama: `ollama pull llama3.1:8b && ollama pull mistral:7b`
            4. Run: `streamlit run app.py`

            ---
            Built for AI Safety Evaluation | [GitHub](https://github.com/yourusername/explainable-redteam)
            """)

    else:
        # Welcome screen
        st.info("👈 Configure your settings in the sidebar and click 'Run Evaluation' to get started!")

        st.markdown("""
        ### Quick Start:

        1. **Select Models**: Choose which LLMs to test (at least one)
        2. **Filter Prompts**: Select categories and difficulty levels
        3. **Run Evaluation**: Click the button to start testing
        4. **Analyze Results**: Explore the visualizations and insights

        ### Prerequisites:
        - Set up API keys in `.env` file
        - For Ollama models, ensure the Ollama server is running
        """)


if __name__ == "__main__":
    main()
