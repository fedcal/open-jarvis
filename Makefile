# ============================================================
# Jarvis — developer convenience targets
# ============================================================

.PHONY: help up down logs ps clean docs-serve docs-build docs-install

help:  ## Mostra questo aiuto · Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

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

# -------- Docs --------

docs-install:  ## Installa le dipendenze MkDocs · Install MkDocs deps
	pip install -r docs/requirements.txt

docs-serve:  ## Preview docs in locale su :8000 · Local docs preview on :8000
	mkdocs serve

docs-build:  ## Build statico del sito docs · Build static docs site
	mkdocs build --clean --strict

docs-deploy:  ## Deploy docs su GitHub Pages (manuale) · Manual GH Pages deploy
	mkdocs gh-deploy --force
