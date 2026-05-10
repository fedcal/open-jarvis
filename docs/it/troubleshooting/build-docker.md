---
title: "Problemi di build e Docker · Open-Jarvis"
description: "Errori frequenti durante la build dei container Open-Jarvis (Docker, pip wheel, Python, Tauri, Expo) e fix verificati."
keywords: "open-jarvis docker build error, pip wheel readme, hatchling, build fix"
---

# Problemi comuni · Build & Docker

## `Readme file does not exist: README.md`

```text
=> ERROR [builder 6/6] RUN pip install --upgrade pip && pip wheel --wheel-dir /wheels .
…
OSError: Readme file does not exist: README.md
…
ERROR: Encountered error while generating package metadata.
failed to solve: process "/bin/sh -c pip install --upgrade pip && pip wheel --wheel-dir /wheels ."
did not complete successfully: exit code: 1
```

**Sintomo.** `docker build` (o `docker compose build`) si interrompe nel
secondo stage del builder, durante `pip wheel`. Il messaggio chiave è
`Readme file does not exist: README.md`.

**Causa.** `pyproject.toml` dichiara:

```toml
[project]
readme = "README.md"
```

Hatchling (il backend di build) **richiede** che il file referenziato
esista nel build context. Il Dockerfile però copia solo i file Python
e il `pyproject.toml`, dimenticando il `README.md`. Risultato: il
metadata generation fallisce e l'intera build viene abortita.

Lo stesso errore appare se hai eliminato il `README.md` dal repo o se
il tuo `.dockerignore` lo esclude.

**Fix.**

1. Aggiungi il `README.md` al `COPY` del builder stage:

   ```diff
    # Install dependencies first to leverage layer caching.
   -COPY pyproject.toml ./
   +COPY pyproject.toml README.md ./
    COPY jarvis_server ./jarvis_server
    RUN pip install --upgrade pip && \
        pip wheel --wheel-dir /wheels .
   ```

2. Verifica che `.dockerignore` **non** filtri il README:

   ```bash
   grep -E '^README' server/.dockerignore && echo "PROBLEMA"
   ```

3. Ribuilda:

   ```bash
   docker compose build --no-cache server
   ```

4. **Verifica**:

   ```bash
   docker compose run --rm server python -c "import jarvis_server; print('OK', jarvis_server.__version__)"
   ```

**Prevenzione.** La regola generale: **se `pyproject.toml` cita un file,
quel file deve essere nel build context**. Nello specifico:

- `readme = "README.md"` → COPY README.md
- `license-files = [...]` → COPY LICENSE / NOTICE
- `dynamic = ["version"]` con `__about__.py` → assicurati di copiare
  il package dove vive

## `pip wheel` molto lento al primo `docker build`

**Sintomo.** Il primo build richiede 10+ minuti.

**Causa.** Le wheel non sono in cache locale; pip scarica e compila.

**Fix.** Abilita il **BuildKit cache mount**:

```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip wheel --wheel-dir /wheels .
```

Build successivi sono ~5× più veloci. Richiede `# syntax=docker/dockerfile:1.7`
in cima al Dockerfile (già presente).

## `permission denied: ./scripts/something.sh`

**Sintomo.** Un'operazione lanciata via Compose fallisce con
`/bin/sh: ./scripts/x.sh: Permission denied`.

**Causa.** Lo script non ha il bit di esecuzione nel file system del
container, perché Git su Windows ignora i permessi POSIX.

**Fix.**

```bash
git update-index --chmod=+x scripts/x.sh
git add scripts/x.sh
git commit -m "chore: mark x.sh executable"
```

Oppure, dentro il Dockerfile prima di lanciarlo:

```dockerfile
RUN chmod +x /app/scripts/x.sh
```

## `port is already allocated` (8080, 5432, 6379, 6333)

**Sintomo.** `docker compose up` fallisce con
`Bind for 0.0.0.0:8080 failed: port is already allocated`.

