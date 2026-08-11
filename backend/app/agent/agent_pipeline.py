

from app.models import SearchSessionCreateDTO, User
from langchain_openai import ChatOpenAI

from .config import get_agent_config
from app.agent.infrastructure.hotels import HotelsService
from app.agent.infrastructure.places import PlacesService
from app.agent.infrastructure.weather import WeatherService
from app.rag.rag_pipeline import RAGPipeline


class TravelAgentPipeline:

    def __init__(self):
        self.rag_pipeline = RAGPipeline(self.get_llm_model)
        self.weather_service = WeatherService()
        self.places_service = PlacesService()
        self.hotels_service = HotelsService()
        self.config = get_agent_config()

    def get_llm_model(self, user: User, mode: str) -> ChatOpenAI:
        """
        Get the LLM model based on the user's subscription and the mode.
        """
        is_paid_subscription = user.subscription_type == "paid"

        if mode == "search":
            if is_paid_subscription:
                return ChatOpenAI(
                    model=self.config.search_llm_model_paid,
                    temperature=self.config.search_temperature_paid,
                    max_tokens=self.config.search_max_tokens_paid,
                    streaming=True,
                )
            else:
                return ChatOpenAI(
                    model=self.config.search_llm_model_free,
                    temperature=self.config.search_temperature_free,
                    max_tokens=self.config.search_max_tokens_free,
                    streaming=True,
                )
        else:  # mode == "chat"
            if is_paid_subscription:
                return ChatOpenAI(
                    model=self.config.chat_llm_model_paid,
                    temperature=self.config.chat_temperature_paid,
                    max_tokens=self.config.chat_max_tokens_paid,
                    streaming=True,
                )
            else:
                return ChatOpenAI(
                    model=self.config.chat_llm_model_free,
                    temperature=self.config.chat_temperature_free,
                    max_tokens=self.config.chat_max_tokens_free,
                    streaming=True,
                )

    def run_search(self, search_data: SearchSessionCreateDTO, user: User) -> dict:
        """
        Run the search pipeline.
        """

        # if user has given a budget to the agent, he will recieve one package
        # if user has not given a budget to the agent, he will recieve 3 packages for each budget tier (BUDGET, STANDARD, LUXURY)
        # k value is set accordingly to the number of packages the user will recieve. If user has given a budget, k=5, else k=10
        k = 5 if search_data.budget else 10

        # Fetch all data from rag and external APIs
        chunks = self.rag_pipeline.retrieve(
            query = f"travel guide attractions food accommodation budget tips {search_data.destination}",
            k = k
        )




