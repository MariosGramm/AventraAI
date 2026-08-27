"""
agent/agent_pipeline.py — Travel Agent Orchestrator
-----------------------------------------------------
Top-level orchestrator for the AventraAI travel agent.
Coordinates all components to produce travel packages (Search mode)
and conversational travel advice (Chat mode).

Search mode (deterministic):
    RAG retrieval → Weather → Hotels → Places → LLM → 3 JSON packages (or 1 if budget given)

Chat mode (ReAct):
    Contextualize → RAG retrieval → ReAct agent with tools → free text response

LangSmith traces automatically when LANGCHAIN_TRACING_V2=true in .env.
"""

import json
import logging
import re

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..models import ChatMessage, ChatRole, SubscriptionTier, User
from ..models import SearchSessionCreateDTO
from .config import get_agent_config
from .infrastructure.airport_codes import resolve_city_iata
from .infrastructure.places import PlacesService, get_place_details_tool, get_places_tool
from .infrastructure.weather import WeatherService, get_weather_tool
from .prompts import (
    CONTEXTUALIZE_PROMPT,
    HARMFUL_CONTENT_REFUSAL_MESSAGE,
    TOPIC_GUARD_PROMPT,
    TRAVEL_CHAT_SYSTEM_PROMPT,
    TRAVEL_SEARCH_SYSTEM_PROMPT,
    wrap_untrusted,
)
from ..rag.rag_service import RAGService

logger = logging.getLogger(__name__)


