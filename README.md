<div align="center">

# 🤖 Jarvis — Personal AI Infrastructure

**An open-source, self-hosted, Iron Man-style AI assistant that lives across all your devices.**
**Un assistente AI open-source, self-hosted, in stile Iron Man che vive su tutti i tuoi dispositivi.**

[![CI](https://github.com/fedcal/open-jarvis/actions/workflows/ci.yml/badge.svg)](https://github.com/fedcal/open-jarvis/actions/workflows/ci.yml)
[![Deploy Docs](https://github.com/fedcal/open-jarvis/actions/workflows/deploy-docs.yml/badge.svg)](https://github.com/fedcal/open-jarvis/actions/workflows/deploy-docs.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-2A6DB2.svg)](http://mypy-lang.org/)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](./CONTRIBUTING.md)
[![GitHub Stars](https://img.shields.io/github/stars/fedcal/open-jarvis?style=social)](https://github.com/fedcal/open-jarvis/stargazers)

[🇮🇹 Italiano](#-italiano) · [🇬🇧 English](#-english) · [📚 Docs](https://fedcal.github.io/open-jarvis/) · [📊 Status](https://fedcal.github.io/open-jarvis/status/) · [🤝 Contributing](./CONTRIBUTING.md) · [🛡️ Security](./SECURITY.md)

</div>

---

## 🇮🇹 Italiano

### Cos'è Jarvis

**Jarvis** è un'infrastruttura AI personale open-source che porta su ogni tuo dispositivo un assistente unico, persistente e contestuale — ispirato al J.A.R.V.I.S. di Iron Man.

Non è un semplice chatbot: è una **rete distribuita di agenti specializzati** che vivono su laptop, smartphone, smartwatch, occhiali smart, visori VR, sistemi olografici e wearable medicali, tutti coordinati da un'identità AI unica e privata.

### Funzionalità chiave

- 🌐 **Ricerca e web scraping intelligente** — agenti che recuperano, sintetizzano e citano fonti dal web in tempo reale
- 🎙️ **Input vocale cross-device** — wake-word, speech-to-text e dialogo naturale su qualsiasi dispositivo
- 👓 **Realtà aumentata e occhiali smart** — overlay informativi su Meta Ray-Ban, XREAL, Brilliant Frame e visori OpenXR
- 🥽 **Realtà virtuale** — interfaccia immersiva su Meta Quest, Valve Index e qualsiasi headset OpenXR
- ✨ **Display olografici** — integrazione con Looking Glass, HYPERVSN e display volumetrici
- ⌚ **Wearable e dispositivi medicali** — Apple Watch, Wear OS, Garmin, Whoop, Oura, dati biometrici via HealthKit / Health Connect / FHIR
- 🧠 **Memoria persistente condivisa** — la conversazione ti segue da un dispositivo all'altro
- 🔐 **Privacy by design** — self-hosted, dati sotto il tuo controllo, modelli locali o cloud a tua scelta
- 🔌 **Estendibile via plugin** — un sistema modulare per aggiungere automazioni, integrazioni e workflow personalizzati

### Architettura in 30 secondi

```
┌─────────────────────────────────────────────────────────┐
│           Identity Layer (auth, device pairing)         │
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│   Orchestration & Routing  ◄──►  Memory (short/long/    │
│                                   semantic + vector DB) │
└─────────────────────────────────────────────────────────┘
                           │
┌──────────┬──────────┬──────────┬──────────┬─────────────┐
│ Desktop  │ Mobile   │ Watch    │ Glasses  │ VR / Holo / │
│ Agent    │ Agent    │ Agent    │ Agent    │ Medical     │
└──────────┴──────────┴──────────┴──────────┴─────────────┘
```

### Quick start

```bash
git clone https://github.com/fedcal/open-jarvis.git
cd open-jarvis
cp .env.example .env
docker compose up -d
```

📖 La guida completa è su **[federicocalo.github.io/open-jarvis](https://fedcal.github.io/open-jarvis/)**.

### Stato del progetto

🚧 **Work in progress.** Stiamo definendo l'architettura e i primi MVP. Cerchiamo contributori — vedi [CONTRIBUTING.md](./CONTRIBUTING.md).

---

## 🇬🇧 English

### What is Jarvis

**Jarvis** is an open-source personal AI infrastructure that brings a unique, persistent and context-aware assistant to every device you own — inspired by Iron Man's J.A.R.V.I.S.

It's not just a chatbot: it's a **distributed network of specialised agents** living on laptops, smartphones, smartwatches, smart glasses, VR headsets, holographic displays and medical wearables, all coordinated by a single private AI identity.

### Key features

- 🌐 **Smart web search & scraping** — agents that fetch, summarise and cite sources from the web in real time
- 🎙️ **Cross-device voice input** — wake-word, speech-to-text and natural dialogue on any device
- 👓 **Augmented reality & smart glasses** — informational overlays on Meta Ray-Ban, XREAL, Brilliant Frame and OpenXR headsets
- 🥽 **Virtual reality** — immersive interface on Meta Quest, Valve Index and any OpenXR-compatible headset
- ✨ **Holographic displays** — integration with Looking Glass, HYPERVSN and volumetric displays
- ⌚ **Wearables & medical devices** — Apple Watch, Wear OS, Garmin, Whoop, Oura, biometric data via HealthKit / Health Connect / FHIR
- 🧠 **Persistent shared memory** — the conversation follows you across devices
- 🔐 **Privacy by design** — self-hosted, data under your control, local or cloud models at your choice
- 🔌 **Plugin-extensible** — a modular system for adding automations, integrations and custom workflows

### 30-second architecture

```
┌─────────────────────────────────────────────────────────┐
│           Identity Layer (auth, device pairing)         │
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│   Orchestration & Routing  ◄──►  Memory (short/long/    │
│                                   semantic + vector DB) │
└─────────────────────────────────────────────────────────┘
                           │
┌──────────┬──────────┬──────────┬──────────┬─────────────┐
│ Desktop  │ Mobile   │ Watch    │ Glasses  │ VR / Holo / │
│ Agent    │ Agent    │ Agent    │ Agent    │ Medical     │
└──────────┴──────────┴──────────┴──────────┴─────────────┘
```

### Quick start

```bash
git clone https://github.com/fedcal/open-jarvis.git
cd open-jarvis
cp .env.example .env
docker compose up -d
```

📖 Full documentation at **[federicocalo.github.io/open-jarvis](https://fedcal.github.io/open-jarvis/)**.

### Project status

🚧 **Work in progress.** We are defining the architecture and the first MVPs. We are looking for contributors — see [CONTRIBUTING.md](./CONTRIBUTING.md).

---

## 📂 Repository structure / Struttura del repository

```
jarvis/
├── server/          # Core backend: API, auth, memory, LLM, orchestration, routing, scraping
├── agents/          # Device-side agents (desktop, mobile, watch, browser, voice,
│                    #                     glasses, VR, holo, medical, scraping)
├── frontend/        # Web UI and admin dashboard
├── plugins/         # Plugin system (productivity, smart home, dev tools, fitness, …)
├── infra/           # Docker, Kubernetes, Terraform, monitoring
├── docs/            # Bilingual MkDocs Material documentation (IT + EN)
├── scripts/         # Utility and dev scripts
├── tests/           # Integration and E2E tests
└── Jarvis.md        # Project vision and bilingual whitepaper
```

---

## 📜 License / Licenza

This project is released under the **MIT License** — see [LICENSE](./LICENSE).
Questo progetto è rilasciato con licenza **MIT** — vedi [LICENSE](./LICENSE).

---

## 🤝 Credits / Crediti

Created and maintained by **[Federico Calò](https://federicocalo.dev)** — [federicocalo.dev](https://federicocalo.dev)
Creato e mantenuto da **[Federico Calò](https://federicocalo.dev)** — [federicocalo.dev](https://federicocalo.dev)

Contributors are very welcome! See [CONTRIBUTING.md](./CONTRIBUTING.md).
I contributori sono benvenuti! Vedi [CONTRIBUTING.md](./CONTRIBUTING.md).

<div align="center">

— ⚡ Built with passion for an open, decentralised, personal AI future ⚡ —

</div>
