"""
Wikivoyage City Guide Fetcher
------------------------------
Automatically downloads city guides from the Wikivoyage API
and saves them as markdown files for the RAG pipeline.

Usage (from backend/scripts/):
    uv run python fetch_city_guides.py

Output:
    backend/app/rag/data/<city_name>.md
"""

import re
import time
import requests
from pathlib import Path

# ===========================================================================
# Configuration
# ===========================================================================

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
OUTPUT_DIR  = BACKEND_DIR / "app" / "rag" / "data"

CITIES = [
    # Europe
    "Paris", "London", "Rome", "Barcelona", "Amsterdam",
    "Venice", "Berlin", "Athens", "Prague", "Lisbon", "Vienna", 
    "Budapest", "Dublin", "Stockholm", "Copenhagen", "Warsaw", "Moscow",
    "Edinburgh", "Florence", "Brussels", "Oslo", "Helsinki", "Reykjavik",
    "Madrid", "Seville", "Valencia", "Porto", "Marseille", "Nice", "Tirana",
    # Asia
    "Tokyo", "Kyoto", "Seoul", "Bangkok", "Singapore",
    "Dubai", "Beijing", "Hong Kong", "Istanbul", "New Delhi",
    # North America
    "New York City", "Los Angeles", "San Francisco", "Las Vegas",
    "Toronto", "Vancouver", "Montreal", "Miami", "Washington, D.C.", "Mexico City",
    # South America
    "Rio de Janeiro", "Buenos Aires", "Lima", "Santiago",
    "Medellín", "Cusco", "Bogotá",
    # Africa
    "Cairo", "Cape Town", "Nairobi", "Marrakesh",
    "Abuja", "Lagos", "Asmara",
    # Oceania
    "Sydney", "Melbourne", "Auckland", "Wellington", "Brisbane",
]

WIKIVOYAGE_API = "https://en.wikivoyage.org/w/api.php"

HEADERS = {
    "User-Agent": "AventraAI/1.0 (travel guide fetcher; educational project) python-requests/2.x"
}

REQUEST_DELAY = 3.0
RETRY_DELAY   = 30.0
MAX_RETRIES   = 3
MAX_CHARS     = 20000

# Whitelist — ONLY these sections are kept, everything else is excluded.
# Matching is done by checking if the section title STARTS WITH any of these keywords.
RELEVANT_SECTIONS = [
    "understand",
    "history",
    "climate",
    "weather",
    "see",
    "do",
    "eat",
    "drink",
    "sleep",
    "buy",
    "shopping",
    "get in",
    "stay safe",
    "highlights",
    "overview",
    "budget",
    "neighbourhoods",
    "neighborhoods",
    "districts",
    "festivals",
    "culture",
    "nightlife",
    "food",
    "accommodation",
    "attractions",
    "activities",
    "people",
    "geography",
]


# ===========================================================================
# Wikivoyage API
# ===========================================================================

