# AventraAI

AventraAI is a full-stack travel planning application powered by a conversational AI agent. Users describe where they want to go, and the system produces structured multi-day itineraries with daily activities, weather context, points of interest, flight and hotel links, and downloadable PDF plans. Beyond one-shot search, users can have open-ended travel conversations where the agent can look up live weather, search for places, and pull details from Google Maps on demand.

The project runs as a React single-page application served through Vercel, backed by a FastAPI service deployed on Render. The PostgreSQL database is hosted on Supabase. All travel knowledge is grounded in a Retrieval-Augmented Generation (RAG) pipeline built on Pinecone and OpenAI embeddings, fed by city guides sourced from Wikivoyage.

---

## Architecture

The system is organized into three layers: a React frontend, a FastAPI backend, and a set of external services that provide domain knowledge and infrastructure. The agent operates in two distinct modes, each with its own execution flow.

### Search Mode (Itinerary Generation)

When a user fills out the itinerary form, the agent runs a deterministic pipeline that gathers all necessary context before making a single LLM call to generate the itinerary. Non-English destination names are first translated using GPT-4o-mini to ensure compatibility with all downstream APIs.

<img src="assets/search-mode.gif" alt="Search mode pipeline diagram" width="700">

### Chat Mode

In chat, the agent operates as a ReAct loop. It has access to tools and RAG context, and can make multiple reasoning steps before responding. This is what differentiates it from a generic LLM chatbot: every response is grounded in live data from the same APIs and knowledge base used by the search pipeline.

<img src="assets/chat-mode.gif" alt="Chat mode pipeline diagram" width="700">

When a user submits a search, the request flows through the agent pipeline: the destination is translated to English if needed, the RAG system is queried for relevant city knowledge, weather is fetched, places are resolved, and all of this context is assembled into a single prompt sent to the LLM. The model returns a structured JSON itinerary that gets persisted in PostgreSQL and rendered on the frontend.

For chat, the agent operates in a ReAct loop. It classifies incoming messages with a lightweight topic guard, reformulates follow-ups into standalone queries using conversation history, retrieves RAG context, and then reasons through tool calls (weather lookup, place search, place details) before producing a final text response. This is a deliberate design choice: the chat mode is not a thin wrapper around a generic LLM. Every conversational turn is grounded in the same RAG knowledge base and live API integrations used by the search pipeline. When a user asks "what's the weather like in Lisbon in March" or "find me a good restaurant near the Acropolis," the agent does not rely on the model's parametric memory alone -- it calls the actual weather and places APIs in real time and cross-references the city guide context from Pinecone. This makes the chat responses factually anchored to current data rather than dependent on whatever the base model happens to recall from its training set, which is what separates it from a general-purpose chatbot that simply generates plausible-sounding travel advice.

---

## Tech Stack

### Local vs Production

| Component | Local Development | Production |
|-----------|------------------|------------|
| Frontend | Vite dev server (localhost:5173) | Vercel (static SPA) |
| Backend | Uvicorn with --reload (localhost:8000) | Render (Docker, Uvicorn) |
| Database | PostgreSQL (local instance) | Supabase (managed PostgreSQL) |
| Vector Store | ChromaDB (city-guides index) | Pinecone (city-guides index) |
| Embeddings | OpenAI text-embedding-3-small | OpenAI text-embedding-3-small |
| LLM | OpenAI GPT-4o-mini / GPT-4o | OpenAI GPT-4o-mini / GPT-4o |
| Observability | LangSmith | Sentry + LangSmith |