class TravelAgentPipeline:
    """
    Top-level orchestrator for the AventraAI travel agent.

    Supports two modes of operation:
        - Search mode: deterministic pipeline that calls RAG, Weather, Hotels,
          and Places APIs sequentially, then invokes an LLM to produce structured
          JSON travel packages.
        - Chat mode: ReAct agent that uses LangChain tools to answer travel
          questions in a conversational manner, with optional history-aware
          query reformulation.

    The LLM model (free vs paid tier) is resolved dynamically per request
    based on the authenticated user's subscription tier.
    """

    def __init__(self) -> None:
        """
        Initialise all infrastructure components and load agent configuration.
        No LLM instances are created at init time — they are resolved per request
        via _get_llm() based on the user's subscription tier.
        """
        self.config          = get_agent_config()
        self.weather_service = WeatherService()
        self.places_service  = PlacesService()
        self.rag_pipeline    = RAGService()

        self._chat_tools = [
            get_weather_tool,
            get_places_tool,
            get_place_details_tool,
        ]

    def run_search(
        self,
        search_data: SearchSessionCreateDTO,
        user: User,
    ) -> dict:
        """
        Execute the deterministic search pipeline and return structured travel packages.

        Fetches context from RAG, Weather API, Hotels API, and Places API,
        then invokes the LLM with the aggregated context to produce either
        one package (if budget is specified) or three packages (budget/mid/luxury).

        Args:
            search_data: DTO containing destination, dates, budget, adults,
                         children, currency, and trip_type.
            user:        The authenticated user — used to resolve the LLM model
                         based on subscription tier.

        Returns:
            A dict matching the travel package JSON schema, e.g.:
            {"packages": [{"tier": "budget", "itinerary": [...], ...}, ...]}
            Returns an empty dict if the LLM response cannot be parsed.
        """

        destination = self._translate_destination(search_data.destination)

        from .infrastructure.city_guide_fetcher import city_file_exists, fetch_and_index_city
        if not city_file_exists(destination):
            fetch_and_index_city(destination)

        rag_chunks = self.rag_pipeline.retrieve(
            query=f"travel guide attractions food tips {destination}",
            k=5,
        )

        check_in  = search_data.date_from.strftime("%Y-%m-%d")
        check_out = search_data.date_to.strftime("%Y-%m-%d")

        weather     = self.weather_service.get_weather(destination, check_in, check_out)

        flight_info = None
        origin = self._translate_destination(search_data.origin) if search_data.origin else None
        origin_iata = search_data.origin_iata or resolve_city_iata(origin)
        destination_iata = search_data.destination_iata or resolve_city_iata(destination)

        # Construct the Skyscanner URL
        if origin_iata and destination_iata:
            origin_iata = origin_iata.lower()
            destination_iata = destination_iata.lower()
            flight_info = (
                f"You can check available flights here: "
                f"https://www.skyscanner.net/transport/flights/"
                f"{origin_iata}/{destination_iata}/"
                f"{search_data.date_from.strftime('%y%m%d')}/"
                f"{search_data.date_to.strftime('%y%m%d')}/"
                f"?adultsv2={search_data.adults}&currency={search_data.currency.value}"
            )

        # Construct Booking.com URL
        booking_info = (
            f"You can browse available hotels here: "
            f"https://www.booking.com/searchresults.html"
            f"?ss={destination.replace(' ', '+')}"
            f"&checkin={check_in}&checkout={check_out}"
            f"&group_adults={search_data.adults}"
            f"&group_children={search_data.children}"
        )

        attractions = self.places_service.get_places(destination, "attractions")
        restaurants = self.places_service.get_places(destination, "restaurants")

        context = self._build_search_context(
            destination=destination,
            rag_chunks=rag_chunks,
            weather=weather,
            attractions=attractions,
            restaurants=restaurants,
        )

        # Seperate instruction regarding the budget.
        # If a budget is specified , return one package that fits the budget.
        # If no budget is specified , return one standard package budget package.
        budget_instruction = (
            f"The user has a budget of {search_data.budget} {search_data.currency.value}. "
            f"Create ONE package that fits this budget. "
            f"Use these tier guidelines:\n"
            f"- budget tier: total trip cost under 500 {search_data.currency.value}\n"
            f"- mid tier: total trip cost between 500 and 2000 {search_data.currency.value}\n"
            f"- luxury tier: total trip cost above 2000 {search_data.currency.value}\n"
            f"Label the package with the appropriate tier."
            if search_data.budget
            else
            "The user has no specific budget. Create ONE mid-range package (tier: mid)."
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", TRAVEL_SEARCH_SYSTEM_PROMPT),
            ("human", "{input}"),
        ])

        llm   = self._get_llm(user, mode="search")
        chain = prompt | llm | StrOutputParser()

        user_request = (
            f"Destination: {destination}\n"
            f"Dates: {check_in} to {check_out}\n"
            f"Adults: {search_data.adults}\n"
            f"Children: {search_data.children}\n"
            f"Budget: {search_data.budget or 'Not specified'} {search_data.currency.value}\n"
            f"Trip type: {search_data.trip_type.value if search_data.trip_type else 'Not specified'}\n"
            f"{budget_instruction}"
        )

        response = chain.invoke({
            "input": (
                f"{wrap_untrusted('user_request', user_request)}\n\n"
                f"{wrap_untrusted('retrieved_context', context)}"
            )
        })

        result = self._parse_search_response(response)

        destination_photos = [a.get("photo_url") for a in attractions if a.get("photo_url")][:1]

        for package in result.get("packages", []):
            package["flight_info"] = flight_info
            package["booking_info"] = booking_info
            package["destination_photos"] = destination_photos

        return result

    def run_chat(
        self,
        message: str,
        history: list[ChatMessage],
        user: User,
    ) -> str:
        """
        Execute the ReAct chat pipeline and return a free-text travel response.

        If chat history is provided, the message is first reformulated into a
        standalone question via the contextualize LLM. The reformulated (or
        original) query is then used for RAG retrieval. A ReAct agent with
        access to weather, places, and hotel tools produces the final response.

        Args:
            message: The latest user message.
            history: List of previous ChatMessage objects for this session.
            user:    The authenticated user — used to resolve the LLM model
                     based on subscription tier.

        Returns:
            A plain-text string containing the agent's travel advice response.
        """
        off_topic_reply = self._check_off_topic(message, history, user)
        if off_topic_reply:
            return off_topic_reply

        standalone_query = (
            self._contextualize(message, history) if history else message
        )

        rag_chunks = self.rag_pipeline.retrieve(query=standalone_query, k=5)

        rag_context = "\n\n".join([
            f"[{chunk.metadata.get('section', 'General')}]\n{chunk.page_content}"
            for chunk in rag_chunks
        ]) if rag_chunks else "No city guide data available."

        llm = self._get_llm(user, mode="chat")

        agent = create_agent(llm, self._chat_tools, system_prompt=TRAVEL_CHAT_SYSTEM_PROMPT)

        formatted_history = self._format_history_as_messages(history)

        result = agent.invoke({
            "messages": [
                *formatted_history,
                HumanMessage(
                    content=(
                        f"{wrap_untrusted('user_message', standalone_query)}\n\n"
                        f"{wrap_untrusted('city_guide_context', rag_context)}"
                    )
                ),
            ]
        })

        messages = result.get("messages", [])
        return messages[-1].content if messages else ""

    def _get_llm(self, user: User, mode: str) -> ChatOpenAI:
        """
        Resolve and return the appropriate ChatOpenAI instance based on
        the user's subscription tier and the current execution mode.

        Args:
            user: The authenticated user whose subscription_tier determines
                  whether the free or paid LLM model is used.
            mode: Execution mode — one of "search", "chat", or "contextualize".

        Returns:
            A configured ChatOpenAI instance ready for invocation.
        """
        is_paid = user.subscription_tier == SubscriptionTier.PAID

        if mode == "search":
            model  = self.config.search_llm_model_paid if is_paid else self.config.search_llm_model_free
            temp   = self.config.search_temperature
            tokens = self.config.search_max_tokens
        else:   #chat
            model  = self.config.chat_llm_model_paid if is_paid else self.config.chat_llm_model_free
            temp   = self.config.chat_temperature
            tokens = self.config.chat_max_tokens

        return ChatOpenAI(model=model, temperature=temp, max_tokens=tokens)

    def _check_off_topic(self, message: str, history: list[ChatMessage], user: User) -> str | None:
        """
        Cheap gatekeeper that filters out non-travel messages before the
        (more expensive) RAG retrieval + ReAct tool-calling agent runs.

        Uses the same small, cheap model as the contextualizer with a low
        token cap, so off-topic messages cost only this single short call
        instead of a full agent loop with tool calls on a bigger model.

        Args:
            message: The latest user message.
            history: List of previous ChatMessage objects for this session.
            user:    The authenticated user — used only for logging when a
                     harmful request is blocked.

        Returns:
            None if the message is travel-related (caller should proceed
            with the normal chat pipeline). Otherwise, a ready-to-send
            string to return to the user as-is (a friendly redirect for
            off-topic messages, or a fixed refusal for harmful ones).
        """
        llm = ChatOpenAI(
            model=self.config.contextualize_model,
            temperature=0,
            max_tokens=80,
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", TOPIC_GUARD_PROMPT),
            ("human", "{input}"),
        ])

        chain = prompt | llm | StrOutputParser()

        verdict = chain.invoke({
            "input": (
                f"{wrap_untrusted('conversation_history', self._format_history_as_text(history[-4:]))}\n\n"
                f"{wrap_untrusted('user_message', message)}"
            )
        }).strip()

        if verdict == "TRAVEL_OK":
            return None
        if verdict == "HARMFUL":
            logger.warning("Blocked harmful chat message from user %s", user.id)
            return HARMFUL_CONTENT_REFUSAL_MESSAGE
        return verdict

    def _contextualize(self, message: str, history: list[ChatMessage]) -> str:
        """
        Reformulate a follow-up user message into a standalone question
        using the chat history as context.

        Uses a cheap, fast LLM (gpt-4o-mini, temperature=0) to rewrite
        ambiguous follow-up questions so they can be understood without
        the conversation history — improving RAG retrieval quality.

        Args:
            message: The latest user message, potentially a follow-up.
            history: List of previous ChatMessage objects in this session.

        Returns:
            A standalone question string. If no reformulation is needed,
            the original message is returned as-is.
        """
        llm = ChatOpenAI(
            model=self.config.contextualize_model,
            temperature=self.config.contextualize_temperature,
            max_tokens=self.config.contextualize_max_tokens,
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", CONTEXTUALIZE_PROMPT),
            ("human", "{input}"),
        ])

        chain = prompt | llm | StrOutputParser()

        return chain.invoke({
            "input": (
                f"{wrap_untrusted('conversation_history', self._format_history_as_text(history))}\n\n"
                f"{wrap_untrusted('user_message', message)}"
            )
        })

    def _build_search_context(
        self,
        destination: str,
        rag_chunks:  list,
        weather:     dict | None,
        attractions: list,
        restaurants: list,
    ) -> str:
        """
        Aggregate data from all sources into a single formatted string
        that will be injected into the LLM prompt as context.
        """
        parts = []

        if rag_chunks:
            rag_text = "\n\n".join([
                f"[{chunk.metadata.get('section', 'General')}]\n{chunk.page_content}"
                for chunk in rag_chunks
            ])
            parts.append(f"=== CITY GUIDE ===\n{rag_text}")
        else:
            logger.warning(f"No context received from RAG for {destination}")

        if weather:
            parts.append(
                f"=== WEATHER ===\n"
                f"Temperature: {weather.get('avg_temp_min')}C - {weather.get('avg_temp_max')}C\n"
                f"Conditions: {weather.get('description')}\n"
                f"Precipitation: {weather.get('total_precip_mm')}mm\n"
                f"Data type: {'Forecast' if weather.get('is_forecast') else 'Historical average'}"
            )
        else:
            logger.warning(f"No context received from Weather API for {destination}")

        if attractions:
            attr_lines = [
                f"- {a.get('name')}: rating={a.get('rating')}, address={a.get('address')}"
                for a in attractions[:5]
            ]
            parts.append(f"=== ATTRACTIONS ===\n" + "\n".join(attr_lines))
        else:
            logger.warning(f"No context received from Places API (attractions) for {destination}")

        if restaurants:
            rest_lines = [
                f"- {r.get('name')}: "
                f"rating={r.get('rating')}, "
                f"price_level={r.get('price_level')}, "
                f"address={r.get('address')}"
                for r in restaurants[:5]
            ]
            parts.append(f"=== RESTAURANTS ===\n" + "\n".join(rest_lines))
        else:
            logger.warning(f"No context received from Places API (restaurants) for {destination}")

        return "\n\n".join(parts)

    def _parse_search_response(self, response: str) -> dict:
        """
        Parse the raw LLM string response into a Python dict.

        Strips markdown code fences (e.g. ```json ... ```) if present,
        then attempts JSON parsing. Logs an error and returns an empty
        dict if parsing fails.

        Args:
            response: Raw string output from the LLM, expected to be
                      a valid JSON object matching the travel package schema.

        Returns:
            A parsed dict containing the travel packages, or an empty dict
            if the response cannot be parsed as JSON.
        """
        try:
            clean = response.strip()
            if clean.startswith("```"):
                clean = re.sub(r"```(?:json)?\n?", "", clean).strip()
                clean = clean.rstrip("`").strip()
            return json.loads(clean)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM search response: {e}")
            logger.error(f"Raw response: {response[:500]}")
            return {}

    def _format_history_as_text(self, history: list[ChatMessage]) -> str:
        """
        Format a list of ChatMessage objects into a plain-text conversation
        log for use in the contextualize prompt.

        Args:
            history: List of ChatMessage objects ordered from oldest to newest.

        Returns:
            A newline-separated string with each message prefixed by its role,
            e.g. "User: ...\nAssistant: ...". Returns "No previous conversation."
            if history is empty.
        """
        if not history:
            return "No previous conversation."

        lines = []
        for msg in history:
            role = "User" if msg.role == ChatRole.USER else "Assistant"
            lines.append(f"{role}: {msg.content}")

        return "\n".join(lines)

    def _format_history_as_messages(self, history: list[ChatMessage]) -> list:
        """
        Convert a list of ChatMessage objects into LangChain message objects
        (HumanMessage / AIMessage) for use in the ReAct agent's chat history.

        Args:
            history: List of ChatMessage objects ordered from oldest to newest.

        Returns:
            A list of LangChain BaseMessage objects compatible with
            MessagesPlaceholder in a ChatPromptTemplate.
        """
        messages = []
        for msg in history:
            if msg.role == ChatRole.USER:
                messages.append(HumanMessage(content=msg.content))
            else:
                messages.append(AIMessage(content=msg.content))
        return messages

    def generate_title(self, first_message: str) -> str:
        """Generate a short chat session title from the user's first message."""
        llm = ChatOpenAI(
            model=self.config.contextualize_model,
            temperature=0,
            max_tokens=20,
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Generate a concise chat title (max 6 words) that captures the topic. "
             "Return ONLY the title, no quotes, no punctuation at the end."),
            ("human", "{message}"),
        ])
        chain = prompt | llm | StrOutputParser()
        return chain.invoke({"message": first_message}).strip()[:100]

    def _translate_destination(self, destination: str) -> str:
        """Translate non-English destination names to English for API compatibility."""
        if destination.isascii():
            return destination
        llm = ChatOpenAI(
            model=self.config.contextualize_model,
            temperature=0,
            max_tokens=20,
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Translate the given place name to English. "
             "Return ONLY the English name, nothing else."),
            ("human", "{destination}"),
        ])
        chain = prompt | llm | StrOutputParser()
        translated = chain.invoke({"destination": destination}).strip()
        logger.info("Translated destination: %s -> %s", destination, translated)
        return translated or destination