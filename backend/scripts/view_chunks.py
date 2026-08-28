"""
View stats and sample chunks from the Pinecone index.

Usage (from backend/):
    uv run python scripts/view_chunks.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from app.rag.rag_service import RAGService

rag = RAGService()

stats = rag.get_stats()
print(f"Total vectors: {stats.get('total_chunks', 0)}")
print(f"Namespaces: {stats.get('namespaces', {})}")

print("\n🔍 Sample query: 'best things to see and do'")
results = rag.retrieve("best things to see and do", k=5)
for i, r in enumerate(results, 1):
    print(f"\n--- Chunk {i} ---")
    print(f"City:    {r.metadata.get('city', 'Unknown')}")
    print(f"Section: {r.metadata.get('section', 'Unknown')}")
    print(f"Source:  {r.metadata.get('source', 'Unknown')}")
    print(f"Content: {r.page_content[:100]}")
