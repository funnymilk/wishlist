# Use Docker buildkit features
# Builder stage: install dependencies via Poetry and export requirements
FROM python:3.12-slim AS builder

ENV POETRY_VERSION=1.8.2 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/var/cache/pypoetry \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl build-essential git ca-certificates libffi-dev libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir "poetry==${POETRY_VERSION}"

WORKDIR /app

# Copy only pyproject and lockfile first for better caching
COPY pyproject.toml poetry.lock* /app/

# Export locked requirements and install into system environment (no virtualenv)
RUN poetry export -f requirements.txt --without-hashes --no-interaction -o requirements.txt \
    && python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Final image
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --shell /bin/sh -m app

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local /usr/local

# Copy project files (use .dockerignore to exclude alembic and other files)
COPY . /app

# Fix permissions
RUN chown -R app:app /app

USER app

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
