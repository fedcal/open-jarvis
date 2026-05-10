---
title: "Problemi di avvio e runtime del server · Open-Jarvis"
description: "Errori che capitano al primo avvio del server (migrazioni Alembic, JWT signature, env vars, port collision) e fix verificati passo per passo."
keywords: "open-jarvis server crash, alembic upgrade, jwt signature failed, asyncpg, env_prefix, port already in use"
---

# Problemi comuni · Avvio del server

## `relation "users" does not exist` al primo `docker compose up`

```text
sqlalchemy.exc.ProgrammingError: (psycopg.errors.UndefinedTable)
relation "users" does not exist
LINE 2: FROM users
             ^
```

**Sintomo.** Lo stack parte, `/health` risponde, ma il primo
`/api/v1/auth/register` ritorna `500 Internal Server Error`.

**Causa.** Il database Postgres è creato ma **vuoto**: le migrazioni
Alembic non sono mai state applicate. Per default il container
`server` esegue al boot:

```sh
alembic upgrade head && exec uvicorn jarvis_server.api.main:app …
```

Se vedi questo errore, probabilmente:

- stai usando un'immagine **vecchia** del server (precedente alla
  release v0.1.1) che non lanciava `alembic upgrade`,
- oppure hai sovrascritto il `command:` nel `docker-compose.override.yml`,
- oppure hai migrato manualmente il database Postgres a una versione
  pulita senza ri-applicare le migration.

**Fix.**

```bash
# Forza l'apply delle migration
docker compose run --rm server alembic upgrade head

# Verifica le tabelle
docker compose exec postgres psql -U jarvis -d jarvis -c "\dt"
```

L'output deve elencare `users`, `devices`, `sessions`,
`mfa_credentials`, `audit_events`, `memory_items`, `pairing_codes` e
`alembic_version`.

**Prevenzione.**

- Non rimuovere `command:` dal compose: il prefisso `alembic upgrade`
  è intenzionale.
- Quando crei un `docker-compose.override.yml`, **estendi** il command,
  non sostituirlo.
- Per ambienti di produzione esegui le migration come **job separato**
  (Helm post-install hook, Argo CD pre-sync, ecc.) prima di rilasciare
  la nuova versione del server.

## `Signature verification failed` con `--workers 2` o più

```text
{"detail":"invalid access token: Signature verification failed."}
```

**Sintomo.** Login OK, ma le richieste successive con quel JWT
ricevono `401`. Riprovando, talvolta funziona — talvolta no.

**Causa.** In modalità sviluppo (senza
`JARVIS_JWT_PRIVATE_KEY_PEM`) il server **genera al boot una coppia
ES256 ephemera** per processo. Con `--workers >1` ogni worker
uvicorn ha la sua keypair: il token firmato dal worker A non è
verificabile dal worker B.

**Fix per il dev locale.** Nel `docker-compose.yml` il `command` è già
configurato con `--workers 1` per evitare questo problema:

```yaml
server:
  command: >
    sh -c "alembic upgrade head &&
           exec uvicorn jarvis_server.api.main:app
                --host 0.0.0.0 --port 8080
                --workers 1 --proxy-headers"
```

**Fix per produzione.** Imposta una keypair stabile via env:

```bash
# Genera una nuova keypair ES256
openssl ecparam -name prime256v1 -genkey -noout -out jwt-private.pem
openssl ec -in jwt-private.pem -pubout -out jwt-public.pem

# Esporta nel formato richiesto da Pydantic Settings
export JARVIS_JWT_PRIVATE_KEY_PEM="$(cat jwt-private.pem)"
export JARVIS_JWT_PUBLIC_KEY_PEM="$(cat jwt-public.pem)"
```

Conserva `jwt-private.pem` in un secret manager (Vault, AWS Secrets
Manager, ecc.). Da quel momento puoi tornare a `--workers 4` (o più)
in modo sicuro.

**Prevenzione.** `Settings.assert_production_safe()` rifiuta lo start
in `production` se le chiavi non sono configurate — è proprio per
questo motivo.

## `ModuleNotFoundError: No module named 'asyncpg'`

```text
File ".../sqlalchemy/dialects/postgresql/asyncpg.py", line 1094,
in import_dbapi
    return AsyncAdapt_asyncpg_dbapi(__import__("asyncpg"))
```

**Causa.** Stai usando lo schema URL `postgresql+asyncpg://...` ma il
server installa **psycopg3** (`psycopg[binary,pool]`), non `asyncpg`.

**Fix.** Cambia il driver nello URL:

