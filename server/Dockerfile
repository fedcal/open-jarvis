# syntax=docker/dockerfile:1.7

# ---------- Stage 1: builder ----------
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Install build deps (kept out of runtime image)
RUN apt-get update \
 && apt-get install --no-install-recommends -y build-essential curl \
 && rm -rf /var/lib/apt/lists/*

# Install dependencies first to leverage layer caching.
# README.md is required because pyproject.toml declares `readme = "README.md"`;
# without it `pip wheel` aborts during metadata generation.
COPY pyproject.toml README.md ./
COPY jarvis_server ./jarvis_server
RUN pip install --upgrade pip && \
    pip wheel --wheel-dir /wheels .

# ---------- Stage 2: runtime ----------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    JARVIS_ENVIRONMENT=production \
    JARVIS_SERVER_HOST=0.0.0.0 \
    JARVIS_SERVER_PORT=8080

# Create unprivileged user
RUN groupadd --system --gid 1000 jarvis && \
    useradd --system --uid 1000 --gid jarvis --create-home --shell /usr/sbin/nologin jarvis

WORKDIR /app

# Install only the wheels from the builder
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl && rm -rf /wheels

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys; \
import json; r=urllib.request.urlopen('http://127.0.0.1:8080/health',timeout=3); \
sys.exit(0 if json.loads(r.read())['status']=='ok' else 1)" || exit 1

USER jarvis

EXPOSE 8080

CMD ["uvicorn", "jarvis_server.api.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2", "--proxy-headers"]
