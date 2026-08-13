"""
View the first few chunks in the ChromaDB collection for city guides.

Usage (from backend/):
    uv run python scripts/view_chunks.py
"""

from pathlib import Path

import chromadb

SCRIPT_DIR  = Path(__file__).resolve().parent          # scripts/
BACKEND_DIR = SCRIPT_DIR.parent                         # backend/
CHROMA_PATH = BACKEND_DIR / "app" / "rag" / "chroma_db"

client = chromadb.PersistentClient(path='app/rag/chroma_db')
collection = client.get_collection('city_guides')

print('Total chunks:', collection.count())


results = collection.peek(15)  # Get the first 15 chunks
for i, (doc, meta) in enumerate(zip(results['documents'], results['metadatas'])):
    print(f'--- Chunk {i+1} ---')
    print(f'City:    {meta.get("city")}')
    print(f'Section: {meta.get("section")}')
    print(f'Source:  {meta.get("source")}')
    print(f'Content: {doc[:100]}')
    print()
