FROM python:3.12-slim

WORKDIR /app

# System deps for psycopg (PostgreSQL) and fonts for PDF generation
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq-dev \
        fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install dependencies (cached layer)
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

# Copy application code
COPY . .

# Copy airports data file
COPY app/agent/infrastructure/airports.dat app/agent/infrastructure/airports.dat

EXPOSE 8000

# Run alembic migrations then start the server
CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"]
