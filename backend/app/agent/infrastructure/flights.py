"""
agent/infrastructure/flights.py
---------------------------------
Provides flight price search using Tavily web search.
Used by the agent to find real-time flight prices and options.
"""

from langchain.tools import tool
import logging
from ..config import get_agent_config
from tavily import TavilyClient




logger = logging.getLogger(__name__)

class FlightsService:
    """
    Provides real-time flight price search using Tavily web search.
    Used by the Agent for travel planning.

    Search mode  → get_flights()      deterministic, called by agent pipeline
    Chat mode    → search_flight_prices_tool() ReAct tool, called by LLM
    """
    BASE_URL = "https://api.tavily.com"

    def __init__(self):
        config = get_agent_config()
        self.client = TavilyClient(api_key=config.tavily_api_key)

    def get_flights(self, origin: str, destination: str, date_from: str, date_to: str = None) -> str:
        """
        Search for real-time flight prices using Tavily web search.
        Used in Search mode (deterministic).

        Args:
            origin:      Origin city (e.g. 'Athens')
            destination: Destination city (e.g. 'Prague')
            date_from:   Departure date (e.g. '2026-09-15')
            date_to:     Return date (e.g. '2026-09-20')

        Returns:
            String with flight options, prices and airlines.
        """

        try:
            result = self.client.search(
                query=f"cheapest flights from {origin} to {destination} {date_from} return {date_to}",
                search_depth="basic",
                max_results=3
            )
            return str(result)
        except Exception as e:
            logger.error(f"Tavily flight search failed: {e}")
            return f"Could not retrieve flight prices from {origin} to {destination}."

# ── LangChain tool wrapper — used by Chat mode ReAct agent ──────────────────
@tool
def search_flight_prices_tool(
    origin: str,
    destination: str,
    date_from: str,
    date_to: str,
) -> str:
    """
    Search for real-time flight prices between two cities.
    Use this when the user asks about flights or provides an origin city.

    Args:
        origin:      Origin city (e.g. 'Athens', 'London')
        destination: Destination city (e.g. 'Prague', 'Tokyo')
        date_from:   Departure date (e.g. 'September 15 2026')
        date_to:     Return date (e.g. 'September 20 2026')

    Returns:
        String with flight options, prices and airlines.
    """
    return FlightsService().get_flights(origin, destination, date_from, date_to)