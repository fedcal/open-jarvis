# Server · Jarvis core backend

🇮🇹 Backend principale di Open-Jarvis. Espone API REST/WebSocket/gRPC, gestisce identità, memoria, orchestrazione e routing tra agenti.
🇬🇧 Open-Jarvis main backend. Exposes REST/WebSocket/gRPC APIs, manages identity, memory, orchestration and routing across agents.

## Layout

```text
server/
├── jarvis_server/
│   ├── api/          # FastAPI app · routes · middleware
│   ├── config/       # Pydantic Settings, environment loading
│   ├── domain/       # Domain models (entities, value objects)
│   ├── llm/          # LLM provider abstraction (planned)
│   ├── memory/       # mem0 / Qdrant adapters (planned)
│   ├── orchestration/  # LangGraph workflows (planned)
│   ├── routing/      # Capability + device routing (planned)
│   └── scraping/     # Crawl4AI / Firecrawl (planned)
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── pyproject.toml    # Build, deps, ruff, mypy, pytest config
├── Dockerfile        # Multi-stage build
└── README.md
```

## Stack

- **Python 3.12** · **FastAPI** · **Pydantic v2** · **Pydantic Settings**
- **structlog** · **httpx** · **orjson**
- Database: **PostgreSQL** (planned) · cache: **Redis** (planned) · vectors: **Qdrant** (planned)
- Test: **pytest** · **pytest-asyncio** · **pytest-cov** · **respx**
- Lint: **ruff** · Types: **mypy** strict

## Quick start

```bash
cd server
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Run dev server
uvicorn jarvis_server.api.main:app --reload --port 8080

# Run tests
pytest

# Lint + type
ruff check .
ruff format --check .
mypy jarvis_server
```

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness/readiness probe |
| GET | `/docs` | Interactive OpenAPI (Swagger UI) |
| GET | `/redoc` | Alternative OpenAPI UI |
| GET | `/openapi.json` | OpenAPI 3.1 schema |

## Environment variables

All settings use the `JARVIS_` prefix. See `.env.example` at the repo root for the full list.

## Status

🟢 Phase 1.0 foundation complete (FastAPI, Settings, health endpoint, tests, CI)
⚪ Phase 1.x next: identity, memory, LLM router, chat endpoints

See [Implementation status](https://fedcal.github.io/open-jarvis/status/) for the live matrix.
