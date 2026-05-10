<div align="center">

# 🤖 Jarvis — Personal AI Infrastructure

**An open-source, self-hosted, Iron Man-style AI assistant that lives across all your devices.**
**Un assistente AI open-source, self-hosted, in stile Iron Man che vive su tutti i tuoi dispositivi.**

[![CI](https://github.com/fedcal/open-jarvis/actions/workflows/ci.yml/badge.svg)](https://github.com/fedcal/open-jarvis/actions/workflows/ci.yml)
[![Deploy Docs](https://github.com/fedcal/open-jarvis/actions/workflows/deploy-docs.yml/badge.svg)](https://github.com/fedcal/open-jarvis/actions/workflows/deploy-docs.yml)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](./LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-2A6DB2.svg)](http://mypy-lang.org/)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](./CONTRIBUTING.md)
[![GitHub Stars](https://img.shields.io/github/stars/fedcal/open-jarvis?style=social)](https://github.com/fedcal/open-jarvis/stargazers)

[🇮🇹 Italiano](#-italiano) · [🇬🇧 English](#-english) · [📚 Docs](https://fedcal.github.io/open-jarvis/) · [📊 Status](https://fedcal.github.io/open-jarvis/status/) · [🤝 Contributing](./CONTRIBUTING.md) · [🛡️ Security](./SECURITY.md) · [👥 Users](./USERS.md)

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

> **Vuoi solo provarlo sul tuo PC senza dominio?** Vai dritto a
> **[Installazione locale (PC + Wi-Fi domestico)](./docs/it/user-manual/install/local-lan.md)**:
> tutto gira sul tuo PC, gli altri dispositivi si collegano via Wi-Fi
> usando `jarvis.local` o l'IP della LAN.
>
> **Vuoi sviluppare contribuendo al progetto?** Vedi la guida
> **[Modalità sviluppo](./docs/it/contributing/development.md)**.

#### 🖥️ Server (VPS o PC sempre acceso)

Il server è il cuore del sistema: gira in Docker, espone HTTPS via Caddy ed è l'unico dispositivo che deve essere sempre online.

```bash
git clone https://github.com/fedcal/open-jarvis.git
cd open-jarvis
cp .env.example .env       # configura dominio, JARVIS_JWT_*, password DB
docker compose up -d
curl https://jarvis.example.com/health   # smoke-test
```

Registra il primo utente:

```bash
curl -X POST https://jarvis.example.com/api/v1/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"tu@example.com","password":"<min-12-char>","display_name":"Tu"}'
```

📖 Guide: **[Server VPS](./docs/it/user-manual/install/server.md)** · **[Locale Wi-Fi (no dominio)](./docs/it/user-manual/install/local-lan.md)**.

#### 🌐 Web (Angular 18 PWA)

```bash
cd frontend/web
pnpm install
pnpm start                       # → http://localhost:4200
```

Apri il browser, inserisci come *Server URL* `http://localhost:8090` (o l'IP del tuo PC), registrati e parti.

Build production:

```bash
pnpm build
# dist/open-jarvis-web/browser/ → servi con Caddy / Nginx / qualsiasi static host
```

📖 [Guida web](./frontend/web/README.md).

#### 💻 Desktop (Tauri 2 — macOS · Windows · Linux)

```bash
# Installa Rust toolchain (una sola volta)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Avvio dev (apre la finestra nativa con HMR del frontend)
pnpm install
pnpm --filter @open-jarvis/desktop dev

# Build firmabile per distribuzione
pnpm --filter @open-jarvis/desktop build
```

Output: `.dmg`/`.app` (macOS), `.msi`/`.exe` (Windows), `.AppImage`/`.deb` (Linux).
📖 [Guida desktop](./agents/desktop/README.md).

#### 📱 Smartphone (Ionic + Angular + Capacitor)

```bash
cd agents/mobile
pnpm install
pnpm start                       # PWA in browser su :4300

# Build native
pnpm sync && pnpm cap add ios && pnpm ios       # apre Xcode
pnpm sync && pnpm cap add android && pnpm android  # apre Android Studio
```

Al primo avvio sul telefono inserisci come *Server URL* l'IP del PC (`http://192.168.X.Y:8090`). Una volta avuto un client web/desktop autenticato, puoi anche fare il **pairing via QR** (codice 6 cifre, TTL 5 min) senza ridigitare le credenziali.

📖 [Guida mobile](./agents/mobile/README.md) · [Pairing dettagliato](./docs/it/security/identity-layer.md).

#### 🌐 Browser (PWA)

Apri `https://jarvis.example.com` su qualunque browser desktop o mobile, aggiungi alla home, autenticati con email/password o passkey. La PWA usa la stessa API REST + WebSocket degli altri client.

#### ⌚ Smartwatch · 👓 Occhiali AR · 🥽 VR · ✨ Olografico · ❤️ Wearable medicali

In roadmap (M2-M8). Tutti i client erediteranno il pairing dal device mobile/desktop "host" già autenticato.

📖 **[Multi-device · guida unificata a tutti i dispositivi](./docs/it/user-manual/multi-device.md)**

### Aggiornare Open-Jarvis

Il versionamento segue **SemVer** (`MAJOR.MINOR.PATCH`). Server e agent sono disaccoppiati: stesso MAJOR ⇒ compatibilità garantita.

```bash
# Server (con migrazioni DB idempotenti)
cd /opt/open-jarvis
git fetch --tags && git checkout vX.Y.Z
docker compose pull
docker compose run --rm server alembic upgrade head
docker compose up -d

# Desktop
brew upgrade open-jarvis            # macOS
winget upgrade OpenJarvis.Desktop   # Windows
flatpak update dev.openjarvis.Desktop  # Linux

# Mobile: App Store / Play Store / F-Droid (auto)
# Web PWA: il service worker propone l'aggiornamento al refresh
```

📖 **[Procedura completa di aggiornamento](./docs/it/user-manual/updates.md)** — include rollback, migrazioni, checklist produzione.

### Problemi comuni

Se qualcosa non va, abbiamo una knowledge base dedicata:

📖 **[docs/it/troubleshooting/](./docs/it/troubleshooting/index.md)** — build & Docker, server runtime, identity, memory, chat, pairing.

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

> **Just want to try it on your PC, no domain?** Jump to
> **[Local install (PC + home Wi-Fi)](./docs/it/user-manual/install/local-lan.md)**:
> everything runs on your PC, other devices connect via Wi-Fi using
> `jarvis.local` or the LAN IP.
>
> **Want to develop / contribute?** See the
> **[Development mode](./docs/it/contributing/development.md)** guide.

#### 🖥️ Server (VPS or always-on PC)

The server is the heart of the system: runs in Docker, exposes HTTPS via Caddy, and is the only device that must be always online.

```bash
git clone https://github.com/fedcal/open-jarvis.git
cd open-jarvis
cp .env.example .env       # set domain, JARVIS_JWT_*, DB password
docker compose up -d
curl https://jarvis.example.com/health   # smoke test
```

Register the first user:

```bash
curl -X POST https://jarvis.example.com/api/v1/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"you@example.com","password":"<min-12-chars>","display_name":"You"}'
```

📖 Guides: **[Server VPS](./docs/it/user-manual/install/server.md)** · **[Local Wi-Fi (no domain)](./docs/it/user-manual/install/local-lan.md)**.

#### 🌐 Web (Angular 18 PWA)

```bash
cd frontend/web
pnpm install
pnpm start                       # → http://localhost:4200
```

Open the browser, set *Server URL* to `http://localhost:8090` (or your PC's LAN IP), register and go. Production:

```bash
pnpm build  # dist/open-jarvis-web/browser/ → serve with Caddy/Nginx
```

📖 [Web guide](./frontend/web/README.md).

#### 💻 Desktop (Tauri 2 — macOS · Windows · Linux)

```bash
# Install Rust toolchain (one-off)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Dev (native window with frontend HMR)
pnpm install
pnpm --filter @open-jarvis/desktop dev

# Signed distributable build
pnpm --filter @open-jarvis/desktop build
```

Output: `.dmg`/`.app` (macOS), `.msi`/`.exe` (Windows), `.AppImage`/`.deb` (Linux).
📖 [Desktop guide](./agents/desktop/README.md).

#### 📱 Smartphone (Ionic + Angular + Capacitor)

```bash
cd agents/mobile
pnpm install
pnpm start                       # PWA in browser on :4300

# Native builds
pnpm sync && pnpm cap add ios && pnpm ios       # opens Xcode
pnpm sync && pnpm cap add android && pnpm android  # opens Android Studio
```

On first launch on the phone, enter your PC's LAN IP as *Server URL* (`http://192.168.X.Y:8090`). Once you have a web/desktop client authenticated, you can also use **QR pairing** (6-digit code, 5-min TTL) without re-typing credentials.

📖 [Mobile guide](./agents/mobile/README.md) · [Pairing details](./docs/it/security/identity-layer.md).

#### 🌐 Browser (PWA)

Open `https://jarvis.example.com` on any desktop or mobile browser, add it to the home screen, authenticate with email/password or passkey. The PWA uses the same REST + WebSocket API as the other clients.

#### ⌚ Smartwatch · 👓 AR glasses · 🥽 VR · ✨ Holographic · ❤️ Medical wearables

Roadmapped (M2-M8). All clients will inherit pairing from a mobile/desktop "host" device already authenticated.

📖 **[Multi-device · unified guide for all devices](./docs/it/user-manual/multi-device.md)**

### Updating Open-Jarvis

Versioning follows **SemVer** (`MAJOR.MINOR.PATCH`). Server and agents are decoupled: same MAJOR ⇒ compatibility guaranteed.

```bash
# Server (with idempotent DB migrations)
cd /opt/open-jarvis
git fetch --tags && git checkout vX.Y.Z
docker compose pull
docker compose run --rm server alembic upgrade head
docker compose up -d

# Desktop
brew upgrade open-jarvis            # macOS
winget upgrade OpenJarvis.Desktop   # Windows
flatpak update dev.openjarvis.Desktop  # Linux

# Mobile: App Store / Play Store / F-Droid (auto)
# Web PWA: the service worker prompts to refresh on update
```

📖 **[Full update procedure](./docs/it/user-manual/updates.md)** — includes rollback, migrations, production checklist.

### Common problems

If something goes wrong, we have a dedicated knowledge base:

📖 **[docs/it/troubleshooting/](./docs/it/troubleshooting/index.md)** — build & Docker, server runtime, identity, memory, chat, pairing.

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

This project is released under **GNU AGPL-3.0** — see [LICENSE](./LICENSE).
Questo progetto è rilasciato sotto **GNU AGPL-3.0** — vedi [LICENSE](./LICENSE).

> 🆓 **Always free, always open source.** AGPL guarantees that any modification — even when offered as a network service — must be published. Read the [License rationale](./docs/it/legal/license-rationale.md) and the [Public users registry](./USERS.md).
> 🆓 **Sempre libero, sempre open source.** AGPL garantisce che ogni modifica — anche se offerta come servizio in rete — debba essere pubblicata. Leggi la [Licence rationale](./docs/it/legal/license-rationale.md) e il [Registro pubblico utenti](./USERS.md).

---

## 🤝 Credits / Crediti

Created and maintained by **[Federico Calò](https://federicocalo.dev)** — [federicocalo.dev](https://federicocalo.dev)
Creato e mantenuto da **[Federico Calò](https://federicocalo.dev)** — [federicocalo.dev](https://federicocalo.dev)

Contributors are very welcome! See [CONTRIBUTING.md](./CONTRIBUTING.md).
I contributori sono benvenuti! Vedi [CONTRIBUTING.md](./CONTRIBUTING.md).

<div align="center">

— ⚡ Built with passion for an open, decentralised, personal AI future ⚡ —

</div>
