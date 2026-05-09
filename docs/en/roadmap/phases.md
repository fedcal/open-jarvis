# Development phases

The **Jarvis** roadmap is organised in incremental phases, each with a usable MVP and measurable contributions.

!!! note "Indicative dates"
    Dates are intentionally vague because the project is community-driven. Velocity depends on contributors. See [Contributing](../contributing/index.md) if you want to accelerate a phase.

## Phase 0 — Foundation 🌱

**Goal:** project skeleton, open-source identity, contributing path.

- ✅ Bilingual manifesto and vision (`Jarvis.md`)
- ✅ MkDocs Material multilingual documentation (IT + EN)
- ✅ Repository structure (`server/`, `agents/`, `frontend/`, `plugins/`, `infra/`)
- ✅ CONTRIBUTING, CODE_OF_CONDUCT, LICENSE, SECURITY
- ✅ CI for automated docs deploy to GitHub Pages
- ✅ `.env.example` template

## Phase 1 — Core MVP 🏗️

**Goal:** a persistent cross-device conversation on two devices.

- 🎯 Identity layer (OAuth + device pairing)
- 🎯 Memory layer (mem0 + Qdrant)
- 🎯 Base LangGraph orchestrator
- 🎯 Desktop agent (Linux/macOS/Windows)
- 🎯 Mobile agent prototype (Android first, iOS next)
- 🎯 Responsive web chat frontend
- 🎯 E2E integration test: message started on desktop continued on mobile

## Phase 2 — Voice & Watch 🎙️

**Goal:** cross-device voice input + smartwatch integration.

- 🎯 Voice agent: Porcupine + faster-whisper + Piper
- 🎯 Custom wake-word "Hey Jarvis"
- 🎯 Watch agent: Wear OS + WatchKit + InfiniTime
- 🎯 Smart context-aware notifications (calendar, location)
- 🎯 Dynamic routing based on available device

## Phase 3 — Web & Knowledge 🌐

**Goal:** online search, personal knowledge base, RAG.

- 🎯 Scraping agent (Crawl4AI + Firecrawl + Jina Reader)
- 🎯 Generated daily briefing (news + email + agenda)
- 🎯 RAG on personal documents (LlamaIndex + ColPali)
- 🎯 Browser agent (headless Playwright)
- 🎯 Sync with Obsidian, Notion, Google Drive

## Phase 4 — Health 🏃

**Goal:** medical-wearable federation, longitudinal insights.

- 🎯 Medical agent: Oura, Whoop, Polar, Garmin, Withings
- 🎯 FHIR-compatible health vault (HAPI FHIR server)
- 🎯 Open Wearables as unified middleware
- 🎯 Biometric threshold alerting
- 🎯 Automated coaching (sleep, training, recovery)

## Phase 5 — Smart home 🏠

**Goal:** full home-automation integration.

- 🎯 Home Assistant bridge
- 🎯 Matter / Thread / Zigbee via HA
- 🎯 Automated routines based on presence, time, biometrics
- 🎯 First plugin marketplace releases

## Phase 6 — Finance 💰

**Goal:** personal wealth management.

- 🎯 Account aggregation via PSD2 (GoCardless Bank Account Data, Tink)
- 🎯 Crypto wallet (Coinbase, Etherscan, on-chain)
- 🎯 Broker integration (Interactive Brokers, Alpaca)
- 🎯 Daily/weekly financial briefing
- 🎯 Alerts on significant changes

## Phase 7 — AR & XR 👓

**Goal:** AR overlays and VR immersion.

- 🎯 Glasses agent: Brilliant Frame + MentraOS
- 🎯 VR agent: OpenXR on Quest, Index, Pico
- 🎯 Contextual floating UIs (navigation, real-time info)
- 🎯 3D Jarvis avatar in VR

## Phase 8 — Holographic & Maker 🎬

**Goal:** holographic presence + Blender / 3D printing integration.

- 🎯 Holo agent: Looking Glass + Voxon
- 🎯 Holographic talking avatar with lip-sync
- 🎯 Blender Python automation
- 🎯 OctoPrint / Klipper / Moonraker integration
- 🎯 On-demand AI 3D generation (TripoSR)

## Phase 9 — Maturity 🏆

**Goal:** stability, documentation, mature plugin ecosystem.

- 🎯 Public plugin marketplace
- 🎯 Multi-tenant managed hosting (optional premium service)
- 🎯 Full localisation (IT, EN, ES, FR, DE, PT, JA)
- 🎯 Third-party security audit
- 🎯 Stable 1.0 release

---

> Every phase is a working MVP, not a waterfall. A Phase 4 feature can be accelerated if the community contributes.
