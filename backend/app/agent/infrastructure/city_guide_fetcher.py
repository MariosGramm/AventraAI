"""
On-demand city guide fetcher.
Fetches a city guide from Wikivoyage and indexes it into ChromaDB
when a user searches for a city not yet in the knowledge base.
"""

import re
import logging
import requests
from pathlib import Path

from app.rag.rag_service import RAGService

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "rag" / "data"

WIKIVOYAGE_API = "https://en.wikivoyage.org/w/api.php"
HEADERS = {"User-Agent": "AventraAI/1.0 (travel guide fetcher) python-requests/2.x"}

RELEVANT_SECTIONS = [
    "understand", "history", "climate", "weather", "see", "do", "eat", "drink",
    "sleep", "buy", "shopping", "get in", "stay safe", "highlights", "overview",
    "budget", "neighbourhoods", "neighborhoods", "districts", "festivals",
    "culture", "nightlife", "food", "accommodation", "attractions", "activities",
]


def city_file_exists(city: str) -> bool:
    return (DATA_DIR / _city_to_filename(city)).exists()


def fetch_and_index_city(city: str) -> bool:
    """Fetch city guide from Wikivoyage and index it. Returns True on success."""
    if city_file_exists(city):
        return True

    logger.info("Fetching city guide for: %s", city)

    raw_text = _fetch_from_wikivoyage(city)
    if not raw_text:
        return False

    content = _parse_and_filter(city, raw_text)
    if len(content) < 200:
        logger.warning("Content too short for %s, skipping", city)
        return False

    if len(content) > 20000:
        content = content[:20000]

    filepath = DATA_DIR / _city_to_filename(city)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding="utf-8")

    try:
        rag = RAGService()
        rag.ingestor.ingest(str(filepath))
        logger.info("Successfully indexed city guide for: %s", city)
        _notify_new_city(city)
    except Exception as e:
        logger.error("Failed to index %s: %s", city, e)

    return True


def _fetch_from_wikivoyage(city: str) -> str | None:
    try:
        response = requests.get(
            WIKIVOYAGE_API,
            params={
                "action": "query", "titles": city, "prop": "extracts",
                "explaintext": True, "exsectionformat": "wiki",
                "format": "json", "redirects": True,
            },
            headers=HEADERS,
            timeout=15,
        )
        response.raise_for_status()
        pages = response.json().get("query", {}).get("pages", {})
        for page_id, page in pages.items():
            if page_id == "-1":
                return None
            return page.get("extract", "") or None
    except requests.RequestException as e:
        logger.error("Wikivoyage fetch error for %s: %s", city, e)
    return None


def _parse_and_filter(city: str, raw_text: str) -> str:
    lines = raw_text.split('\n')
    md = [f"# {city} — Travel Guide", "", "> Source: Wikivoyage", ""]

    intro_lines = []
    in_intro = True
    current_section = None
    current_content = []
    include_current = False

    def flush():
        if current_section and include_current:
            content = _clean(('\n'.join(current_content)).strip())
            if len(content) >= 30:
                md.append(f"## {current_section}")
                md.append("")
                md.append(content)
                md.append("")

    for line in lines:
        stripped = line.strip()
        header_match = re.match(r'^(==+)\s*(.+?)\s*\1$', stripped)
        if header_match:
            in_intro = False
            flush()
            current_section = header_match.group(2).strip()
            current_content = []
            include_current = any(
                current_section.lower().startswith(k) for k in RELEVANT_SECTIONS
            )
        elif in_intro:
            if stripped:
                intro_lines.append(stripped)
        else:
            current_content.append(stripped)

    flush()

    if intro_lines:
        intro = _clean('\n'.join(intro_lines))[:800]
        md.insert(4, intro)
        md.insert(5, "")

    return '\n'.join(md)


def _clean(text: str) -> str:
    text = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', text)
    text = re.sub(r'\{\{[^}]*\}\}', '', text)
    text = re.sub(r'\[https?://\S+\s+([^\]]+)\]', r'\1', text)
    text = re.sub(r'\[https?://\S+\]', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r"'{2,3}", '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def _city_to_filename(city: str) -> str:
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


def _notify_new_city(city: str) -> None:
    try:
        from app.utils import send_email
        send_email(
            email_to="mariosgramm21@gmail.com",
            subject=f"AventraAI — New city indexed: {city}",
            html_content=f"<p>A new city guide was auto-fetched and indexed: <strong>{city}</strong></p>",
        )
    except Exception as e:
        logger.warning("Failed to send new city notification: %s", e)
