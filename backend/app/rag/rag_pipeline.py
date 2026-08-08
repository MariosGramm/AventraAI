"""
rag_pipeline.py — Orchestrator
-------------------------------
Wires together the three components:
  ingestion   → load + split + store
  retrieval   → search + stats + clear
  generation  → LCEL chain + streaming

LangSmith traces automatically when LANGCHAIN_TRACING_V2=true in .env.
"""

import logging

from app.rag.config import get_config
from app.rag.ingestion.ingestor import DocumentIngestor
from app.rag.retrieval.retriever import VectorRetriever
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings



logger = logging.getLogger(__name__)
    

class RAGPipeline:
    """
    Top-level orchestrator.
    Delegates every responsibility to a specialised component.
    """

    def __init__(self):
        config = get_config()

        self.embeddings = OpenAIEmbeddings(
            model=config.embedding_model
        )
        self.vector_store = Chroma(
            collection_name="documents",
            embedding_function=self.embeddings,
            persist_directory=str(config.chroma_db_path)
        )
        #TODO: Agent config for model, temperature, max_tokens
        # self.llm = ChatOpenAI(
        #     model=config.llm_model,
        #     temperature=config.temperature,
        #     max_tokens=config.max_tokens,
        #     streaming=True,
        # )
        self.ingestor    = DocumentIngestor(self.vector_store)
        self.retriever   = VectorRetriever(self.vector_store, self.embeddings)
        # self.chain_builder = ChainBuilder(self.llm, self.vector_store) TODO: Implement chain builder for generation component

    def retrieve(self, query: str, k: int = None) -> list:
        """Return relevant chunks for a query."""
        return self.retriever.as_retriever(k=k).invoke(query)

    def get_stats(self) -> dict:
        """Return ChromaDB stats."""
        return self.retriever.get_stats()

    def clear(self) -> None:
        """Clear the chain and rebuild it"""
        self.retriever.clear()
        # ── Sync the NEW vector_store to ALL components ────────────────
        new_vs = self.retriever.vector_store
        self.vector_store                = new_vs
        self.ingestor.vector_store       = new_vs   
        #self.chain_builder.vector_store  = new_vs  TODO: Implement chain builder for generation component
        #self.chain_builder.build() TODO: Implement chain builder for generation component


    def search(self, destination: str, dates: dict, budget: float = None) -> dict:
        """Full search flow: RAG + Weather + Places + LLM → 3 packages."""
        # TODO: implement in agent branch
        raise NotImplementedError

    def chat(self, message: str, history: list = None) -> str:
        """Chat flow: RAG + LLM → free text response."""
        # TODO: implement in agent branch
        raise NotImplementedError
        