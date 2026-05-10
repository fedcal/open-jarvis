---
title: "Modalità sviluppo · Open-Jarvis"
description: "Guida completa allo sviluppo locale di Open-Jarvis: server FastAPI con hot-reload, test, lint, migrazioni Alembic, frontend Next.js, mobile Expo, desktop Tauri, debug, IDE setup."
keywords: "open-jarvis sviluppo, development mode, hot-reload, fastapi, uv, pytest, ruff, alembic, expo, tauri, vscode"
---

# Modalità sviluppo

Open-Jarvis è progettato per essere **sviluppato comodamente in
locale**: un server con hot-reload, una suite di test hermetica, lint
e typecheck integrati, frontend con HMR. Niente cloud, niente API
keys obbligatorie — il default `EchoAdapter` permette di lavorare
offline.

## Prerequisiti

| Tool | Versione | Scopo |
|------|----------|-------|
| Python | 3.12+ | server, test, migrazioni |
| [uv](https://github.com/astral-sh/uv) | 0.5+ | gestione dipendenze e virtualenv |
| Docker | 24+ | Postgres, Redis, Qdrant locali |
| Docker Compose plugin | v2 | orchestrazione stack |
| Node.js | 20 LTS | frontend Next.js + agent React Native |
| pnpm | 9+ | package manager frontend |
| Rust toolchain | stable | compilazione agent desktop Tauri (solo se ci lavori) |
| make | — | shortcut comandi |

Verifica:

```bash
python --version    # 3.12+
uv --version
docker --version
node --version
make --version
```

## Layout del repository

```
open-jarvis/
├── server/             # FastAPI core — il modulo che probabilmente toccherai
│   ├── jarvis_server/
│   │   ├── api/        # routes, deps, app factory
│   │   ├── identity/   # auth, JWT, MFA, pairing
│   │   ├── memory/     # embeddings, vector store, service
│   │   ├── llm/        # adapter + router
│   │   ├── orchestration/  # state graph + tools
│   │   ├── domain/     # DTO condivisi
│   │   ├── db/         # SQLAlchemy base + session
│   │   └── config/     # settings Pydantic
│   ├── migrations/     # Alembic
│   ├── tests/          # unit + integration
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/           # Next.js 15 (PWA web)
├── agents/             # client desktop, mobile, watch, glasses, …
├── plugins/            # plugin system
├── infra/              # k8s, terraform, monitoring
├── docs/               # MkDocs Material (IT + EN)
├── scripts/            # utility CLI
├── docker-compose.yml  # stack locale
└── Makefile            # shortcut dev
```

## Setup iniziale (one-shot)

```bash
git clone https://github.com/fedcal/open-jarvis.git
cd open-jarvis

# Stack di servizi (Postgres + Redis + Qdrant)
make up

# Dipendenze Python del server (in un virtualenv .venv gestito da uv)
make deps

# Verifica: tutto verde
make check
```

`make check` esegue **lint + typecheck + test**: deve passare al primo
colpo. Se non passa, è un bug del repository — apri un'issue.

## Avviare il server in dev (hot-reload)

```bash
make server-dev
```

equivale a:

```bash
cd server && uv run uvicorn jarvis_server.api.main:app \
  --reload --host 0.0.0.0 --port 8080
```

Apri <http://localhost:8080/docs> per la dashboard OpenAPI Swagger.
Modifica un file Python: uvicorn rileva la change e ricarica il
processo in <1 s.

!!! tip "Quando NON usare hot-reload"
    Test, profiling, debug step-by-step. Per quei casi avvia il server
    senza `--reload` (es. via VS Code launch config) così i breakpoint
    sono stabili.

### Override delle dipendenze del server

Per default `make server-dev` usa la **stessa configurazione del
compose**: SQLite locale `./jarvis-dev.db`, in-memory vector store,
`EchoAdapter` come unico backend LLM. Se vuoi forzare Postgres
+ Qdrant + Ollama:

```bash
export JARVIS_DATABASE_URL="postgresql+asyncpg://jarvis:jarvis@localhost:5432/jarvis"
export JARVIS_REDIS_URL="redis://localhost:6379/0"
make server-dev
```

In alternativa, lascia che `docker compose up server` ricompili
l'immagine; il volume non è montato in dev mode quindi serve un
`docker compose build server` ad ogni modifica — meglio il flow
host-side con `make server-dev`.

### Profili Docker Compose

```bash
docker compose --profile local-llm up -d   # avvia anche Ollama
docker compose up postgres redis qdrant    # solo data store, niente server
```

## Test

```bash
make server-test           # tutti i test + coverage 80% gate
make server-test-fast      # solo test, senza coverage
```

Filtri utili:

```bash
cd server
uv run -m pytest tests/identity/ -v        # solo identity
uv run -m pytest -k "test_login" -v        # match per nome
uv run -m pytest -m integration            # solo integration tests
uv run -m pytest --lf                      # rerun degli ultimi failed
uv run -m pytest -x --pdb                  # stop on first fail + pdb
```

### Coverage HTML

```bash
cd server && uv run -m pytest --cov-report=html
xdg-open htmlcov/index.html      # Linux
open    htmlcov/index.html       # macOS
start   htmlcov/index.html       # Windows
```

### Test marker custom

| Marker | Scopo |
|--------|-------|
| `@pytest.mark.integration` | richiede DB / HTTP / async session |
| `@pytest.mark.unit` | pura logica, no I/O |

Default: tutti vengono eseguiti.

## Lint, format, typecheck

```bash
make server-lint        # ruff check (≈ flake8 + isort + bugbear + …)
make server-fmt         # ruff fix + ruff format (auto)
make server-typecheck   # mypy strict
```

Pre-commit (opzionale ma consigliato):

```bash
pip install pre-commit
pre-commit install
# Da qui ogni `git commit` lancia ruff + mypy + secret scan
```

## Migrazioni database (Alembic)

### Applicare migrazioni

```bash
make server-migrate
# equivale a: cd server && uv run alembic upgrade head
```

Esegui sempre dopo un `git pull`: il branch potrebbe avere una
nuova migrazione.

### Creare una nuova migrazione

1. Modifica i modelli ORM in `server/jarvis_server/<package>/orm.py`.
2. Auto-genera la migrazione:

   ```bash
   make server-migration NAME="add bio column to user"
   # → server/migrations/versions/2026_05_10_0004_add_bio_column_to_user.py
   ```

3. **Apri il file generato** e leggilo: Alembic auto-detect non
   gestisce sempre i casi complessi (rinomine, costanti server-side).
   Sistemalo a mano se serve.
4. Applica e testa:

   ```bash
   make server-migrate
   make server-test
   ```

5. Committa **insieme**: la modifica al modello e la migrazione
   devono essere nello stesso commit (lo richiede `tdd-guide`).

### Rollback

```bash
cd server && uv run alembic downgrade -1
```

⚠️ Non funziona se la migrazione è distruttiva (drop column). Per
quelli, ripristina da backup; vedi
[Aggiornare Open-Jarvis](../user-manual/updates.md#rollback-server).

### Ispezionare lo SQL prima di applicare

```bash
cd server && uv run alembic upgrade head --sql > preview.sql
```

Utile per pull request che toccano lo schema in produzione.

## Frontend (Next.js 15) — modalità sviluppo

```bash
cd frontend
pnpm install
cp .env.local.example .env.local      # NEXT_PUBLIC_API_URL=http://localhost:8080
pnpm dev                               # HMR su :3000
```

Pagine principali:

- `/` — homepage + chat
- `/devices` — gestione device + pairing
- `/memory` — memoria semantica (search, browse, forget)

API client autogenerato da OpenAPI:

```bash
cd frontend && pnpm gen:api
# legge http://localhost:8080/openapi.json e rigenera src/lib/api/
```

## Mobile (Expo) — modalità sviluppo

```bash
cd agents/mobile
pnpm install
pnpm start                # apre Metro bundler
# poi i / a / w per iOS / Android / Web
```

Per testare su uno smartphone fisico sulla **stessa Wi-Fi del PC**:

1. Installa l'app **Expo Go** dallo store.
2. Scansiona il QR mostrato da Metro.
3. Imposta `EXPO_PUBLIC_API_URL` nel `.env` su
   `http://192.168.X.Y:8080` (l'IP del PC, **non** `localhost`).

Vedi anche [Installazione locale (PC + Wi-Fi)](../user-manual/install/local-lan.md)
per il setup di rete.

## Desktop agent (Tauri) — modalità sviluppo

```bash
cd agents/desktop
pnpm install
pnpm tauri dev            # apre la finestra con hot-reload sul webview
```

Richiede la toolchain Rust:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup default stable
```

## Modalità sviluppo "completa": un comando

Vuoi tutto a manetta in un unico flusso? Usa due terminali:

```bash
# Terminale 1 — stack di dati + server
make up
make server-dev

# Terminale 2 — frontend
cd frontend && pnpm dev
```

Apri:

- <http://localhost:3000> — frontend
- <http://localhost:8080/docs> — API Swagger
- <http://localhost:6333/dashboard> — Qdrant
- <http://localhost:8000/it/> — docs (se hai fatto `make docs-serve`)

## Variabili d'ambiente in dev

Il server legge `.env` (gitignored). Copia `.env.example` e modifica:

```bash
JARVIS_ENVIRONMENT=development
JARVIS_LOG_LEVEL=debug                  # log verbosi
JARVIS_DATABASE_URL=sqlite+aiosqlite:///./jarvis-dev.db
# o per usare Postgres del compose:
# JARVIS_DATABASE_URL=postgresql+asyncpg://jarvis:jarvis@localhost:5432/jarvis

JARVIS_JWT_PRIVATE_KEY_PEM=             # vuoto → ephemeral key auto-generata
JARVIS_JWT_PUBLIC_KEY_PEM=

# Provider opzionali (lascia vuoto per usare solo EchoAdapter)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

In produzione `assert_production_safe()` rifiuta i default; in dev e
test queste verifiche sono disabilitate.

## Logging strutturato in dev

```python
import structlog
log = structlog.get_logger(__name__)
log.info("user_login", user_id=user.id, ip=request.client.host)
```

Output dev (pretty):

```
2026-05-10 14:23:01 [info     ] user_login user_id=… ip=192.168.1.42
```

Output prod (JSON):

```json
{"event":"user_login","user_id":"…","ip":"192.168.1.42",
 "timestamp":"2026-05-10T14:23:01Z","level":"info"}
```

## Debugging

### VS Code

`.vscode/launch.json` (presente nel repo):

```json
{
  "configurations": [
    {
      "name": "Debug FastAPI",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": ["jarvis_server.api.main:app", "--host", "0.0.0.0", "--port", "8080"],
      "cwd": "${workspaceFolder}/server",
      "envFile": "${workspaceFolder}/.env"
    },
    {
      "name": "Debug pytest (current file)",
      "type": "debugpy",
      "request": "launch",
      "module": "pytest",
      "args": ["${file}", "-v"],
      "cwd": "${workspaceFolder}/server"
    }
  ]
}
```

Estensioni consigliate (`.vscode/extensions.json`):

- `ms-python.python` + `ms-python.vscode-pylance`
- `charliermarsh.ruff`
- `tamasfe.even-better-toml`
- `redhat.vscode-yaml`

### PyCharm

Marca `server/` come **Sources Root** (right-click → *Mark Directory
as*). Imposta l'interprete su `server/.venv/bin/python`. Le run
configuration sono auto-rilevate da `pyproject.toml`.

### Debug ad-hoc

```python
from rich import print as rprint   # già fra le deps di structlog
rprint(state)                       # pretty stampa Pydantic / dataclass
breakpoint()                        # set di un trap nel codice
```

## Convenzioni di codice

- **Formattazione**: `ruff format` (PEP-8, line length 100).
- **Naming**: `snake_case` per file/var/funzioni, `PascalCase` per
  classi, `UPPER_SNAKE` per costanti.
- **Type hints obbligatori** per tutto il codice nuovo.
- **Frozen dataclass / Pydantic frozen** per i DTO.
- **Async-first**: tutte le route, i service, le query DB usano
  `async`/`await`.
- **Errori**: classi domain-specific (es. `EmailAlreadyRegistered`)
  con `# noqa: N818` se non terminano con `Error`.
- **Test isolation**: ogni test riceve un engine SQLite in-memory,
  niente stato condiviso.

Vedi [Quality standards](quality-standards.md) per il dettaglio.

## Branching e commit

- Branch base: `develop`. Da qui parti con un nuovo
  `feat/<scope>` o `fix/<scope>`.
- Commit message: **Conventional Commits in inglese**.

  ```
  feat(memory): support Qdrant payload filters
  fix(auth): refresh token rejected on clock skew
  docs(troubleshooting): document docker network errors
  ```

- PR target: `develop`. Quando develop accumula abbastanza feature,
  un release manager fa il merge in `staging` e poi `main`.
- Vedi [Branching strategy](branching-strategy.md) e
  [Release cycle](release-cycle.md).

## Lavorare in parallelo su più branch

```bash
git worktree add ../open-jarvis-feat-x feat/x
cd ../open-jarvis-feat-x
make deps && make server-dev      # totalmente isolato dall'altro worktree
```

Comodo quando devi tenere aperta una review mentre sviluppi
qualcos'altro.

## CI locale (mirror del workflow GitHub)

```bash
make ci   # lint + typecheck + test, esattamente quello che gira su GitHub
```

Se `make ci` passa in locale, la PR passa la CI. Se la CI rompe ma
`make ci` no, è un bug d'ambiente: apri un'issue.

## Risorse aggiuntive

- [Quality standards](quality-standards.md)
- [Code review](code-review.md)
- [Branching strategy](branching-strategy.md)
- [Release cycle](release-cycle.md)
- [Governance](governance.md)
- [Architettura del runtime core](../architecture/core-runtime.md)
- [Identity Layer](../security/identity-layer.md)
- [Problemi comuni](../troubleshooting/index.md)

## Hai bloccato qualcuno?

Apri una **draft PR** ed etichettala `help-wanted`: la community è
attiva. In alternativa apri una **discussion** su GitHub —
rispondiamo in 24-48 h.
