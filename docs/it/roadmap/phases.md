# Fasi di sviluppo

La roadmap di **Jarvis** è organizzata in fasi incrementali, ciascuna con un MVP usabile e contributi misurabili.

!!! note "Date indicative"
    Le date sono volutamente generiche perché il progetto è community-driven. La velocità dipende dai contributori. Vedi [Contribuire](../contributing/index.md) se vuoi accelerare una fase.

## Fase 0 — Foundation 🌱

**Obiettivo:** scheletro del progetto, identità open source, contributing path.

- ✅ Manifesto e visione bilingue (`Jarvis.md`)
- ✅ Documentazione MkDocs Material multilingue (IT + EN)
- ✅ Struttura repository (`server/`, `agents/`, `frontend/`, `plugins/`, `infra/`)
- ✅ CONTRIBUTING, CODE_OF_CONDUCT, LICENSE, SECURITY
- ✅ CI per il deploy automatico della documentazione su GitHub Pages
- ✅ `.env.example` template

## Fase 1 — Core MVP 🏗️

**Obiettivo:** una conversazione persistente cross-device su due dispositivi.

- 🎯 Identity layer (OAuth + device pairing)
- 🎯 Memory layer (mem0 + Qdrant)
- 🎯 LangGraph orchestrator base
- 🎯 Desktop agent (Linux/macOS/Windows)
- 🎯 Mobile agent prototipo (Android prima, iOS dopo)
- 🎯 Frontend chat web responsive
- 🎯 Integration test e2e: messaggio iniziato su desktop continuato su mobile

## Fase 2 — Voice & Watch 🎙️

**Obiettivo:** input vocale cross-device + integrazione smartwatch.

- 🎯 Voice agent: Porcupine + faster-whisper + Piper
- 🎯 Wake-word custom "Hey Jarvis"
- 🎯 Watch agent: Wear OS + WatchKit + InfiniTime
- 🎯 Notifiche intelligenti basate su contesto (calendar, location)
- 🎯 Routing dinamico in base al device disponibile

## Fase 3 — Web & Knowledge 🌐

**Obiettivo:** ricerca online, knowledge base personale, RAG.

- 🎯 Scraping agent (Crawl4AI + Firecrawl + Jina Reader)
- 🎯 Daily briefing generato (news + email + agenda)
- 🎯 RAG su documenti personali (LlamaIndex + ColPali)
- 🎯 Browser agent (Playwright headless)
- 🎯 Sync con Obsidian, Notion, Google Drive

## Fase 4 — Health 🏃

**Obiettivo:** federazione di wearable medicali, insight longitudinali.

- 🎯 Medical agent: Oura, Whoop, Polar, Garmin, Withings
- 🎯 Health vault FHIR-compatibile (HAPI FHIR server)
- 🎯 Open Wearables come middleware unificato
- 🎯 Alerting su soglie biometriche
- 🎯 Coaching automatico (sleep, training, recovery)

## Fase 5 — Smart home 🏠

**Obiettivo:** integrazione domotica completa.

- 🎯 Bridge Home Assistant
- 🎯 Matter / Thread / Zigbee tramite HA
- 🎯 Routine automatiche basate su presenza, ora, biometrica
- 🎯 Plugin marketplace primi rilasci

## Fase 6 — Finance 💰

**Obiettivo:** gestione patrimonio personale.

- 🎯 Aggregazione conti via PSD2 (GoCardless Bank Account Data, Tink)
- 🎯 Wallet crypto (Coinbase, Etherscan, on-chain)
- 🎯 Integrazione broker (Interactive Brokers, Alpaca)
- 🎯 Daily/weekly briefing finanziario
- 🎯 Alert su variazioni significative

## Fase 7 — AR & XR 👓

**Obiettivo:** overlay AR e immersione VR.

- 🎯 Glasses agent: Brilliant Frame + MentraOS
- 🎯 VR agent: OpenXR su Quest, Index, Pico
- 🎯 UI flottanti contestuali (navigazione, info real-time)
- 🎯 Avatar Jarvis 3D in VR

## Fase 8 — Holographic & Maker 🎬

**Obiettivo:** presenza olografica + integrazione Blender / stampa 3D.

- 🎯 Holo agent: Looking Glass + Voxon
- 🎯 Avatar olografico parlante con lip-sync
- 🎯 Blender Python automation
- 🎯 OctoPrint / Klipper / Moonraker integration
- 🎯 Generazione 3D AI on-demand (TripoSR)

## Fase 9 — Maturity 🏆

**Obiettivo:** stabilità, documentazione, ecosistema plugin maturo.

- 🎯 Plugin marketplace pubblico
- 🎯 Multi-tenant managed hosting (servizio premium opzionale)
- 🎯 Localizzazione completa (IT, EN, ES, FR, DE, PT, JA)
- 🎯 Audit di sicurezza terzo
- 🎯 Release 1.0 stabile

---

> Ogni fase è un MVP funzionante, non un waterfall. Una funzionalità di Fase 4 può essere accelerata se la community contribuisce.
