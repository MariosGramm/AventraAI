import logging

from ..config import get_rag_config 

logger = logging.getLogger(__name__)

class VectorRetriever:
    """Wraps the vector store with retrieval and stats operations."""

    def __init__(self, vector_store, embeddings):
        self.vector_store = vector_store
        self.embeddings = embeddings

    def get_retriever(self, k: int = None):
        config = get_rag_config()
        k = k or config.top_k
        return self.vector_store.as_retriever(search_kwargs={"k": k})

    def get_stats(self) -> dict:
        try:
            index = self.vector_store._index
            stats = index.describe_index_stats()
            return {
                "total_chunks": stats.total_vector_count,
                "namespaces": dict(stats.namespaces),
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"total_chunks": 0, "namespaces": {}}

    