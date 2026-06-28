# TriageMate — container image for the ADK web app.
# Demonstrates deployability: builds and runs the same way locally or on a managed
# runtime such as Cloud Run. The GEMINI_API_KEY is supplied at runtime, never baked in.
FROM python:3.12-slim

# Install uv (fast Python package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies first for better layer caching
COPY pyproject.toml ./
RUN uv sync --no-dev

# Copy the application
COPY triage_agent/ ./triage_agent/
COPY mcp_server/ ./mcp_server/
COPY skills/ ./skills/

# Cloud Run / container platforms inject PORT; ADK web honors --port
ENV PORT=8080
EXPOSE 8080

# GEMINI_API_KEY must be provided at runtime, e.g.:
#   docker run -e GEMINI_API_KEY=... -p 8080:8080 triagemate
CMD ["sh", "-c", "uv run adk web --host 0.0.0.0 --port ${PORT}"]
