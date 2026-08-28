"""
run_indexer.py
--------------
One-time script to index all city guides into Pinecone.

Usage (from backend/):
    uv run python scripts/run_indexer.py
"""

import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from app.rag.config import get_rag_config
from app.rag.rag_service import RAGService


def main():
    print("=" * 60)
    print("AventraAI — RAG Indexer (Pinecone)")
    print("=" * 60)

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set in .env")
        sys.exit(1)

    if not os.getenv("PINECONE_API_KEY"):
        print("❌ PINECONE_API_KEY not set in .env")
        sys.exit(1)

    config = get_rag_config()

    if not config.data_path.exists():
        print(f"❌ Data directory not found: {config.data_path}")
        sys.exit(1)

    md_files = list(config.data_path.glob("*.md"))
    if not md_files:
        print(f"❌ No markdown files found in: {config.data_path}")
        sys.exit(1)

    print(f"\n📁 Data directory:  {config.data_path}")
    print(f"🧠 Embedding model: {config.embedding_model}")
    print(f"🌲 Pinecone index:  {config.pinecone_index_name}")
    print(f"🌍 City guides:     {len(md_files)}\n")

    rag = RAGService()

    # Check current state
    stats = rag.get_stats()
    print(f"📊 Current vectors: {stats.get('total_chunks', 0)}\n")

    # Index all city guides
    success_count = 0
    skipped_count = 0
    failed_count  = 0

    for i, md_file in enumerate(sorted(md_files), 1):
        print(f"[{i}/{len(md_files)}] Indexing: {md_file.name}...")
        try:
            chunks = rag.ingestor.ingest(str(md_file))
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

    final_stats = rag.get_stats()
    print(f"📊 Total vectors: {final_stats.get('total_chunks', 0)}")
    print("=" * 60)

    # Verification
    if success_count > 0:
        print("\n🔍 Verification — test query:")
        results = rag.retrieve("best things to see and do", k=3)
        for r in results:
            city    = r.metadata.get("city", "Unknown")
            section = r.metadata.get("section", "Unknown")
            preview = r.page_content[:80].replace("\n", " ")
            print(f"  [{city} — {section}] {preview}...")


if __name__ == "__main__":
    main()