```diff
- JARVIS_DATABASE_URL=postgresql+asyncpg://jarvis:jarvis@localhost:5432/jarvis
+ JARVIS_DATABASE_URL=postgresql+psycopg://jarvis:jarvis@localhost:5432/jarvis
```

`postgresql+psycopg` usa la modalità asincrona di psycopg3 (introdotta
nella v3.0). Performance e feature parity con asyncpg sono ottime per
Open-Jarvis.

**Quando dovresti usare asyncpg invece?** Casi specifici di **bench
high-throughput** dove la differenza in microsecondi conta.
Aggiungilo alle deps con `pip install asyncpg` o
`uv add asyncpg`.

## `port is already allocated`

Vedi [Build & Docker → port collision](build-docker.md#port-is-already-allocated-8080-5432-6379-6333).

In sintesi: sovrascrivi le porte host nel `.env`:

```bash
JARVIS_HOST_PORT=8090
POSTGRES_HOST_PORT=15432
REDIS_HOST_PORT=16379
QDRANT_HOST_PORT=16333
QDRANT_GRPC_HOST_PORT=16334
```

## `make server-dev` non legge `.env`

**Sintomo.** Hai impostato `JARVIS_DATABASE_URL=...` nel `.env` di
repo root, ma il server in dev mode usa il valore di default
(`sqlite+aiosqlite:///./jarvis-dev.db`).

**Causa.** `make server-dev` esegue `cd server && uv run uvicorn ...`:
pydantic-settings cerca `.env` nella cwd del processo, cioè in
`server/.env`, che non esiste.

**Fix.** Il Makefile passa già `--env-file ../.env` a uvicorn:

```bash
cd server && uv run uvicorn jarvis_server.api.main:app \
    --reload --host 0.0.0.0 --port 8080 --env-file ../.env
```

Se vedi ancora il problema, verifica che `make server-dev` sia
aggiornato (`grep env-file Makefile`).

## `value is not a valid email address: ... reserved name`

**Sintomo.** `/api/v1/auth/register` ritorna `422` con
`The part after the @-sign is a special-use or reserved name`.

**Causa.** Email validator rifiuta i TLD riservati IETF
([RFC 6761](https://datatracker.ietf.org/doc/html/rfc6761)):
`.local`, `.test`, `.localhost`, `.invalid`, `.example`, `.onion`.

**Fix.** Usa `@example.com`, un dominio reale che possiedi, o un TLD
interno aziendale (es. `@home.lan` se la tua LAN usa `.lan`).

## Container `unhealthy` con healthcheck timeout

**Sintomo.** `docker compose ps` mostra `(unhealthy)` per `jarvis-server`.

**Diagnosi rapida.**

```bash
# Cosa risponde il healthcheck?
docker compose exec server python -c \
  "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8080/health',timeout=3).read())"
```

Se la risposta è OK ma lo status è ancora `unhealthy`, il server è
appena partito: il healthcheck ha `start_period=15s` (default
Compose) e ricontrolla ogni 30 s. Aspetta 30-60 s.

Se invece la risposta non c'è, controlla i log:

```bash
docker compose logs server --tail=50
```

Cerca uno fra:

- `Application startup failed.` → leggi le righe sopra: tipicamente
  alembic in errore, env mancante, DB non raggiungibile.
- `Address already in use` → port collision.
- `Connection refused` verso postgres → il container `postgres` non è
  ancora `healthy`. Il `depends_on.condition: service_healthy` dovrebbe
  evitarlo; se vedi questo, significa che hai modificato `depends_on`.

## Il container si riavvia in loop

**Sintomo.** `docker compose ps` mostra `Restarting (1)` ciclicamente.

**Diagnosi.** Spesso è una env-var mancante post-update:

```bash
diff <(grep '^[A-Z]' .env) <(grep '^[A-Z]' .env.example) | head -20
```

Aggiungi le chiavi mancanti, poi:

```bash
docker compose up -d --force-recreate server
```

## `permission denied` su `/var/run/docker.sock`

**Sintomo.** Da utente non-root: `permission denied while trying to
connect to the Docker daemon`.

**Fix.**

```bash
sudo usermod -aG docker $USER
newgrp docker         # rilegge il gruppo nella shell corrente
docker info           # deve funzionare senza sudo
```

Se sei su un sistema condiviso e non puoi modificare i gruppi, prefissa
ogni comando con `sudo`. NB: la doc del progetto presuppone che tu
possa usare Docker senza sudo.

## Vedi anche

- [Build & Docker](build-docker.md)
- [Glossario error code](index.md#glossario-degli-error-code)
- [Identity Layer (architettura)](../security/identity-layer.md)
- [Aggiornare Open-Jarvis](../user-manual/updates.md)