### Full Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Vite, React Bootstrap, React Router, Axios |
| Backend | Python 3.12, FastAPI, SQLModel, Alembic, Pydantic Settings |
| Database | PostgreSQL (psycopg), hosted on Supabase in production |
| AI / LLM | LangChain, OpenAI GPT-4o and GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small |
| Vector Store | Pinecone (city-guides index) |
| Authentication | JWT (HS256, Argon2 hashing), Google OAuth 2.0 |
| Payments | Stripe Checkout and Webhooks |
| Email | Resend |
| Observability | Sentry (FastAPI + SQLAlchemy tracing), LangSmith (optional) |
| Deployment | Vercel (frontend), Render with Docker (backend), Supabase (database) |
| CI/CD | GitHub Actions, auto-deploy on push via Render and Vercel |
| PDF Generation | fpdf2 |

---

## RAG Pipeline and On-Demand Indexing

The knowledge base is built around city travel guides stored as markdown files. Each guide is sourced from Wikivoyage and covers sections like history, climate, things to see, food, nightlife, neighborhoods, and practical travel tips.

### How indexing works

Guides are split by markdown headers into semantically meaningful chunks (by city and section), embedded using OpenAI's `text-embedding-3-small` model, and upserted into a Pinecone index called `city-guides`. At retrieval time, the system pulls the top 5 most relevant chunks for a given query using similarity search, with results cached for 24 hours to reduce redundant calls.

### On-demand city guide fetching and indexing

This is where it gets interesting. The system does not require every city to be pre-indexed. When a user searches for a destination that has no local guide file, the pipeline automatically fetches the corresponding Wikivoyage article, filters it down to travel-relevant sections, truncates it to a reasonable length, writes it as a markdown file, and indexes it into Pinecone in real time. The user's search then proceeds with the freshly indexed knowledge, as if the city had always been part of the database.

This means the knowledge base grows organically based on actual user demand. Every new city a user asks about becomes permanently available for all future queries.

Whenever a new city is indexed on demand, the system sends an email notification with the city name so that new additions to the knowledge base are tracked without needing to check logs.

<img src="assets/tbilisi-indexed.png" alt="Email notification when a new city is indexed on demand" width="500">

There is also a bulk indexing pipeline (under `backend/scripts/`) used for initial setup. It downloads guides for a curated list of major global destinations, cleans them, and indexes the full set into Pinecone in one pass.

### Current coverage

The knowledge base ships with approximately 105 pre-indexed city guides covering major destinations worldwide. Any city with a Wikivoyage article can be added on the fly through the on-demand mechanism described above.

### Caching strategy

RAG retrieval and external API calls are the two most expensive operations in the pipeline, both in terms of latency and cost. To keep these under control, the system uses TTL-based caching at multiple levels:

- **RAG results** are cached for 24 hours. If the same destination or a similar query comes up within that window, the system serves the cached chunks instead of making a new embedding call and Pinecone query. This avoids redundant OpenAI embedding costs and Pinecone read units for popular destinations that get searched repeatedly.

- **Google Places search results and place details** are cached for 24 hours. Place photos are cached for one hour (since photo URLs expire). This is significant because the Google Places API bills per request, and the same attractions and restaurants tend to come up across different users searching the same city.

- **Weather geocoding and forecast data** are cached similarly, which prevents repeated calls to Open-Meteo for the same location within a short timeframe.

The net effect is that the first search for a given city pays the full cost of all API calls, but subsequent searches within the cache window are served almost entirely from memory. For a destination like Paris or Tokyo that might get searched dozens of times a day, this translates to a substantial reduction in external API usage.

---

## Backend

The backend is a FastAPI application structured around a clear separation of concerns:

### Agent Pipeline (`app/agent/`)

The core intelligence of the application. The `TravelAgentPipeline` class exposes two main flows:

- **Search mode**: A deterministic pipeline that translates the destination, ensures RAG coverage, fetches weather from Open-Meteo, resolves IATA airport codes for Skyscanner links, queries Google Places for attractions and restaurants, and sends all collected context to the LLM with strict JSON output requirements. The model must return exactly one package with one itinerary entry per trip day and four activities per day.

