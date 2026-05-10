# Open-Jarvis · Web (Angular 18 PWA)

Client web ufficiale di Open-Jarvis. Stack:

- **Angular 18** standalone components, signals, control flow `@for/@if`
- **Tailwind CSS 3** con palette `jarvis-*`
- **Service worker** Angular per PWA (offline-shell + cache freshness API)
- **AGPL-3.0** come il resto del progetto

## Pagine

| Path | Descrizione |
|------|-------------|
| `/login` | Login + registrazione + scelta server URL |
| `/` | Chat con streaming SSE (token-by-token) |
| `/memory` | Aggiungi/cerca/elimina memorie semantiche |
| `/devices` | Genera QR di pairing per smartphone & co. |
| `/settings` | Server URL, backend LLM, modelli Ollama |

## Sviluppo

```bash
cd frontend/web
pnpm install
pnpm start            # → http://localhost:4200
```

Apri il browser, inserisci come *Server URL* l'URL del backend
(es. `http://localhost:8090` se hai sovrascritto la porta) e
registrati. Da quel momento il token è salvato in `localStorage` e
l'app intercetta automaticamente i 401 con refresh-token rotation.

## Build production

```bash
pnpm build            # → dist/open-jarvis-web/browser
```

Servi la cartella con qualunque static server. Per il deploy con Caddy:

```caddy
jarvis.example.com {
  encode gzip zstd
  root * /srv/open-jarvis-web/browser
  try_files {path} /index.html
  file_server
  reverse_proxy /api/* server:8080
  reverse_proxy /docs* server:8080
}
```

## Configurazione runtime

L'URL del server è risolto in quest'ordine:

1. `window.__OJ_API_BASE_URL__` (iniettato da Tauri / Capacitor / `index.html`)
2. `localStorage('oj.api_base_url')` (impostato dalla pagina di Login)
3. stesso origin (default per il deploy reverse-proxy)

## LLM backend selector

`/settings` mostra:

- **Backend disponibili** dal server (Echo, Ollama, OpenAI, Anthropic se
  configurati lato server con le API keys).
- **Modelli Ollama** scaricati localmente, recuperati via
  `/api/v1/llm/ollama/models` (proxy del daemon).
- Selezione del backend preferito → salvato in `localStorage` come
  `oj.preferred_backend` (TODO: passare il valore al chat turn).

## Test

```bash
pnpm test             # Karma + Jasmine
```
