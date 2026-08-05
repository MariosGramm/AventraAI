
import logging
from pathlib import Path

from backend.app.rag.config import get_config
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import MarkdownTextSplitter

logger = logging.getLogger(__name__)

class DocumentIngestor:
    """
    Loads a document, splits it into chunks, and stores them in the vector store.
    """

    def __init__(self, vector_store):
        self.vector_store = vector_store

    def ingest(self, file_path: str) -> int:
        """
        Full ingestion pipeline: Load → Split → Store.
        Returns the number of chunks added.
        """

        config = get_config()
        docs = self._load(file_path)

        if not docs:
            raise ValueError(f"No documents found in {file_path}")

        
        splitter = MarkdownTextSplitter(
            chunk_size = config.chunk_size,
            chunk_overlap = config.chunk_overlap
        )

        # Split the document into chunks
        chunks = splitter.split_documents(docs)

        filename = Path(file_path).name 
        for chunk in chunks:
            chunk.metadata["source"] = filename

        #Duplicate check: Filter out chunks that already exist in the vector store
        existing_chunks = self.vector_store._collection.get(
            where = {"source": filename}, limit = 1
        )

        if existing_chunks["ids"]:
            raise ValueError(f"Document **{filename}** already exists in the vector store.")

        # Store the chunks in the vector store
        self.vector_store.add_documents(chunks)
        logger.info(f"Added {len(chunks)} chunks from {filename} to the vector store.")

        return len(chunks)


    def _load(self, file_path: str) -> list:
        """
        Load a document from the given file path.
        Currently supports Markdown files.
        """
        return UnstructuredMarkdownLoader(file_path).load()


    