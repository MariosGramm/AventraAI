"""
IATA airport code resolver.
Uses OpenFlights airports.dat for ~5600 cities worldwide,
with manual overrides for major multi-airport cities.
"""

import csv
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

AIRPORTS_FILE = Path(__file__).parent / "airports.dat"

# Override for cities with multiple airports — prefer the main international one
MAJOR_CITY_OVERRIDES = {
    "paris": "CDG", "london": "LHR", "new york": "JFK", "new york city": "JFK",
    "tokyo": "NRT", "osaka": "KIX", "milan": "MXP", "rome": "FCO",
    "moscow": "SVO", "chicago": "ORD", "los angeles": "LAX",
    "san francisco": "SFO", "washington": "IAD", "washington dc": "IAD",
    "toronto": "YYZ", "montreal": "YUL", "buenos aires": "EZE",
    "rio de janeiro": "GIG", "sao paulo": "GRU", "istanbul": "IST",
    "seoul": "ICN", "beijing": "PEK", "shanghai": "PVG",
    "bangkok": "BKK", "singapore": "SIN", "sydney": "SYD",
    "melbourne": "MEL", "stockholm": "ARN", "copenhagen": "CPH",
    "berlin": "BER", "munich": "MUC", "amsterdam": "AMS",
    "dubai": "DXB", "hong kong": "HKG", "kuala lumpur": "KUL",
    "ho chi minh city": "SGN", "delhi": "DEL", "new delhi": "DEL",
    "mumbai": "BOM", "rio": "GIG", "kyoto": "KIX", "bali": "DPS",
    "corfu": "CFU", "rhodes": "RHO", "santorini": "JTR",
    "crete": "HER", "heraklion": "HER",
}

COUNTRY_OVERRIDES = {
    "albania": "TIA", "argentina": "EZE", "australia": "SYD", "austria": "VIE",
    "belgium": "BRU", "brazil": "GIG", "canada": "YYZ", "chile": "SCL",
    "china": "PEK", "colombia": "BOG", "croatia": "ZAG", "czech republic": "PRG",
    "czechia": "PRG", "denmark": "CPH", "ecuador": "UIO", "egypt": "CAI",
    "england": "LHR", "eritrea": "ASM", "finland": "HEL", "france": "CDG",
    "germany": "BER", "greece": "ATH", "hungary": "BUD",
    "iceland": "KEF", "india": "DEL", "indonesia": "CGK", "ireland": "DUB",
    "israel": "TLV", "italy": "FCO", "japan": "NRT", "kenya": "NBO",
    "malaysia": "KUL", "mexico": "MEX", "morocco": "CMN", "netherlands": "AMS",
    "new zealand": "AKL", "nigeria": "LOS", "norway": "OSL", "peru": "LIM",
    "philippines": "MNL", "poland": "WAW", "portugal": "LIS", "romania": "OTP",
    "russia": "SVO", "saudi arabia": "RUH", "scotland": "EDI", "singapore": "SIN",
    "south africa": "JNB", "south korea": "ICN", "spain": "MAD", "sweden": "ARN",
    "switzerland": "ZRH", "thailand": "BKK", "turkey": "IST", "uae": "DXB",
    "uk": "LHR", "united kingdom": "LHR", "united states": "JFK", "usa": "JFK",
    "vietnam": "SGN", "estonia": "TLL", "latvia": "RIX", "taiwan": "TPE",
    "cuba": "HAV", "tanzania": "DAR", "ghana": "ACC", "jordan": "AMM",
    "oman": "MCT",
}


@lru_cache(maxsize=1)
def _load_airports() -> dict[str, str]:
    """Load city→IATA mapping from airports.dat (cached singleton)."""
    mapping: dict[str, str] = {}
    if not AIRPORTS_FILE.exists():
        return mapping
    with open(AIRPORTS_FILE, encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row) < 6:
                continue
            city, iata = row[2].strip(), row[4].strip()
            if not iata or iata == "\\N" or len(iata) != 3 or not city:
                continue
            city_lower = city.lower()
            if city_lower not in mapping:
                mapping[city_lower] = iata
    return mapping


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    normalized = "".join(c for c in normalized if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", normalized.lower()).strip()


def resolve_city_iata(city: str | None) -> str | None:
    """Resolve a city or country name to its main IATA airport code."""
    if not city:
        return None

    key = _normalize(city)

    if key in MAJOR_CITY_OVERRIDES:
        return MAJOR_CITY_OVERRIDES[key]

    if key in COUNTRY_OVERRIDES:
        return COUNTRY_OVERRIDES[key]

    airports = _load_airports()
    return airports.get(key)
