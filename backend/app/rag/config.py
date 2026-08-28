
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass
class Config:
    """Configuration for the RAG system."""

    # Paths
    base_path: Path = Path(__file__).parent
    data_path: Path = base_path / "data"

    # Chunking
    chunk_size: int = 1000
    chunk_overlap: int = 100

    # Retrieval
    top_k: int = 5
    min_relevance_score: float = 0.15

    # Embedding
    embedding_model: str = "text-embedding-3-small"

    # Pinecone
    pinecone_index_name: str = "city-guides"


@lru_cache()
def get_rag_config() -> Config:
    """Get the configuration for the RAG system - Singleton pattern."""
    return Config()