**Causa.** Una versione precedente del server è ancora attiva, oppure
un processo non-Docker sta ascoltando sulla stessa porta. Sui PC dev
è comune avere già un Postgres locale (5432), un Redis (6379), un
Qdrant (6333), o tool Java/IDE su 8080.

**Fix.** Sovrascrivi le porte host nel `.env` (le variabili sono
mappate dal `docker-compose.yml` con default sicuri):

```bash
# .env
JARVIS_HOST_PORT=8090         # API server
POSTGRES_HOST_PORT=15432
REDIS_HOST_PORT=16379
QDRANT_HOST_PORT=16333
QDRANT_GRPC_HOST_PORT=16334
```

Dopo aver modificato il `.env`:

```bash
docker compose down
docker compose up -d
docker compose ps              # verifica le nuove mapping in colonna PORTS
curl http://localhost:8090/health
```

Per scoprire chi tiene una porta:

```bash
ss -tlnp | grep -E '8080|5432|6379|6333'    # Linux
lsof -iTCP -sTCP:LISTEN | grep 8080         # macOS / BSD
Get-NetTCPConnection -State Listen -LocalPort 8080  # Windows PowerShell
```

!!! warning "Le porte interne dei container restano standard"
    Le porte **interne** ai container (8080 per il server, 5432 per
    Postgres, …) non cambiano mai. Solo le porte **host** lato sinistro
    della mapping (`HOST:CONTAINER`). Quindi i parametri tipo
    `JARVIS_DATABASE_URL` puntano a `postgres:5432` (nome servizio),
    non `localhost:15432`.

## `no space left on device`

**Sintomo.** Build fallisce a metà o `docker compose up` non parte.

**Fix immediato:**

```bash
docker system df          # vedi quanto occupano le immagini
docker system prune -af   # rimuovi immagini, container e build cache non usati
docker volume prune       # ATTENZIONE: cancella i volumi non referenziati
```

**Prevenzione.** Aggiungi al cron del server:

```cron
0 3 * * 0 /usr/bin/docker system prune -af --filter "until=168h"
```

(prune settimanale di immagini più vecchie di 7 giorni).

## Build fallisce solo su Apple Silicon (`linux/arm64`)

**Sintomo.** `psycopg-binary` o `cryptography` non hanno wheel `arm64`
per la versione Python richiesta.

**Fix temporaneo.** Forza la build per `linux/amd64` con emulazione:

```bash
docker buildx build --platform linux/amd64 -t jarvis-server:dev .
```

**Fix corretto.** Verifica le versioni delle dipendenze su PyPI:
quasi sempre c'è una release più recente con wheel arm64. Aggiorna
`pyproject.toml` e ricompila.

## Image size sovradimensionata

**Sintomo.** `jarvis-server:dev` pesa >1 GB.

**Causa.** Il build sta installando dipendenze di sviluppo o compilatori
nello stage finale.

**Fix.** Verifica che il Dockerfile usi un **multi-stage** (builder +
runtime, già nostra struttura) e che il runtime non abbia
`build-essential`. Comando di check:

```bash
docker history jarvis-server:dev --no-trunc | head -20
```

## `failed to solve: cannot resolve image`

**Sintomo.** `docker compose pull` fallisce con
`pull access denied for ghcr.io/fedcal/open-jarvis`.

**Fix.** Le immagini ufficiali non sono ancora pubblicate su GHCR (Fase
0). Per ora compila localmente con `docker compose build`. Quando
arriveranno le immagini firmate, il `docker-compose.yml` userà
`image: ghcr.io/fedcal/open-jarvis:vX.Y.Z`.

## Vedi anche

- [Aggiornamento server](../user-manual/updates.md#1-aggiornare-il-server)
- [Installazione server VPS](../user-manual/install/server.md)
- [Glossario error code](index.md#glossario-degli-error-code)