- **Chat mode**: A ReAct-style agent built with LangChain that can call weather, place search, and place detail tools. Messages go through a topic guard that rejects harmful content and redirects off-topic queries, and follow-up questions are reformulated into standalone queries using a lightweight contextualization step.

Free-tier users get `gpt-4o-mini` (fast, cost-effective). Paid users get `gpt-4o` (higher quality, better reasoning). Search uses a low temperature (0.2) for consistency; chat uses a higher temperature (0.7) for more natural conversation.

### Prompting Strategy

All prompts follow the PCTF framework (Persona, Context, Task, Format), which gives the model a clear identity, the information it needs, what it should do, and how it should structure its output. This keeps behavior predictable across different models and temperatures.

The system uses five distinct prompts, each with a specific role:

- **Search system prompt** (`TRAVEL_SEARCH_SYSTEM_PROMPT`): The main prompt for itinerary generation. It defines the travel agent persona, tells the model what context sources are available (city guides, weather, places), specifies the exact JSON schema it must return, and enforces structural constraints like one itinerary entry per trip day and exactly four activities per day. It also includes safety rules and instruction isolation directives to prevent prompt injection through user input or RAG content.

- **Chat system prompt** (`TRAVEL_CHAT_SYSTEM_PROMPT`): Governs the conversational agent. Same PCTF structure but with a different task: engage in natural travel conversation, ask one clarifying question at a time, suggest the search feature when the user is ready to plan, and always call the places tool before claiming it has no information. Output format is plain text rather than JSON.

- **Contextualization prompt** (`CONTEXTUALIZE_PROMPT`): A lightweight prompt used to reformulate follow-up messages into standalone queries. Uses few-shot examples to show the model what a good reformulation looks like ("What about the weather there?" with Prague context becomes "What is the weather like in Prague?"). This is necessary because RAG retrieval works best with self-contained queries, and raw follow-ups like "Is it expensive?" are meaningless without conversation context.

- **Topic guard prompt** (`TOPIC_GUARD_PROMPT`): A cheap classifier that runs on `gpt-4o-mini` before the full agent is invoked. It categorizes each message as `TRAVEL_OK`, `HARMFUL`, or off-topic. Travel-related messages pass through; harmful messages trigger a hardcoded refusal; off-topic messages get a short redirect back to travel. Running this on a fast, cheap model avoids wasting a full agent invocation on messages that will be filtered anyway.

- **Harmful content refusal** (`HARMFUL_CONTENT_REFUSAL_MESSAGE`): A hardcoded string, not a generated response. When the topic guard returns `HARMFUL`, this fixed message is returned directly without involving the model. This is intentional: a small guard model should never improvise the wording of a safety refusal, because there is a risk it could echo or engage with the harmful content while refusing it.

All prompts include instruction isolation rules. User input, conversation history, and RAG content are wrapped in XML-style tags (using `wrap_untrusted()`) so the model can distinguish data from instructions. The wrapper also strips any embedded tag markers from the content to prevent breakout attempts where injected text tries to close the tag and inject new instructions.

### Infrastructure Services (`app/agent/infrastructure/`)

- **Weather**: Uses Open-Meteo for geocoding and forecasts. For trips within 16 days, it uses the forecast API; for trips further out, it pulls historical data from the same dates one year prior. Returns min/max temperatures, precipitation, and weather descriptions.

- **Places**: Integrates with Google Places API (New) for text search, place details, and photos. Results are cached for 24 hours, photos for one hour.

- **Airport Codes**: Resolves city names to IATA codes using bundled OpenFlights data with manual overrides for edge cases. Used to construct Skyscanner deep links.

- **City Guide Fetcher**: The on-demand Wikivoyage integration described above. Includes email notification (via Resend) when a new city is indexed.

### API Routes (`app/api/routes/`)

