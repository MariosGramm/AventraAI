"""IATA codes for the cities supported by the travel guides."""

import re
import unicodedata


CITY_IATA_CODES = {
    "abuja": "ABV", "amsterdam": "AMS", "asmara": "ASM", "athens": "ATH",
    "auckland": "AKL", "bangkok": "BKK", "barcelona": "BCN", "beijing": "PEK",
    "berlin": "BER", "bogota": "BOG", "brisbane": "BNE", "brussels": "BRU",
    "budapest": "BUD", "buenos aires": "EZE", "cairo": "CAI", "cape town": "CPT",
    "copenhagen": "CPH", "cusco": "CUZ", "dubai": "DXB", "dublin": "DUB",
    "edinburgh": "EDI", "florence": "FLR", "helsinki": "HEL", "hong kong": "HKG",
    "istanbul": "IST", "kyoto": "KIX", "lagos": "LOS", "las vegas": "LAS",
    "lima": "LIM", "lisbon": "LIS", "london": "LON", "los angeles": "LAX",
    "madrid": "MAD", "marrakesh": "RAK", "marseille": "MRS", "medellin": "MDE",
    "melbourne": "MEL", "mexico city": "MEX", "miami": "MIA", "montreal": "YUL",
    "moscow": "MOW", "nairobi": "NBO", "new delhi": "DEL", "new york city": "NYC",
    "nice": "NCE", "oslo": "OSL", "paris": "PAR", "porto": "OPO", "prague": "PRG",
    "reykjavik": "REK", "rio de janeiro": "RIO", "rome": "ROM", "santiago": "SCL",
    "san francisco": "SFO", "seoul": "SEL", "seville": "SVQ", "singapore": "SIN",
    "stockholm": "STO", "sydney": "SYD", "tirana": "TIA", "tokyo": "TYO",
    "toronto": "YTO", "valencia": "VLC", "vancouver": "YVR", "venice": "VCE",
    "vienna": "VIE", "warsaw": "WAW", "washington dc": "WAS", "wellington": "WLG",
}

CITY_IATA_CODES.update({
    "delhi": "DEL",
    "new york": "NYC",
    "rio": "RIO",
    "washington": "WAS",
})


def resolve_city_iata(city: str | None) -> str | None:
    """Return the metropolitan IATA code for a supported city name."""
    if not city:
        return None

    normalized_city = unicodedata.normalize("NFKD", city)
    normalized_city = "".join(char for char in normalized_city if not unicodedata.combining(char))
    normalized_city = re.sub(r"[^a-z0-9]+", " ", normalized_city.lower()).strip()
    return CITY_IATA_CODES.get(normalized_city)