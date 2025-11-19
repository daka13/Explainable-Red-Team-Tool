"""
Embedding analysis and visualization using UMAP.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
import plotly.express as px
import plotly.graph_objects as go

try:
    from sentence_transformers import SentenceTransformer
    from umap import UMAP
    from sklearn.cluster import KMeans
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False


class EmbeddingAnalyzer:
    """Analyzes and visualizes embeddings from prompts and responses"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding analyzer

        Args:
            model_name: SentenceTransformer model name
        """
        if not EMBEDDINGS_AVAILABLE:
            raise ImportError(
                "Required libraries not available. "
                "Install with: pip install sentence-transformers umap-learn scikit-learn"
            )

        self.model_name = model_name
        self.encoder = None
        self.umap_model = None

    def load_encoder(self):
        """Load the sentence encoder model"""
        try:
            self.encoder = SentenceTransformer(self.model_name)
        except Exception as e:
            raise RuntimeError(f"Failed to load encoder {self.model_name}: {e}")

    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """
        Encode texts into embeddings

        Args:
            texts: List of text strings

        Returns:
            Numpy array of embeddings [n_texts, embedding_dim]
        """
        if self.encoder is None:
            self.load_encoder()

        try:
            embeddings = self.encoder.encode(texts, show_progress_bar=True)
            return embeddings
        except Exception as e:
            print(f"Error encoding texts: {e}")
            return np.array([])

    def reduce_dimensions(
        self,
        embeddings: np.ndarray,
        n_components: int = 2,
        **kwargs
    ) -> np.ndarray:
        """
        Reduce embedding dimensions using UMAP

        Args:
            embeddings: High-dimensional embeddings
            n_components: Target dimensionality (2 or 3)
            **kwargs: Additional UMAP parameters

        Returns:
            Reduced embeddings
        """
        default_params = {
            "n_neighbors": 15,
            "min_dist": 0.1,
            "metric": "cosine",
            "random_state": 42
        }
        default_params.update(kwargs)

        self.umap_model = UMAP(n_components=n_components, **default_params)

        try:
            reduced = self.umap_model.fit_transform(embeddings)
            return reduced
        except Exception as e:
            print(f"Error in UMAP reduction: {e}")
            return np.array([])

    def cluster_embeddings(
        self,
        embeddings: np.ndarray,
        n_clusters: int = 5
    ) -> np.ndarray:
        """
        Cluster embeddings using K-means

        Args:
            embeddings: Embedding vectors
            n_clusters: Number of clusters

        Returns:
            Cluster labels
        """
        try:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            labels = kmeans.fit_predict(embeddings)
            return labels
        except Exception as e:
            print(f"Error in clustering: {e}")
            return np.array([])

    def analyze_results_dataframe(
        self,
        df: pd.DataFrame,
        use_prompts: bool = True,
        use_responses: bool = False
    ) -> pd.DataFrame:
        """
        Analyze results DataFrame and add embedding columns

        Args:
            df: Results DataFrame
            use_prompts: Include prompt embeddings
            use_responses: Include response embeddings

        Returns:
            DataFrame with embedding analysis
        """
        df_copy = df.copy()

        if use_prompts and "prompt_text" in df_copy.columns:
            print("Encoding prompts...")
            prompt_embeddings = self.encode_texts(df_copy["prompt_text"].tolist())

            if len(prompt_embeddings) > 0:
                # Reduce to 2D
                reduced_prompts = self.reduce_dimensions(prompt_embeddings, n_components=2)

                df_copy["prompt_embed_x"] = reduced_prompts[:, 0]
                df_copy["prompt_embed_y"] = reduced_prompts[:, 1]

                # Cluster
                clusters = self.cluster_embeddings(prompt_embeddings, n_clusters=5)
                df_copy["prompt_cluster"] = clusters

        if use_responses and "response" in df_copy.columns:
            print("Encoding responses...")
            # Filter out empty responses
            valid_responses = df_copy["response"].fillna("").astype(str)
            response_embeddings = self.encode_texts(valid_responses.tolist())

            if len(response_embeddings) > 0:
                # Reduce to 2D
                reduced_responses = self.reduce_dimensions(response_embeddings, n_components=2)

                df_copy["response_embed_x"] = reduced_responses[:, 0]
                df_copy["response_embed_y"] = reduced_responses[:, 1]

        return df_copy

    def plot_embedding_space(
        self,
        df: pd.DataFrame,
        color_by: str = "refused",
        symbol_by: str = "model",
        title: str = "Embedding Space Visualization"
    ) -> go.Figure:
        """
        Plot 2D embedding space

        Args:
            df: DataFrame with embedding columns
            color_by: Column to use for coloring
            symbol_by: Column to use for symbols
            title: Plot title

        Returns:
            Plotly figure
        """
        if "prompt_embed_x" not in df.columns:
            return go.Figure()

        fig = px.scatter(
            df,
            x="prompt_embed_x",
            y="prompt_embed_y",
            color=color_by,
            symbol=symbol_by,
            hover_data=["prompt_id", "model", "prompt_category", "refusal_confidence"],
            title=title,
            labels={
                "prompt_embed_x": "UMAP Dimension 1",
                "prompt_embed_y": "UMAP Dimension 2"
            }
        )

        fig.update_layout(height=600)
        fig.update_traces(marker=dict(size=8))

        return fig

    def plot_cluster_analysis(self, df: pd.DataFrame) -> go.Figure:
        """
        Plot cluster analysis with statistics

        Args:
            df: DataFrame with cluster columns

        Returns:
            Plotly figure
        """
        if "prompt_cluster" not in df.columns:
            return go.Figure()

        # Calculate cluster statistics
        cluster_stats = df.groupby("prompt_cluster").agg({
            "refused": "mean",
            "prompt_embed_x": "count"
        }).reset_index()
        cluster_stats.columns = ["Cluster", "Refusal Rate", "Count"]

        fig = px.scatter(
            df,
            x="prompt_embed_x",
            y="prompt_embed_y",
            color="prompt_cluster",
            size="refusal_confidence",
            hover_data=["prompt_id", "model", "refused"],
            title="Prompt Clustering in Embedding Space",
            labels={
                "prompt_embed_x": "UMAP Dimension 1",
                "prompt_embed_y": "UMAP Dimension 2",
                "prompt_cluster": "Cluster"
            }
        )

        fig.update_layout(height=600)

        return fig

    def plot_model_comparison_embeddings(self, df: pd.DataFrame) -> go.Figure:
        """
        Compare how different models cluster in embedding space

        Args:
            df: DataFrame with embeddings

        Returns:
            Plotly figure
        """
        if "prompt_embed_x" not in df.columns:
            return go.Figure()

        fig = px.scatter(
            df,
            x="prompt_embed_x",
            y="prompt_embed_y",
            color="model",
            symbol="refused",
            facet_col="model",
            facet_col_wrap=2,
            hover_data=["prompt_category", "refusal_confidence"],
            title="Model-wise Embedding Space Comparison",
            labels={
                "prompt_embed_x": "UMAP 1",
                "prompt_embed_y": "UMAP 2"
            }
        )

        fig.update_layout(height=800)

        return fig

    def find_similar_prompts(
        self,
        df: pd.DataFrame,
        prompt_id: str,
        n_similar: int = 5
    ) -> pd.DataFrame:
        """
        Find prompts similar to a given prompt based on embeddings

        Args:
            df: DataFrame with embeddings
            prompt_id: ID of reference prompt
            n_similar: Number of similar prompts to return

        Returns:
            DataFrame with similar prompts
        """
        if "prompt_embed_x" not in df.columns:
            return pd.DataFrame()

        # Get reference embedding
        ref_row = df[df["prompt_id"] == prompt_id]
        if len(ref_row) == 0:
            return pd.DataFrame()

        ref_embed = np.array([
            ref_row.iloc[0]["prompt_embed_x"],
            ref_row.iloc[0]["prompt_embed_y"]
        ])

        # Calculate distances
        embeddings = df[["prompt_embed_x", "prompt_embed_y"]].values
        distances = np.linalg.norm(embeddings - ref_embed, axis=1)

        # Get indices of most similar (excluding self)
        similar_indices = np.argsort(distances)[1:n_similar+1]

        return df.iloc[similar_indices][["prompt_id", "prompt_text", "model", "refused"]]


def visualize_embedding_distribution(embeddings: np.ndarray, labels: List[str]) -> go.Figure:
    """
    Visualize distribution of embeddings

    Args:
        embeddings: 2D embeddings
        labels: Labels for each embedding

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    for label in set(labels):
        mask = np.array(labels) == label
        subset = embeddings[mask]

        fig.add_trace(go.Scatter(
            x=subset[:, 0],
            y=subset[:, 1],
            mode='markers',
            name=label,
            marker=dict(size=8)
        ))

    fig.update_layout(
        title="Embedding Distribution",
        xaxis_title="Dimension 1",
        yaxis_title="Dimension 2",
        height=600
    )

    return fig