- **Authentication**: Google OAuth flow and standard email/password login with JWT tokens. Password hashing uses Argon2 with a bcrypt verification fallback.
- **Travel**: Creates search sessions, runs the agent pipeline, enforces usage quotas (3 free / 20 paid searches per month), and generates PDF itineraries.
- **Chat**: Session management, message persistence, agent interaction, title generation, pin/rename/delete operations. Enforces 50 free / 500 paid messages per monthly period.
- **Users**: Registration, profile management, password updates, onboarding tracking, and superuser administration.
- **Payments**: Stripe Checkout session creation, subscription confirmation, cancellation at period end, and webhook handling for asynchronous Stripe events.

### Data Layer (`app/models.py`, `app/crud.py`)

The database schema covers users (with Google identity linking and subscription state), chat sessions and messages, search sessions, and a full travel package hierarchy (package, itinerary, activity, accommodation). Migrations are managed through Alembic.

### Entity Diagram

<img src="assets/er-diagram.png" alt="Database entity relationship diagram" width="750">

---

## Frontend

The frontend is a React 19 single-page application built with TypeScript and Vite. It uses React Bootstrap for layout and styling, React Router for navigation, and Axios for API communication.

### Key Screens

- **Landing Page**: Product overview with plan comparison and rotating destination visuals.
- **Chat Page**: The main interface. Supports both free-form conversation and structured travel search through a toggleable form. Messages render with basic markdown support, and travel packages appear as interactive cards with PDF download. Responses are revealed progressively to simulate streaming.
- **Profile Page**: Displays usage quotas, subscription status, and allows profile editing and subscription cancellation.
- **Auth Pages**: Login, registration, password recovery, and Google OAuth.

### Notable Features

- **Voice input**: Browser-based speech recognition (English) is integrated into the chat input, allowing users to dictate messages.
- **Onboarding tour**: First-time users see a guided overlay highlighting the main UI elements.
- **Guest route handling**: Authenticated users are redirected away from login/register pages.
- **Simulated streaming**: The frontend progressively reveals complete API responses character by character to create a typing effect.

### Mobile Responsiveness

The interface adapts to mobile screens (below 768px) using a custom `useIsMobile()` hook that wraps `matchMedia`. On mobile, the sidebar collapses into a slide-out drawer accessible via a hamburger menu, the search form switches from a two-column grid to a single-column stack, the landing page hero scales down its typography and hides floating destination cards, and the profile page stacks name fields vertically. The onboarding tour also adapts by skipping the sidebar step (which is not visible on mobile) and constraining tooltip positioning to stay within the viewport. All changes are conditional on the hook's return value, so the desktop layout is completely unaffected.

---

## Deployment

The frontend deploys to **Vercel** as a static SPA with a catch-all rewrite for client-side routing. The backend deploys to **Render** using a Docker image based on Python 3.12 slim, with `uv` as the package manager. The container runs Alembic migrations at startup and serves the application through Uvicorn on port 8000. The PostgreSQL database is hosted on **Supabase**, which provides a managed Postgres instance with connection pooling.

Both Render and Vercel are connected to the GitHub repository and trigger a new build automatically on every push to `main`. On the CI side, a GitHub Actions workflow runs the backend test suite on every push and pull request that touches `backend/` -- it spins up a PostgreSQL service container, installs dependencies with `uv`, and executes pytest. This means every commit is validated before the deployment goes live.

> **Note:** The backend runs on Render's free tier, which spins down the server after 15 minutes of inactivity. The first request after a cold start takes approximately 50 seconds while the container boots up and runs migrations. Subsequent requests are fast. This only affects the very first interaction after an idle period.

### Environment Variables

The backend requires configuration for:

- `DATABASE_URL` (PostgreSQL connection string)
- `OPENAI_API_KEY`
- `PINECONE_API_KEY`
- `GOOGLE_MAPS_API_KEY`
- `RESEND_API_KEY`
- `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET`
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
- `SECRET_KEY` (JWT signing)
- `SENTRY_DSN` (optional)

The frontend requires:

