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

from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings

from .config import get_rag_config
from .ingestion.ingestor import DocumentIngestor
from .retrieval.retriever import VectorRetriever

logger = logging.getLogger(__name__)


class RAGService:
    """Service facade for the Pinecone city guide knowledge base."""

    def __init__(self) -> None:
        config = get_rag_config()

        self.embeddings = OpenAIEmbeddings(model=config.embedding_model)
        self.vector_store = PineconeVectorStore(
            index_name=config.pinecone_index_name,
            embedding=self.embeddings,
        )
        self.ingestor  = DocumentIngestor(self.vector_store)
        self.retriever = VectorRetriever(self.vector_store, self.embeddings)

    def retrieve(self, query: str, k: int = None) -> list:
        return self.retriever.get_retriever(k=k).invoke(query)

    def get_stats(self) -> dict:
        return self.retriever.get_stats()

    def clear(self) -> None:
        self.vector_store.delete(delete_all=True)
        logger.info("Pinecone index cleared.")