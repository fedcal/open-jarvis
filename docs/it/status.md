---
title: "Stato dell'implementazione · Open-Jarvis"
description: "Matrice live dello stato di implementazione delle funzionalità di Open-Jarvis. Tracciato a ogni commit per garantire trasparenza nei confronti della community open source."
keywords: "open-jarvis stato, implementazione, roadmap live, feature tracker, open source progress"
---

# Stato dell'implementazione

Questa pagina è il **single source of truth** dello stato di implementazione di Open-Jarvis.
Viene aggiornata a **ogni commit significativo** e indica per ciascuna feature il suo stato attuale, il commit di riferimento e i test associati.

!!! tip "Legenda"
    - 🟢 **Done** — implementato, testato, in uso
    - 🟡 **In progress** — in lavorazione attiva (branch `feat/*`)
    - 🔵 **Next** — pianificato per la prossima iterazione
    - ⚪ **Planned** — definito ma non ancora avviato
    - 🟣 **Vision** — long-term, dipende dalla community

## Fase 0 · Foundation 🌱

| Feature | Stato | Commit | Note |
|---|---|---|---|
| Repository scaffold (server, agents, frontend, plugins, infra) | 🟢 Done | [`578c012`](https://github.com/fedcal/open-jarvis/commit/578c012) | 10 agenti scaffolded |
| `.gitignore` multi-stack con protezione `.env` | 🟢 Done | [`578c012`](https://github.com/fedcal/open-jarvis/commit/578c012) | |
| Documentazione MkDocs Material bilingue (IT + EN) | 🟢 Done | [`578c012`](https://github.com/fedcal/open-jarvis/commit/578c012) | 52 pagine |
| Manuale utente (install · config · usage · troubleshooting · FAQ) | 🟢 Done | [`578c012`](https://github.com/fedcal/open-jarvis/commit/578c012) | Living doc bilingue |
| GitHub Actions deploy docs su GH Pages | 🟢 Done | [`578c012`](https://github.com/fedcal/open-jarvis/commit/578c012) | Live su [fedcal.github.io/open-jarvis](https://fedcal.github.io/open-jarvis/) |
| MIT LICENSE + CONTRIBUTING + CODE_OF_CONDUCT + SECURITY | 🟢 Done | [`578c012`](https://github.com/fedcal/open-jarvis/commit/578c012) | |
| GitHub issue/PR templates | 🟢 Done | [`578c012`](https://github.com/fedcal/open-jarvis/commit/578c012) | |
| Mobile-first redesign + SEO (OG, Twitter, JSON-LD, robots) | 🟢 Done | [`9fedc70`](https://github.com/fedcal/open-jarvis/commit/9fedc70) | |
| Server Python scaffold (FastAPI + Pydantic Settings) | 🟢 Done | _phase 1.0_ | Health endpoint funzionante |
| Test suite base (pytest + coverage ≥ 80%) | 🟢 Done | _phase 1.0_ | |
| CI workflow (lint + typecheck + test + security scan) | 🟢 Done | _phase 1.0_ | |
| Server Dockerfile multi-stage | 🟢 Done | _phase 1.0_ | |
| Pre-commit hooks (ruff, mypy, gitleaks) | 🟢 Done | _phase 1.0_ | |

## Fase 1 · Core MVP 🏗️

| Feature | Stato | Test | Note |
|---|---|---|---|
| Health endpoint REST | 🟢 Done | unit + integration | `/health` con dipendenze |
| Configuration via Pydantic Settings | 🟢 Done | unit | env-based, type-safe |
| Logging strutturato (structlog) | 🔵 Next | – | JSON in prod, pretty in dev |
| Database schema (PostgreSQL) | ⚪ Planned | – | Alembic migrations |
| Identity layer (User · Device entities) | ⚪ Planned | – | |
| Device pairing (QR + token) | ⚪ Planned | – | |
| OAuth 2.0 / OIDC integration | ⚪ Planned | – | Authentik default |
| JWT auth + refresh token | ⚪ Planned | – | |
| Memory layer (mem0 wrapper) | ⚪ Planned | – | |
| Vector store integration (Qdrant) | ⚪ Planned | – | |
| LLM router (Ollama + Anthropic + OpenAI) | ⚪ Planned | – | |
| LangGraph orchestrator base | ⚪ Planned | – | |
| Chat REST + WebSocket endpoints | ⚪ Planned | – | |
| Desktop agent (Tauri) | ⚪ Planned | – | |
| Mobile agent (React Native) | ⚪ Planned | – | |
| Web frontend (Next.js / Angular) | ⚪ Planned | – | |
| E2E test cross-device | ⚪ Planned | – | |

## Fase 2 · Voice & Watch 🎙️

| Feature | Stato | Note |
|---|---|---|
| Wake-word "Hey Jarvis" (Porcupine) | ⚪ Planned | on-device |
| Speech-to-text (faster-whisper) | ⚪ Planned | locale |
| TTS (Piper) | ⚪ Planned | naturale |
| Watch agent (Wear OS) | ⚪ Planned | |
| Watch agent (WatchKit) | ⚪ Planned | |
| Watch agent (InfiniTime/PineTime) | ⚪ Planned | open hardware |
| Notifiche intelligenti context-aware | ⚪ Planned | |
| Routing dinamico per device | ⚪ Planned | |

## Fase 3 · Web & Knowledge 🌐

| Feature | Stato |
|---|---|
| Scraping agent (Crawl4AI) | ⚪ Planned |
| Scraping agent (Firecrawl self-hosted) | ⚪ Planned |
| Scraping agent (Jina Reader) | ⚪ Planned |
| Daily briefing generator | ⚪ Planned |
| RAG su documenti (LlamaIndex) | ⚪ Planned |
| Visual RAG su PDF (ColQwen2) | ⚪ Planned |
| Browser agent (Playwright) | ⚪ Planned |
| Sync Obsidian | ⚪ Planned |
| Sync Notion | ⚪ Planned |
| Sync Google Drive | ⚪ Planned |
| Embedding multilingue (BGE-M3) | ⚪ Planned |

## Fase 4 · Health 🏃

| Feature | Stato |
|---|---|
| Connettore Oura | ⚪ Planned |
| Connettore Whoop | ⚪ Planned |
| Connettore Polar | ⚪ Planned |
| Connettore Garmin | ⚪ Planned |
| Connettore Withings | ⚪ Planned |
| Connettore Fitbit/Google Health | ⚪ Planned |
| Connettore Dexcom CGM | ⚪ Planned |
| HAPI FHIR vault | ⚪ Planned |
| Open Wearables middleware | ⚪ Planned |
| Coaching engine | ⚪ Planned |
| Biometric alerting | ⚪ Planned |

## Fase 5 · Smart Home 🏠

| Feature | Stato |
|---|---|
| Home Assistant bridge | ⚪ Planned |
| Matter bridge (via HA) | ⚪ Planned |
| Frigate event ingestion | ⚪ Planned |
| ESPHome custom devices | ⚪ Planned |

## Fase 6 · Finance 💰

| Feature | Stato |
|---|---|
| TrueLayer (PSD2 EU) | ⚪ Planned |
| GoCardless Bank Data | ⚪ Planned |
| IBKR portfolio | ⚪ Planned |
| Alpaca portfolio | ⚪ Planned |
| Coinbase / Kraken / Binance read-only | ⚪ Planned |
| Zerion cross-chain | ⚪ Planned |
| Etherscan storico ETH | ⚪ Planned |
| Firefly III bridge | ⚪ Planned |
| Daily/weekly briefing finanziario | ⚪ Planned |
| Subscription tracker | ⚪ Planned |

## Fase 7 · AR & XR 👓

| Feature | Stato |
|---|---|
| Glasses agent Brilliant Frame | ⚪ Planned |
| Glasses agent MentraOS | ⚪ Planned |
| VR agent OpenXR/Monado | ⚪ Planned |
| Avatar 3D Jarvis | ⚪ Planned |
| Real-time translator overlay | 🟣 Vision |

## Fase 8 · Holographic & Maker 🎬

| Feature | Stato |
|---|---|
| Holo agent Looking Glass | ⚪ Planned |
| Holo agent Voxon | ⚪ Planned |
| Avatar olografico parlante | ⚪ Planned |
| Blender bpy automation | ⚪ Planned |
| Moonraker bridge | ⚪ Planned |
| OctoPrint bridge | ⚪ Planned |
| Bambu MQTT bridge | ⚪ Planned |
| TRELLIS-2 self-hosted (3D AI) | ⚪ Planned |
| Slicer automation | ⚪ Planned |

## Fase 9 · Maturity 🏆

| Feature | Stato |
|---|---|
| Plugin marketplace pubblico | 🟣 Vision |
| Multi-tenant managed hosting | 🟣 Vision |
| Localizzazione completa (ES/FR/DE/PT/JA) | 🟣 Vision |
| Audit di sicurezza terzo | 🟣 Vision |
| Release 1.0 stabile | 🟣 Vision |

## Metriche del progetto

| Metrica | Valore | Aggiornato |
|---|---|---|
| Test coverage server | _aggiornato a ogni CI run_ | _live_ |
| Documentazione | 52 pagine + status | live |
| Linguaggi supportati | IT, EN | – |
| Linee di codice | _aggiornato a ogni release_ | – |
| Contributori | [vedi GitHub](https://github.com/fedcal/open-jarvis/graphs/contributors) | live |

## Come contribuire

Vuoi accelerare una feature? Vedi [Contribuire](contributing/index.md). Le feature ⚪ **Planned** sono ottimi punti di partenza per nuovi contributori.
