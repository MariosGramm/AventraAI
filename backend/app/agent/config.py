
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import os


@dataclass
class Config:
    """Configuration for the Agent."""

    #Search mode
    search_llm_model_free: str = "gpt-4o-mini"
    search_llm_model_paid: str = "gpt-4o"
    search_temperature: float = 0.2      
    search_max_tokens: int = 16000

    # Chat mode - Free tier
    chat_llm_model_free: str = "gpt-4o-mini"
    chat_llm_model_paid: str = "gpt-4o"
    chat_temperature:    float = 0.7       
    chat_max_tokens:     int   = 500 

    #Contextualization mode
    contextualize_model: str = "gpt-4o-mini"
    contextualize_temperature: float = 0.0
    contextualize_max_tokens: int = 100

    #API Keys
    google_maps_api_key: str = os.getenv("GOOGLE_MAPS_API_KEY")
    stayingapi_api_key: str = os.getenv("STAYINGAPI_API_KEY")


@lru_cache()
def get_agent_config() -> Config:
    """Get the configuration for the Agent - Singleton pattern."""
    return Config()
    