- `VITE_API_URL` (backend base URL)
- `VITE_GOOGLE_CLIENT_ID`

---

## Testing

The backend has a pytest-based test suite that runs automatically on every push and pull request via GitHub Actions. The CI pipeline spins up a PostgreSQL service container, installs dependencies, and runs all tests before a deployment can proceed. No code reaches production without passing the full suite.

The tests are unit-level and focused on the components that carry the most risk: the agent pipeline, external service integrations, security utilities, and business rules.

### What is tested

- **Agent pipeline** (`test_agent_pipeline.py`): Validates LLM JSON parsing (including malformed and fenced responses), chat history formatting, model tier selection based on subscription level, and destination translation passthrough. The pipeline is constructed without its production initialization using a patched `__init__`, so tests exercise the helper methods in isolation without calling OpenAI.

- **Airport codes** (`test_airport_codes.py`): Verifies IATA resolution for major cities, case insensitivity, data-backed lookups from the bundled OpenFlights dataset, and graceful handling of unknown cities, empty input, and `None`.

- **Business rules** (`test_business_rules.py`): Guards the freemium/paid usage constants (search and message quotas), maximum pinned chats, trip duration arithmetic, and payment return-path allowlisting. These tests exist to catch accidental changes to values that affect billing and rate limiting.

- **Enums** (`test_enums.py`): Asserts the exact set of values for all domain enums (subscription tiers, chat roles, package tiers, activity types, currencies, trip types, search statuses). This prevents silent breakage when someone adds or renames an enum member without updating the rest of the codebase.

- **Places service** (`test_places.py`): Tests the TTL caching layer for search, detail, and photo requests, including cache key normalization. Also tests the expired place-ID fallback mechanism, where a failed detail lookup triggers a fresh search and retries with the new ID.

- **Prompt injection isolation** (`test_prompts.py`): Validates `wrap_untrusted()` -- the XML tag wrapper that separates data from instructions. Tests cover standard wrapping, stripping of embedded opening/closing tags that could allow breakout, empty content, and preservation of unrelated tags.

- **RAG retrieval** (`test_rag.py`): Verifies that repeated queries for the same destination hit the cache instead of calling Pinecone again, and that different queries produce distinct cache entries.

- **Security** (`test_security.py`): Tests Argon2 password hashing and verification (correct password, wrong password, non-plaintext hash), and JWT token creation by decoding tokens and asserting subject and expiry claims against the configured secret.

- **Weather service** (`test_weather.py`): Tests normal weather retrieval with mocked geocoding and forecast responses, empty geocoding fallback, and date range validation with dynamically computed dates.

### Testing patterns

External HTTP calls (OpenAI, Google Places, Open-Meteo, Pinecone) are mocked using `unittest.mock.patch` with `side_effect` sequences to simulate multi-step API interactions. Module-level caches are cleared in `setup_method` before each test to guarantee isolation. Security and enum tests run against the real implementations without mocking, since they are fast and deterministic.

---

## Project Structure

```
backend/
  app/
    agent/               # AI pipeline, prompts, configuration
      infrastructure/    # Weather, places, airports, city guide fetcher
    api/
      routes/            # Auth, chat, travel, users, payments
    core/                # Config, database, security
    rag/                 # RAG service, ingestion, retrieval
      data/              # City guide markdown files
  scripts/               # Bulk fetching and indexing utilities
  tests/                 # Unit and integration tests

frontend/
  src/
    components/          # Reusable UI components
    context/             # React auth context
    hooks/               # Custom hooks (auth, speech recognition)
    pages/               # Route-level page components
    services/            # API client and auth service
```

---

## Development

### Backend

```bash
cd backend
uv sync
cp .env.example .env  # configure your keys
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
cd backend
pytest
```

### Bulk Indexing

To populate the knowledge base with the default city set:

```bash
cd backend
python scripts/fetch_city_guides.py
python scripts/run_indexer.py
```
