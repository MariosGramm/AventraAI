import logging
from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class DocumentIngestor:
    """
    Loads a markdown document, splits it into chunks by headers,
    and stores them in the vector store.
    """

    def __init__(self, vector_store):
        self.vector_store = vector_store

    def ingest(self, file_path: str) -> int:
        """
        Full ingestion pipeline: Load → Split → Store.
        Returns the number of chunks added.
        """
        filename  = Path(file_path).name
        city_name = filename.replace(".md", "").replace("_", " ").title()

        # Load
        docs = self._load(file_path)
        if not docs:
            raise ValueError(f"No content extracted from {file_path}")

        # Split by markdown headers
        splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#",  "city"),
                ("##", "section"),
            ],
            strip_headers=True
        )
        chunks = splitter.split_text(docs[0].page_content)

        # Add metadata to each chunk
        for chunk in chunks:
            chunk.metadata["source"] = filename
            chunk.metadata["city"]   = city_name

        if not chunks:
            raise ValueError(f"No chunks created from {filename}")

        # Store
        self.vector_store.add_documents(chunks)
        logger.info(f"Added {len(chunks)} chunks from {filename}")

        return len(chunks)

    def _load(self, file_path: str) -> list:
        """Load markdown file as plain text."""
        return TextLoader(file_path, encoding="utf-8").load()