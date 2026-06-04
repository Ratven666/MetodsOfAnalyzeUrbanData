# =============================================================================
# Stage 1: install Python dependencies (cached as long as requirements.txt
#           does not change — standard Docker layer-caching best practice)
# =============================================================================
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip \
    && pip install --prefix=/install -r /app/requirements.txt

# =============================================================================
# Stage 2: lean runtime image (no build tools, smaller final image)
# =============================================================================
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Only libpq runtime — no gcc needed
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy only necessary project files
COPY fastapi_wheather_lab /app/fastapi_wheather_lab
COPY migrations /app/migrations
COPY alembic.ini /app/alembic.ini

EXPOSE 8000

# Default command (overridden by docker-compose command: to run migrations first)
CMD ["uvicorn", "fastapi_wheather_lab.main:app", "--host", "0.0.0.0", "--port", "8000"]
