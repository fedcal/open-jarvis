---
title: "Development mode · Open-Jarvis"
description: "Full local development guide for Open-Jarvis: FastAPI server with hot-reload, tests, lint, Alembic migrations, Angular frontend, Ionic mobile, Tauri desktop, debug, IDE setup."
keywords: "open-jarvis development, hot-reload, fastapi, uv, pytest, ruff, alembic, angular, ionic, tauri, vscode"
---

# Development mode

Open-Jarvis is built to be **easy to develop locally**: a server with
hot-reload, a hermetic test suite, integrated lint and typecheck, web
frontend with HMR. No cloud, no mandatory API keys — the default
`EchoAdapter` lets you work offline.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | server, tests, migrations |
| [uv](https://github.com/astral-sh/uv) | 0.5+ | dependency + venv mgmt |
| Docker | 24+ | local Postgres, Redis, Qdrant |
| Docker Compose plugin | v2 | stack orchestration |
| Node.js | 20 LTS | Angular web + Ionic mobile |
| pnpm | 9+ | frontend package manager |
| Rust toolchain | stable | Tauri desktop (only if you work on it) |
| make | — | command shortcuts |

## Repo layout

```
open-jarvis/
├── server/                # FastAPI core (you'll touch this)
│   ├── jarvis_server/
│   │   ├── api/           # routes, deps, app factory
│   │   ├── identity/      # auth, JWT, MFA, pairing
│   │   ├── memory/        # embeddings, vector store, service
│   │   ├── llm/           # adapters + router
│   │   ├── orchestration/ # state graph + tools
│   │   ├── domain/        # shared DTOs
│   │   ├── db/            # SQLAlchemy base
│   │   └── config/        # Pydantic settings
│   ├── migrations/        # Alembic
│   └── tests/             # unit + integration
├── frontend/web/          # Angular 18 PWA
├── agents/desktop/        # Tauri 2 shell
├── agents/mobile/         # Ionic + Capacitor
├── docker-compose.yml
└── Makefile
```

## One-shot setup

```bash
git clone https://github.com/fedcal/open-jarvis.git
cd open-jarvis
make up          # Postgres + Redis + Qdrant
make deps        # Python deps in server/.venv
make check       # lint + typecheck + test (must pass)
```

## Server with hot-reload

```bash
make server-dev
```

Equivalent to:

```bash
cd server && uv run uvicorn jarvis_server.api.main:app \
    --reload --host 0.0.0.0 --port 8080 --env-file ../.env
```

Open <http://localhost:8080/docs> for Swagger UI. Edit a Python file:
uvicorn reloads in <1 s.

!!! info "Why `--env-file ../.env`"
    Pydantic-settings looks for `.env` in the **process cwd**. Since
    `make server-dev` does `cd server`, without `--env-file` the
    repo-root `.env` is invisible. uvicorn loads it into `os.environ`
    before app boot, so `JARVIS_*` arrives correctly.

### Override server deps

By default `make server-dev` uses **SQLite** (`./jarvis-dev.db`),
in-memory vector store, `EchoAdapter`. To force Postgres + Qdrant +
Ollama edit `.env`:

```bash
JARVIS_DATABASE_URL=postgresql+psycopg://jarvis:jarvis@localhost:5432/jarvis
JARVIS_REDIS_URL=redis://localhost:6379/0
```

!!! warning "If you've overridden ports"
    With `POSTGRES_HOST_PORT=15432`, the URL must use `:15432`,
    otherwise server-dev hits `:5432` and gets `connection refused`.

!!! warning "JWT keypair in dev: shared, single-worker"
    Without `JARVIS_JWT_*_KEY_PEM` the server generates an ephemeral
    ES256 keypair at boot. With `--workers >1` each worker rolls a
    different one, breaking JWT verification. The compose forces
    `--workers 1` for that reason.

## Tests

```bash
make server-test           # all tests + 80% coverage gate
make server-test-fast      # tests only
```

Filters:

```bash
cd server
uv run -m pytest tests/identity/ -v
uv run -m pytest -k "test_login" -v
uv run -m pytest -m integration
uv run -m pytest --lf
uv run -m pytest -x --pdb
```

## Lint, format, typecheck

```bash
make server-lint
make server-fmt          # auto-fix + format
make server-typecheck
```

Pre-commit:

```bash
pip install pre-commit && pre-commit install
```

## Database migrations (Alembic)

```bash
make server-migrate      # apply migrations to head
make server-migration NAME="add bio column to user"
cd server && uv run alembic downgrade -1
```

Always read the auto-generated file before applying — Alembic
auto-detect doesn't handle every case (renames, server-side defaults).

## Web frontend (Angular 18 PWA)

```bash
cd frontend/web
pnpm install
cp .env.local.example .env.local 2>/dev/null || true
pnpm start                              # → http://localhost:4200
```

Pages: `/`, `/login`, `/memory`, `/devices`, `/settings`. Login URL
field defaults to current origin; on dev typically point at
`http://localhost:8090` (or your override).

## Mobile (Ionic + Capacitor)

```bash
cd agents/mobile
pnpm install
pnpm start                              # → http://localhost:4300

pnpm sync && pnpm cap add ios && pnpm ios          # Xcode
pnpm sync && pnpm cap add android && pnpm android  # Android Studio
```

To test on a real phone over the **same Wi-Fi** as the PC:

1. Use Capacitor Live Reload (`pnpm cap run ios -l --external`)
2. Set `EXPO_PUBLIC_API_URL` to `http://192.168.X.Y:8090`

See [Local install](../user-manual/install/local-lan.md).

## Desktop (Tauri 2)

```bash
cd agents/desktop
pnpm install
pnpm dev               # native window with HMR
```

Needs Rust toolchain:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup default stable
```

## "Full" dev mode in two terminals

```bash
# Terminal 1 — data + server
make up
make server-dev

# Terminal 2 — frontend
cd frontend/web && pnpm dev
```

Open:

- <http://localhost:3000> — frontend (or 4200)
- <http://localhost:8080/docs> — API Swagger
- <http://localhost:6333/dashboard> — Qdrant
- <http://localhost:8000/en/> — docs (`make docs-serve`)

## Env vars in dev

The server reads `.env` (gitignored). See `.env.example`:

```bash
JARVIS_ENVIRONMENT=development
JARVIS_LOG_LEVEL=debug
JARVIS_DATABASE_URL=sqlite+aiosqlite:///./jarvis-dev.db
JARVIS_JWT_PRIVATE_KEY_PEM=
JARVIS_JWT_PUBLIC_KEY_PEM=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

!!! warning "Everything starts with `JARVIS_`"
    Pydantic Settings has `env_prefix="JARVIS_"`. So `DATABASE_URL`
    is **ignored**: the right name is `JARVIS_DATABASE_URL`.

## Debugging

### VS Code

`.vscode/launch.json`:

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
    }
  ]
}
```

Recommended extensions: `ms-python.python`, `ms-python.vscode-pylance`,
`charliermarsh.ruff`, `tamasfe.even-better-toml`, `Angular.ng-template`.

### PyCharm

Mark `server/` as **Sources Root**. Set interpreter to
`server/.venv/bin/python`.

## Code conventions

- **Format**: `ruff format` (PEP-8, line length 100).
- **Naming**: `snake_case` files/vars/funcs, `PascalCase` classes,
  `UPPER_SNAKE` constants.
- **Type hints mandatory** everywhere new.
- **Frozen dataclass / Pydantic frozen** for DTOs.
- **Async-first**: every route, service, query is `async`.
- **Errors**: domain-flavoured names (`EmailAlreadyRegistered`) with
  `# noqa: N818`.
- **Test isolation**: each test gets a fresh in-memory SQLite engine.

## Branching and commits

- Base branch: `develop`. Open `feat/<scope>` or `fix/<scope>`.
- Commits: **Conventional Commits in English**:
  ```
  feat(memory): support Qdrant payload filters
  fix(auth): refresh token rejected on clock skew
  ```
- PR target: `develop`. Releases promote `develop` → `staging` → `main`.

## Working on multiple branches in parallel

```bash
git worktree add ../open-jarvis-feat-x feat/x
cd ../open-jarvis-feat-x && make deps && make server-dev
```

## Local CI

```bash
make ci   # lint + typecheck + test, mirrors GitHub
```

## See also

- [Quality standards](quality-standards.md)
- [Code review](code-review.md)
- [Branching strategy](branching-strategy.md)
- [Release cycle](release-cycle.md)
- [Identity Layer](https://fedcal.github.io/open-jarvis/security/identity-layer/)
- [Common problems](../troubleshooting/index.md)
