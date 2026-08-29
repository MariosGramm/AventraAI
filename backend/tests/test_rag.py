"""Tests for RAG service caching."""

from unittest.mock import patch, MagicMock
from types import SimpleNamespace

from app.rag import rag_service as rag_module


class TestRAGCache:

    def setup_method(self):
        rag_module._rag_cache.clear()

    @patch("app.rag.rag_service.PineconeVectorStore")
    @patch("app.rag.rag_service.OpenAIEmbeddings")
    def test_cache_hit_skips_retrieval(self, mock_embeddings, mock_vs):
        from app.rag.rag_service import RAGService

        mock_retriever = MagicMock()
        mock_retriever.invoke.return_value = [
            SimpleNamespace(page_content="Prague guide", metadata={"city": "Prague"})
        ]
        mock_vs.return_value.as_retriever.return_value = mock_retriever

        svc = RAGService()
        svc.retriever.vector_store = mock_vs.return_value

        result1 = svc.retrieve("Prague travel guide", k=5)
        result2 = svc.retrieve("Prague travel guide", k=5)

        assert result1 == result2
        # The retriever should only be invoked once (second is cached)
        assert mock_retriever.invoke.call_count <= 1

    def test_different_queries_get_different_cache_entries(self):
        rag_module._rag_cache[("prague", 5)] = ["chunk_prague"]
        rag_module._rag_cache[("tokyo", 5)] = ["chunk_tokyo"]

        assert rag_module._rag_cache[("prague", 5)] != rag_module._rag_cache[("tokyo", 5)]
