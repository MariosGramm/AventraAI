
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass
class Config:
    """Configuration for the RAG system."""

    # Paths
    base_path: Path = Path(__file__).parent
    chroma_db_path: Path = None

    # Chunking
    chunk_size: int = 1000
    chunk_overlap: int = 100

    # Retrieval
    top_k: int = 5
    min_relevance_score: float = 0.15

    # Embedding
    embedding_model: str = "text-embedding-3-small"

    def __post_init__(self):
        if self.chroma_db_path is None:
            self.chroma_db_path = self.base_path / "chroma_db"

    # Create directory if it doesn't exist
        self.chroma_db_path.mkdir(exist_ok=True)

@lru_cache()
def get_config() -> Config:
    """Get the configuration for the RAG system - Singleton pattern."""
    return Config()
    

#TODO : Implement sample docs path and sample docs for testing purposes if needed.
