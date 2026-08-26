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

COUNTRY_IATA_CODES = {
    "albania": "TIA", "argentina": "EZE", "australia": "SYD", "austria": "VIE",
    "belgium": "BRU", "brazil": "GIG", "canada": "YYZ", "chile": "SCL",
    "china": "PEK", "colombia": "BOG", "croatia": "ZAG", "czech republic": "PRG",
    "czechia": "PRG", "denmark": "CPH", "ecuador": "UIO", "egypt": "CAI",
    "england": "LON", "eritrea": "ASM", "finland": "HEL", "france": "PAR",
    "germany": "BER", "greece": "ATH", "hong kong": "HKG", "hungary": "BUD",
    "iceland": "KEF", "india": "DEL", "indonesia": "CGK", "ireland": "DUB",
    "israel": "TLV", "italy": "FCO", "japan": "TYO", "kenya": "NBO",
    "malaysia": "KUL", "mexico": "MEX", "morocco": "CMN", "netherlands": "AMS",
    "new zealand": "AKL", "nigeria": "LOS", "norway": "OSL", "peru": "LIM",
    "philippines": "MNL", "poland": "WAW", "portugal": "LIS", "romania": "OTP",
    "russia": "MOW", "saudi arabia": "RUH", "scotland": "EDI", "singapore": "SIN",
    "south africa": "JNB", "south korea": "ICN", "spain": "MAD", "sweden": "STO",
    "switzerland": "ZRH", "thailand": "BKK", "turkey": "IST", "uae": "DXB",
    "uk": "LON", "united kingdom": "LON", "united states": "JFK", "usa": "JFK",
    "vietnam": "SGN",
}


def resolve_city_iata(city: str | None) -> str | None:
    """Return the IATA code for a city or country (falls back to main airport)."""
    if not city:
        return None

    normalized_city = unicodedata.normalize("NFKD", city)
    normalized_city = "".join(char for char in normalized_city if not unicodedata.combining(char))
    normalized_city = re.sub(r"[^a-z0-9]+", " ", normalized_city.lower()).strip()
    return CITY_IATA_CODES.get(normalized_city) or COUNTRY_IATA_CODES.get(normalized_city)