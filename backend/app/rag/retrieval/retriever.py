import logging

from langchain_chroma import Chroma

from ..config import get_rag_config 

logger = logging.getLogger(__name__)

class VectorRetriever:
    """
    Wraps the ChromaDB vector store with retrieval, stats, and clear operations.
    Decoupled from the LLM — pure vector search layer.
    """
    def __init__(self, vector_store, embeddings):
        self.vector_store = vector_store
        self.embeddings = embeddings

    def get_retriever(self, k:int = None):
        """
        Returns a retriever object than can be used in LCEL chains.
        """
        config = get_rag_config()
        k = k or config.top_k
        return self.vector_store.as_retriever(search_kwargs={"k": k})

    def get_stats(self) -> dict:
        """
        Returns chunk count and unique document sources.
        """
        collection = self.vector_store._collection
        count = collection.count()
        sources = set()

        if count > 0:
            data = collection.get(include=["metadatas"])

            for metadata in (data["metadatas"] or []):  # Error avoidance: data["metadatas"] can be None
                if metadata and "source" in metadata:
                    sources.add(metadata["source"]) 

        return {
            "total_chunks": count,
            "unique_sources": len(sources),
            "sources": sorted(sources)
        }

    def clear(self):
        """
        Deletes all documents from the vector store and resets the collection.
        """

        config = get_rag_config()
        self.vector_store._collection.delete_collection()

        # Reinitialize the vector store after deletion
        self.vector_store = Chroma(
            collection_name = "city_guides",
            embedding_function = self.embeddings,
            persist_directory = str(config.chroma_db_path)
        )

        logger.info("Vector store cleared and reinitialized.")

    

    