

from backend.app.rag.config import get_config
from langchain_community.document_loaders import UnstructuredMarkdownLoader



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


        


def _load(self, file_path: str) -> list:
        """
        Load a document from the given file path.
        Currently supports Markdown files.
        """
        return UnstructuredMarkdownLoader(file_path).load()


    