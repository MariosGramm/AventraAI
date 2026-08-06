"""
Remove the "Source" line from all city guide markdown files in the data directory.
This is a one-time cleanup script to ensure that the "Source" line is not included in the indexed chunks.

Usage (from backend/):
    uv run python scripts/clean_city_guides.py
"""

from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "app" / "rag" / "data"

md_files = list(DATA_DIR.glob("*.md"))
print(f"Found {len(md_files)} files\n")

for md_file in md_files:
    content = md_file.read_text(encoding="utf-8")
    
    # Αφαίρεσε τη γραμμή με το Source
    lines = content.split("\n")
    cleaned = [
        line for line in lines
        if not line.strip().startswith("> Source:")
    ]
    
    cleaned_content = "\n".join(cleaned)
    md_file.write_text(cleaned_content, encoding="utf-8")
    print(f"✅ Cleaned: {md_file.name}")

print("\nDone!")