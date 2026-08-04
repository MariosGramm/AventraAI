
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Configuration for the RAG system."""

    # Paths
    base_path: Path = Path(__file__).parent
    chroma_db_path: Path = None

    # Chunking
    #TODO: Add chunking parameters here
    
