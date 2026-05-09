# Installation

This page covers the installation of the **Jarvis server** and the desktop agent. For mobile, watch and medical-wearable enrolment see the dedicated pages under [Integrations](../integrations/mobile.md).

## Minimum hardware requirements

| Profile | CPU | RAM | Storage | GPU |
|---|---|---|---|---|
| **Local dev** | 4 cores | 8 GB | 30 GB SSD | not required |
| **Home self-host** | 6 cores | 16 GB | 100 GB SSD | optional (recommended for local models) |
| **Personal prod** | 8 cores | 32 GB | 500 GB NVMe | NVIDIA with CUDA (for Ollama) |

## Software requirements

- **Docker** ≥ 24 + **Docker Compose** ≥ 2.20
- **Git** ≥ 2.30
- **make** (optional but recommended)
- **Python 3.12** + **Node.js 20** (only if you develop the code locally)

### Installing Docker

=== "Linux (Ubuntu/Debian)"

    ```bash
    curl -fsSL https://get.docker.com | sudo sh
    sudo usermod -aG docker $USER
    newgrp docker
    docker --version
    ```

=== "macOS"

    ```bash
    brew install --cask docker
    open -a Docker
    ```

=== "Windows"

    1. Install **WSL2** (`wsl --install`)
    2. Download and install **Docker Desktop** with WSL2 backend
    3. Enable integration with your Linux distro

## 1. Clone the repository

```bash
git clone https://github.com/fedcal/open-jarvis.git
cd open-jarvis
```

## 2. Minimum configuration

```bash
cp .env.example .env
```

!!! warning "Secret safety"
    The `.env` file contains tokens and passwords. It is **gitignored on purpose**: it will never be pushed to the repository. Only `.env.example` is tracked.

Edit `.env` with an editor:

```bash
nano .env    # or: code .env / vim .env
```

**Required** variables for first boot:

```env
SERVER_SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)
DATABASE_URL=postgresql://jarvis:jarvis@postgres:5432/jarvis
REDIS_URL=redis://redis:6379/0
QDRANT_URL=http://qdrant:6333

# At least one of the following LLM providers:
ANTHROPIC_API_KEY=sk-ant-...
# or
OPENAI_API_KEY=sk-...
# or (100% local LLM)
OLLAMA_BASE_URL=http://ollama:11434
```

All other variables (OAuth, medical wearables, scraping, AR/VR, finance) are **optional** and asked for as you activate the corresponding features.

## 3. Start services

```bash
docker compose up -d
```

To include **Ollama** as well (local LLM, 100% private):

```bash
docker compose --profile local-llm up -d
```

Verify that all containers are `healthy`:

```bash
docker compose ps
```

## 4. Verify installation

```bash
curl http://localhost:8080/health
```

Expected response:

```json
{ "status": "ok", "version": "0.1.0", "memory": "ok", "qdrant": "ok" }
```

Open your browser at **[http://localhost:3000](http://localhost:3000)** for the web UI.

## 5. Create admin account

On the first UI start you'll be prompted to create the first user. That user becomes the **admin** of the instance with permissions on everything.

Alternatively, from CLI:

```bash
docker compose exec server jarvis user create \
  --email your@email.com \
  --admin
```

## Future updates

```bash
git pull
docker compose pull
docker compose up -d
docker compose exec server jarvis db migrate
```

## Full uninstall

⚠️ This procedure deletes **all data**.

```bash
docker compose down -v   # stops everything and removes volumes
rm -rf .env data/        # removes config and local data
```

> Continue to → [Configuration](configuration.md)
