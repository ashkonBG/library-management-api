# ── Stage 1: dependency installation ─────────────────────────────────────────
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Copy dependency manifests first for better layer caching
COPY pyproject.toml uv.lock* ./

# Install dependencies into the project's virtual environment
RUN uv sync --frozen --no-dev

# ── Stage 2: runtime image ────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy the virtual environment built in the previous stage
COPY --from=builder /app/.venv /app/.venv

# Copy application source
COPY . .

# Make the data directory for the SQLite file
RUN mkdir -p /app/data

# Ensure the venv binaries are on PATH
ENV PATH="/app/.venv/bin:$PATH"

# Expose the API port
EXPOSE 8000

# Run migrations then start Uvicorn
CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000"]
