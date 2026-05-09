# Getting started

Quick guide to get your **Jarvis** instance up and running in minutes.

## Requirements

- **Docker** ≥ 24 and **Docker Compose** ≥ 2.20
- **Python** ≥ 3.12 (for server-side agents)
- **Node.js** ≥ 20 (for frontend and web agents)
- **Git**
- (optional) NVIDIA GPU with CUDA for local models via Ollama

## 1. Clone the repository

```bash
git clone https://github.com/fedcal/open-jarvis.git
cd open-jarvis
```

## 2. Configure environment variables

Copy the template and customise it:

```bash
cp .env.example .env
```

!!! warning "Security"
    The `.env` file is gitignored on purpose: it contains your personal tokens and must never be committed.
    Only `.env.example` is tracked by the repository — it is the template for other developers.

Minimum variables for the MVP:

```env
SERVER_SECRET_KEY=...      # generate with: openssl rand -hex 32
DATABASE_URL=...
JARVIS_MODEL_LARGE=...     # e.g. anthropic/claude-sonnet-4-6
ANTHROPIC_API_KEY=...      # or OPENAI_API_KEY, GROQ_API_KEY, etc.
```

## 3. Start the services

```bash
docker compose up -d
```

Services started:

- **server** — main API (port `8080`)
- **postgres** — relational storage (port `5432`)
- **qdrant** — vector store (port `6333`)
- **redis** — cache and pub/sub (port `6379`)
- **frontend** — web UI (port `3000`)

## 4. Verify installation

```bash
curl http://localhost:8080/health
```

Expected response:

```json
{"status": "ok", "version": "0.1.0"}
```

Open your browser at [http://localhost:3000](http://localhost:3000).

## 5. Enrol your first device

From the terminal:

```bash
docker compose exec server jarvis enroll --type=desktop
```

A QR code will be displayed for pairing through the mobile app.

## Next steps

- 🏗️ Study the [architecture](../architecture/index.md)
- 📱 Configure a [device](../devices/index.md)
- 🤝 Learn how to [contribute](../contributing/index.md)
