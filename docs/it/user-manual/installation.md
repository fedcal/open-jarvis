# Installazione

Questa pagina copre l'installazione del **server Jarvis** e dell'agente desktop. Per l'enrolment dei device mobile, watch e wearable medicali vedi le pagine specifiche in [Integrazioni](../integrations/mobile.md).

## Requisiti hardware minimi

| Profilo | CPU | RAM | Storage | GPU |
|---|---|---|---|---|
| **Sviluppo locale** | 4 core | 8 GB | 30 GB SSD | non richiesta |
| **Self-host casalingo** | 6 core | 16 GB | 100 GB SSD | opzionale (consigliata per modelli locali) |
| **Produzione personale** | 8 core | 32 GB | 500 GB NVMe | NVIDIA con CUDA (per Ollama) |

## Requisiti software

- **Docker** ≥ 24 + **Docker Compose** ≥ 2.20
- **Git** ≥ 2.30
- **make** (opzionale ma raccomandato)
- **Python 3.12** + **Node.js 20** (solo se sviluppi codice localmente)

### Installazione Docker

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

    1. Installa **WSL2** (`wsl --install`)
    2. Scarica e installa **Docker Desktop** con backend WSL2
    3. Abilita l'integrazione con la tua distro Linux

## 1. Clone del repository

```bash
git clone https://github.com/fedcal/open-jarvis.git
cd open-jarvis
```

## 2. Configurazione minima

```bash
cp .env.example .env
```

!!! warning "Sicurezza segreti"
    Il file `.env` contiene token e password. È **gitignored** di proposito: non verrà mai pushato sul repository. Solo `.env.example` è tracciato.

Modifica `.env` con un editor:

```bash
nano .env    # oppure: code .env / vim .env
```

Variabili **obbligatorie** per il primo avvio:

```env
SERVER_SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)
DATABASE_URL=postgresql://jarvis:jarvis@postgres:5432/jarvis
REDIS_URL=redis://redis:6379/0
QDRANT_URL=http://qdrant:6333

# Almeno uno dei seguenti provider LLM:
ANTHROPIC_API_KEY=sk-ant-...
# oppure
OPENAI_API_KEY=sk-...
# oppure (LLM 100% locale)
OLLAMA_BASE_URL=http://ollama:11434
```

Tutte le altre variabili (OAuth, wearable medicali, scraping, AR/VR, finance) sono **opzionali** e vengono richieste man mano che attivi le feature corrispondenti.

## 3. Avvio dei servizi

```bash
docker compose up -d
```

Per includere anche **Ollama** (LLM locale, 100% privato):

```bash
docker compose --profile local-llm up -d
```

Verifica che tutti i container siano in `healthy`:

```bash
docker compose ps
```

## 4. Verifica installazione

```bash
curl http://localhost:8080/health
```

Risposta attesa:

```json
{ "status": "ok", "version": "0.1.0", "memory": "ok", "qdrant": "ok" }
```

Apri il browser su **[http://localhost:3000](http://localhost:3000)** per accedere all'UI web.

## 5. Creazione account amministratore

Al primo avvio dell'UI verrà richiesto di creare il primo utente. Questo utente diventa **admin** dell'istanza con permessi su tutto.

In alternativa, da CLI:

```bash
docker compose exec server jarvis user create \
  --email tua@email.com \
  --admin
```

## Aggiornamenti futuri

```bash
git pull
docker compose pull
docker compose up -d
docker compose exec server jarvis db migrate
```

## Disinstallazione completa

⚠️ Questa procedura cancella **tutti i dati**.

```bash
docker compose down -v   # ferma tutto e rimuove i volumi
rm -rf .env data/        # rimuove configurazione e dati locali
```

> Vai a → [Configurazione](configuration.md)
