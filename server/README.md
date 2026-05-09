# Server · Backend principale

🇮🇹 Backend principale di Jarvis. Espone API REST/WebSocket/gRPC, gestisce identità, memoria, orchestrazione e routing tra agenti.
🇬🇧 Jarvis main backend. Exposes REST/WebSocket/gRPC APIs, manages identity, memory, orchestration and routing across agents.

## Layout

```text
server/
├── api/             # REST · WebSocket · gRPC endpoints
├── auth/            # OAuth · device pairing · JWT
├── memory/          # mem0 · Qdrant · Zep adapters
├── llm/             # Model abstraction (Ollama · Anthropic · OpenAI · Groq)
├── orchestration/   # LangGraph workflows · MCP / A2A protocols
├── routing/         # Capability & device routing
├── scraping/        # Crawl4AI · Firecrawl · Jina pipelines
└── tests/           # pytest suite
```

## Stack

- **Python 3.12** · **FastAPI** · **Pydantic AI** · **LangGraph**
- **PostgreSQL** + **Redis** + **Qdrant**

## Quickstart

```bash
cd server
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn api.main:app --reload
```

🇮🇹 Status: 🚧 work in progress.
🇬🇧 Status: 🚧 work in progress.
