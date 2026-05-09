# Configurazione

Questa pagina descrive come configurare le **integrazioni opzionali** di Jarvis dopo l'installazione di base.

## Struttura della configurazione

| File | Scopo | Tracciato in git? |
|---|---|---|
| `.env` | Token e segreti reali | ❌ MAI |
| `.env.example` | Template di esempio | ✅ Sì |
| `config/jarvis.yaml` | Configurazione applicativa non-segreta | ✅ Sì |
| `data/` | Database, vector store, conversazioni | ❌ MAI |

## 1. Provider LLM

Puoi configurare uno o più provider. Jarvis sceglie il modello più adatto per ogni task in base a:

- complessità del task
- privacy policy dell'utente
- disponibilità del device

### Anthropic (Claude)

```env
ANTHROPIC_API_KEY=sk-ant-...
JARVIS_MODEL_LARGE=anthropic/claude-sonnet-4-6
```

### OpenAI

```env
OPENAI_API_KEY=sk-...
JARVIS_MODEL_LARGE=openai/gpt-4o
```

### Ollama (locale, 100% privato)

```env
OLLAMA_BASE_URL=http://ollama:11434
JARVIS_MODEL_SMALL=ollama/llama3.2:1b
JARVIS_MODEL_MEDIUM=ollama/llama3.1:8b
JARVIS_MODEL_LARGE=ollama/qwen2.5:14b
```

Scarica i modelli locali:

```bash
docker compose exec ollama ollama pull llama3.1:8b
docker compose exec ollama ollama pull qwen2.5:14b
docker compose exec ollama ollama pull bge-m3   # embedding multilingue IT+EN
```

### Groq (low-latency cloud)

```env
GROQ_API_KEY=gsk_...
JARVIS_MODEL_FAST=groq/llama-3.3-70b-versatile
```

## 2. Identità e OAuth

Per autenticazione SSO multi-device si raccomanda **Authentik** (Docker-friendly, FIDO2/passkey, OIDC).

```yaml
# config/jarvis.yaml
auth:
  provider: authentik
  oidc_issuer: https://auth.tuodominio.com/application/o/jarvis/
  client_id: jarvis-client
```

Il `client_secret` corrispondente va in `.env`:

```env
OIDC_CLIENT_SECRET=...
```

## 3. Pairing dei dispositivi

### Dispositivo desktop

```bash
docker compose exec server jarvis enroll --type=desktop --label="Laptop ufficio"
```

Scansiona il QR code con l'app mobile **oppure** copia il token mostrato a schermo.

### Dispositivo mobile (iOS/Android)

1. Installa l'app **Jarvis** dallo store
2. Apri **Impostazioni → Pair new device**
3. Inquadra il QR code generato dal server

### Dispositivo watch (Wear OS)

Pairing automatico tramite l'app mobile companion.

### Wearable medicali (Oura, Whoop, …)

Vedi [Integrazione salute](../features/health.md).

## 4. Memoria e RAG

Default: **mem0 + Qdrant**.

```env
MEMORY_BACKEND=mem0
QDRANT_URL=http://qdrant:6333
EMBEDDING_MODEL=ollama/bge-m3   # multilingue IT+EN
```

Per indicizzare documenti personali (Obsidian, Notion, Drive):

```bash
docker compose exec server jarvis rag connect obsidian \
  --vault-path /vaults/personal
```

Vedi [Documenti & RAG](../features/rag.md) per il dettaglio completo.

## 5. Funzionalità opzionali

| Feature | Variabili `.env` | Documentazione |
|---|---|---|
| Salute | `OURA_*`, `WHOOP_*`, `POLAR_*`, `GARMIN_*`, `FHIR_SERVER_URL` | [Salute](../features/health.md) |
| Finanza | `TRUELAYER_*`, `GOCARDLESS_*`, `IBKR_*`, `COINBASE_*`, `ETHERSCAN_API_KEY` | [Finanza](../features/finance.md) |
| News | `MINIFLUX_URL`, `CURRENTS_API_KEY`, `BLUESKY_HANDLE` | [News](../features/news.md) |
| AR / VR | `FRAME_DEVICE_ID`, `MENTRAOS_API_KEY` | [Dispositivi](../devices/index.md) |
| Olografi | `LOOKING_GLASS_BRIDGE_URL`, `VOXON_DEVICE_ID` | [Ologrammi](../integrations/holographic.md) |
| Stampa 3D | `MOONRAKER_URL`, `OCTOPRINT_*`, `BAMBU_*` | [Maker](../features/maker.md) |
| Smart home | `HOME_ASSISTANT_URL`, `HOME_ASSISTANT_TOKEN` | [Altri sistemi](../integrations/other-systems.md) |

## 6. Hardening di sicurezza

✅ Reverse-proxy con TLS (Caddy / Traefik / Nginx)
✅ Firewall in entrata che esponga solo `:443`
✅ Cifratura at-rest del volume `data/` (LUKS / FileVault)
✅ Rotazione mensile di `SERVER_SECRET_KEY` e `JWT_SECRET`
✅ Backup giornaliero di `data/` su storage offline
✅ Aggiornamenti settimanali (`docker compose pull && docker compose up -d`)

> Vai a → [Utilizzo quotidiano](usage.md)
