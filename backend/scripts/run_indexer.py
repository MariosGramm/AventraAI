"""
run_indexer.py
--------------
One-time script to index all city guides into ChromaDB.
Run this whenever you add or update city guide files.

Usage (from backend/):
    uv run python scripts/run_indexer.py
"""

import os
import sys
from pathlib import Path

# Add backend/ to path so app imports work
sys.path.append(str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

import chromadb
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from app.rag.config import get_config
from app.rag.ingestion.ingestor import DocumentIngestor


def main():
    print("=" * 60)
    print("AventraAI — RAG Indexer")
    print("=" * 60)

    # Check OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set in .env")
        sys.exit(1)

    config = get_config()

    # Check data directory
    if not config.data_path.exists():
        print(f"❌ Data directory not found: {config.data_path}")
        sys.exit(1)

    md_files = list(config.data_path.glob("*.md"))
    if not md_files:
        print(f"❌ No markdown files found in: {config.data_path}")
        sys.exit(1)

    print(f"\n📁 Data directory:  {config.data_path}")
    print(f"💾 ChromaDB path:   {config.chroma_db_path}")
    print(f"🧠 Embedding model: {config.embedding_model}")
    print(f"🌍 City guides:     {len(md_files)}\n")

    # Step 1: Clear existing collection
    print("🗑️  Clearing existing collection...")
    try:
        client = chromadb.PersistentClient(path=str(config.chroma_db_path))
        client.delete_collection("city_guides")
        print("✅ Existing collection deleted\n")
    except Exception:
        print("ℹ️  No existing collection found — starting fresh\n")

    # Step 2: Create fresh vectorstore
    embeddings = OpenAIEmbeddings(model=config.embedding_model)
    vectorstore = Chroma(
        collection_name="city_guides",
        embedding_function=embeddings,
        persist_directory=str(config.chroma_db_path),
    )

    # Step 3: Index all city guides
    ingestor = DocumentIngestor(vectorstore)

    success_count = 0
    skipped_count = 0
    failed_count  = 0

    for i, md_file in enumerate(sorted(md_files), 1):
        print(f"[{i}/{len(md_files)}] Indexing: {md_file.name}...")
        try:
            chunks = ingestor.ingest(str(md_file))
            print(f"  ✅ {chunks} chunks indexed")
            success_count += 1
        except ValueError as e:
            print(f"  ⚠️  Skipped: {e}")
            skipped_count += 1
        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed_count += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"✅ Success:  {success_count} cities")
    print(f"⏭️  Skipped:  {skipped_count} cities")
    print(f"❌ Failed:   {failed_count} cities")
    print(f"💾 ChromaDB: {config.chroma_db_path}")
    print("=" * 60)

    # Step 4: Verification
    if success_count > 0:
        print("\n🔍 Verification — test query:")
        results = vectorstore.similarity_search(
            query="best things to see and do",
            k=3
        )
        for r in results:
            city    = r.metadata.get("city", "Unknown")
            section = r.metadata.get("section", "Unknown")
            preview = r.page_content[:80].replace("\n", " ")
            print(f"  [{city} — {section}] {preview}...")


if __name__ == "__main__":
    main()
