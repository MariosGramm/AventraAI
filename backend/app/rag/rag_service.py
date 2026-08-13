"""
rag/rag_service.py — RAG Service
----------------------------------
Provides a clean, unified interface for interacting with the ChromaDB
vector store and the city guide knowledge base.

This is NOT an orchestration layer — it is a service facade that
initialises shared infrastructure (embeddings, vector store) and
exposes three simple operations:

  retrieve() → similarity search over indexed city guide chunks
  get_stats() → collection statistics for debugging and monitoring
  clear()     → wipe and recreate the vector store collection

All orchestration (LLM calls, tool invocation, context building) is
handled exclusively by the agent layer (agent/agent_pipeline.py),
which consumes this service as a dependency.

LangSmith traces automatically when LANGCHAIN_TRACING_V2=true in .env.
"""

import logging

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from .config import get_rag_config
from .ingestion.ingestor import DocumentIngestor
from .retrieval.retriever import VectorRetriever

logger = logging.getLogger(__name__)


class RAGService:
    """
    Service facade for the ChromaDB city guide knowledge base.

    Initialises shared infrastructure (embeddings, vector store) once
    and exposes a minimal public interface for the agent to consume.
    Ingestion and retrieval responsibilities are delegated to
    DocumentIngestor and VectorRetriever respectively.

    This class does not perform any LLM calls or chain building —
    those concerns belong entirely to agent/agent_pipeline.py.
    """

    def __init__(self) -> None:
        """
        Initialise OpenAI embeddings, ChromaDB vector store, ingestor,
        and retriever. All configuration values are loaded from
        rag/config.py via get_rag_config().
        """
        config = get_rag_config()

        self.embeddings = OpenAIEmbeddings(model=config.embedding_model)
        self.vector_store = Chroma(
            collection_name="city_guides",
            embedding_function=self.embeddings,
            persist_directory=str(config.chroma_db_path),
        )
        self.ingestor  = DocumentIngestor(self.vector_store)
        self.retriever = VectorRetriever(self.vector_store, self.embeddings)

    def retrieve(self, query: str, k: int = None) -> list:
        """
        Perform a similarity search over the city guide chunks and return
        the most relevant results.

        Args:
            query: Natural language search query (e.g. "attractions and food in Prague").
            k:     Number of chunks to return. Falls back to config.top_k when None.

        Returns:
            A list of LangChain Document objects ordered by relevance score,
            each containing page_content (str) and metadata with keys:
            city (str), section (str), source (str).
        """
        return self.retriever.as_retriever(k=k).invoke(query)

    def get_stats(self) -> dict:
        """
        Return diagnostic statistics about the ChromaDB collection.

        Useful for verifying that indexing completed successfully and for
        monitoring the knowledge base in production.

        Returns:
            A dict with the following keys:
              total_chunks (int)       — total number of indexed chunks.
              unique_sources (int)     — number of distinct city guide files.
              sources (list[str])      — sorted list of indexed filenames.
        """
        return self.retriever.get_stats()

    def clear(self) -> None:
        """
        Delete all documents from the vector store, recreate an empty collection,
        and sync the new vector store instance to all dependent components.

        Use this before re-running the indexer to ensure a clean slate.
        """
        self.retriever.clear()
        new_vs                     = self.retriever.vectorstore
        self.vector_store          = new_vs
        self.ingestor.vector_store = new_vs