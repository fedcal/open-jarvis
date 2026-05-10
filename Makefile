# ============================================================
# Jarvis — developer convenience targets
# ============================================================

.PHONY: help up down logs ps clean \
        docs-serve docs-build docs-install docs-deploy \
        deps server-dev server-test server-lint server-fmt server-typecheck \
        server-migrate server-migration db-shell redis-shell qdrant-shell \
        check ci

help:  ## Mostra questo aiuto · Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'

# -------- Stack --------

up:  ## Avvia lo stack locale (docker compose) · Start the local stack
	docker compose up -d
	@echo "Server:    http://localhost:8080"
	@echo "Frontend:  http://localhost:3000"
	@echo "Qdrant:    http://localhost:6333/dashboard"

down:  ## Ferma lo stack · Stop the stack
	docker compose down

logs:  ## Tail dei log · Tail logs
	docker compose logs -f --tail=100

ps:  ## Stato dei container · Container status
	docker compose ps

clean:  ## ⚠️  Reset totale (volumi inclusi) · Full reset (volumes included)
	docker compose down -v

# -------- Server (modalità sviluppo · development mode) --------

deps:  ## Installa dipendenze server (uv) · Install server dependencies
	cd server && uv sync --extra dev

server-dev:  ## Avvia FastAPI con hot-reload su :8080 · Run FastAPI with hot-reload
	@# uvicorn --env-file loads ../.env (repo root) into the process before
	@# the app boots, so pydantic-settings can read JARVIS_* even from server/
	cd server && uv run uvicorn jarvis_server.api.main:app \
	    --reload --host 0.0.0.0 --port 8080 --env-file ../.env

server-test:  ## Esegui la test suite con coverage · Run tests with coverage
	cd server && uv run -m pytest

server-test-fast:  ## Test suite senza coverage (più veloce) · Tests without coverage
	cd server && uv run -m pytest --no-cov

server-lint:  ## Ruff lint · Ruff lint
	cd server && uv run ruff check jarvis_server tests

server-fmt:  ## Auto-format + auto-fix · Auto-format + auto-fix
	cd server && uv run ruff check --fix jarvis_server tests
	cd server && uv run ruff format jarvis_server tests

server-typecheck:  ## mypy strict · mypy strict
	cd server && uv run mypy jarvis_server

# -------- Database (Alembic + shells) --------

server-migrate:  ## Applica migrazioni Alembic · Run Alembic migrations to head
	cd server && uv run alembic upgrade head

server-migration:  ## Genera nuova migrazione (NAME=...) · Create new migration
	@test -n "$(NAME)" || (echo "Usage: make server-migration NAME='add foo column'"; exit 1)
	cd server && uv run alembic revision --autogenerate -m "$(NAME)"

db-shell:  ## psql sul Postgres del compose · Postgres shell via compose
	docker compose exec postgres psql -U jarvis -d jarvis

redis-shell:  ## redis-cli sul Redis del compose · Redis CLI via compose
	docker compose exec redis redis-cli

qdrant-shell:  ## curl Qdrant collections · Qdrant collections via curl
	curl -s http://localhost:6333/collections | jq .

# -------- CI bundle --------

check:  ## Lint + typecheck + test · Lint + typecheck + tests (mirrors CI)
	$(MAKE) server-lint
	$(MAKE) server-typecheck
	$(MAKE) server-test

ci: check  ## Alias di `check` · Alias for `check`

# -------- Docs --------

docs-install:  ## Installa le dipendenze MkDocs · Install MkDocs deps
	pip install -r docs/requirements.txt

docs-serve:  ## Preview docs in locale su :8000 · Local docs preview on :8000
	mkdocs serve

docs-build:  ## Build statico del sito docs · Build static docs site
	mkdocs build --clean --strict

docs-deploy:  ## Deploy docs su GitHub Pages (manuale) · Manual GH Pages deploy
	mkdocs gh-deploy --force
