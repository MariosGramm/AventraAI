"""
rag/rag_pipeline.py — RAG Orchestrator
----------------------------------------
Wires together the ingestion and retrieval components of the RAG pipeline.
Provides a clean interface for the agent to retrieve relevant city guide chunks.

  ingestion  → load + split + store (used by run_indexer.py script)
  retrieval  → similarity search + stats + clear

LangSmith traces automatically when LANGCHAIN_TRACING_V2=true in .env.
"""

import logging

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from .config import get_config
from .ingestion.ingestor import DocumentIngestor
from .retrieval.retriever import VectorRetriever

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Top-level RAG orchestrator.

    Initialises shared infrastructure (embeddings, vector store) and
    delegates to DocumentIngestor for ingestion and VectorRetriever
    for similarity search. The generation layer is handled entirely
    by the agent (agent_pipeline.py) — this class is retrieval-only.
    """

    def __init__(self) -> None:
        """
        Initialise embeddings, ChromaDB vector store, ingestor, and retriever.
        All configuration is loaded from rag/config.py via get_config().
        """
        config = get_config()

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
        Perform a similarity search and return the most relevant chunks.

        Args:
            query: Natural language search query.
            k:     Number of chunks to return. Defaults to config.top_k if None.

        Returns:
            A list of LangChain Document objects ordered by relevance,
            each with page_content and metadata (city, section, source).
        """
        return self.retriever.as_retriever(k=k).invoke(query)

    def get_stats(self) -> dict:
        """
        Return statistics about the ChromaDB collection.

        Returns:
            A dict with keys: total_chunks (int), unique_sources (int),
            sources (list[str] sorted alphabetically).
        """
        return self.retriever.get_stats()

    def clear(self) -> None:
        """
        Delete all documents from the vector store and recreate an empty collection.
        Syncs the new vector store instance to all dependent components.
        """
        self.retriever.clear()
        new_vs                   = self.retriever.vectorstore
        self.vector_store        = new_vs
        self.ingestor.vector_store = new_vs