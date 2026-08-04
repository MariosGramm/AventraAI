
from dataclasses import dataclass
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

    #Generation
    llm_model_free: str = "gpt-4o-mini"
    llm_model_paid: str = "gpt-4o"
    max_tokens: int = 4000
    temperature: float = 0.3

    


    