def fetch_plain_text(city: str) -> str | None:
    """
    Fetch plain text content for a city from the Wikivoyage API.
    Returns the full text or None on failure.
    """
    params = {
        "action": "query",
        "titles": city,
        "prop": "extracts",
        "explaintext": True,
        "exsectionformat": "wiki",
        "format": "json",
        "redirects": True,
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                WIKIVOYAGE_API,
                params=params,
                headers=HEADERS,
                timeout=15
            )

            if response.status_code == 429:
                wait = RETRY_DELAY * attempt
                print(f"  ⏳ Rate limited (attempt {attempt}/{MAX_RETRIES}). Waiting {wait:.0f}s...")
                time.sleep(wait)
                continue

            response.raise_for_status()
            data = response.json()

            pages = data.get("query", {}).get("pages", {})
            for page_id, page in pages.items():
                if page_id == "-1":
                    print(f"  ⚠️  Not found: {city}")
                    return None
                extract = page.get("extract", "")
                if not extract:
                    print(f"  ⚠️  Empty content: {city}")
                    return None
                return extract

        except requests.RequestException as e:
            print(f"  ❌ Request error (attempt {attempt}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)

    print(f"  ❌ Failed after {MAX_RETRIES} attempts: {city}")
    return None


# ===========================================================================
# Content processing
# ===========================================================================

def is_relevant_section(title: str) -> bool:
    """
    Whitelist-only check.
    Returns True only if the section title starts with a keyword
    from RELEVANT_SECTIONS. Everything else is excluded.
    """
    title_lower = title.lower().strip()
    for keyword in RELEVANT_SECTIONS:
        if title_lower == keyword or title_lower.startswith(keyword):
            return True
    return False


def clean_wikitext(text: str) -> str:
    """Remove wikitext markup and return clean plain text."""
    # [[links|display text]] → display text
    text = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', text)
    # {{templates}} → remove
    text = re.sub(r'\{\{[^}]*\}\}', '', text)
    # [url text] → text
    text = re.sub(r'\[https?://\S+\s+([^\]]+)\]', r'\1', text)
    # bare [url] → remove
    text = re.sub(r'\[https?://\S+\]', '', text)
    # HTML tags → remove
    text = re.sub(r'<[^>]+>', '', text)
    # bold/italic → remove markers
    text = re.sub(r"'{2,3}", '', text)
    # collapse multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def parse_and_filter(city: str, raw_text: str) -> str:
    """
    Parse plain text into structured markdown.
    Keeps only sections that pass the whitelist check.
    """
    lines = raw_text.split('\n')

    markdown_lines = [
        f"# {city} — Travel Guide",
        "",
        f"> Source: Wikivoyage (Creative Commons Attribution-ShareAlike 3.0)",
        "",
    ]

    intro_lines          = []
    in_intro             = True
    current_section      = None
    current_content      = []
    include_current      = False

    def flush_section():
        """Append current section to output if it passed the whitelist."""
        if current_section is None or not include_current:
            return
        content = clean_wikitext('\n'.join(current_content)).strip()
        if len(content) < 30:
            return
        markdown_lines.append(f"## {current_section}")
        markdown_lines.append("")
        markdown_lines.append(content)
        markdown_lines.append("")

    for line in lines:
        stripped = line.strip()

        # Detect == Section == or === Sub-section === headers
        header_match = re.match(r'^(==+)\s*(.+?)\s*\1$', stripped)

        if header_match:
            in_intro = False
            flush_section()
            current_section = header_match.group(2).strip()
            current_content = []
            include_current = is_relevant_section(current_section)
        elif in_intro:
            if stripped:
                intro_lines.append(stripped)
        else:
            current_content.append(stripped)

    flush_section()

    # Insert intro (max ~800 chars, cut at sentence boundary)
    if intro_lines:
        intro_text = clean_wikitext('\n'.join(intro_lines))
        if len(intro_text) > 800:
            intro_text = intro_text[:800]
            last_period = intro_text.rfind('.')
            if last_period > 400:
                intro_text = intro_text[:last_period + 1]
        if intro_text:
            markdown_lines.insert(4, "")
            markdown_lines.insert(4, intro_text)

    return '\n'.join(markdown_lines)


def truncate_content(content: str, max_chars: int) -> str:
    """Truncate to max_chars, always cutting at a complete section boundary."""
    if len(content) <= max_chars:
        return content

    truncated    = content[:max_chars]
    last_section = truncated.rfind('\n## ')

    if last_section > max_chars // 2:
        return content[:last_section].strip()

    return truncated.strip()


def city_to_filename(city: str) -> str:
    """Convert a city name to a safe lowercase filename."""
    return (
        city.lower()
        .replace(" ", "_")
        .replace(",", "")
        .replace(".", "")
        .replace("é", "e")
        .replace("á", "a")
        .replace("ó", "o")
        + ".md"
    )


def save_markdown(city: str, content: str) -> Path:
    """Write markdown content to file and return its path."""
    filepath = OUTPUT_DIR / city_to_filename(city)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath


# ===========================================================================
# Main
# ===========================================================================

def main():
    print("=" * 60)
    print("Wikivoyage City Guide Fetcher")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    print(f"🌍 Cities to fetch:  {len(CITIES)}")
    print(f"📏 Max chars/file:   {MAX_CHARS:,}\n")

    success_count = 0
    skip_count    = 0
    fail_count    = 0

    for i, city in enumerate(CITIES, 1):

        # Skip cities that already have a file
        if (OUTPUT_DIR / city_to_filename(city)).exists():
            print(f"[{i}/{len(CITIES)}] Skipping (already exists): {city}")
            skip_count += 1
            continue

        print(f"[{i}/{len(CITIES)}] Fetching: {city}...")

        raw_text = fetch_plain_text(city)
        if not raw_text:
            fail_count += 1
            continue

        markdown = parse_and_filter(city, raw_text)
        markdown = truncate_content(markdown, MAX_CHARS)

        if len(markdown) < 200:
            print(f"  ⚠️  Content too short after filtering: {city}")
            fail_count += 1
            continue

        filepath = save_markdown(city, markdown)
        print(f"  ✅ Saved: {filepath.name} ({len(markdown):,} chars)")
        success_count += 1

        if i < len(CITIES):
            time.sleep(REQUEST_DELAY)

    print("\n" + "=" * 60)
    print(f"✅ Success:  {success_count} cities")
    print(f"⏭️  Skipped:  {skip_count} cities (already exist)")
    print(f"❌ Failed:   {fail_count} cities")
    print(f"📁 Files:    {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()