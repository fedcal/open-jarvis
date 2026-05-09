# JARVIS — Personal AI Infrastructure

> **Bilingual whitepaper / Whitepaper bilingue**
> 🇬🇧 [English](#-english) · 🇮🇹 [Italiano](#-italiano)

---

## 🇬🇧 English

### Project vision

The goal of this project is to build a personal AI assistant in the spirit of Iron Man's J.A.R.V.I.S.: a unique AI identity that lives on **multiple devices simultaneously** while remaining tied to a single user.

The assistant must be able to:

- recognise that smartphone, laptop, smartwatch, AR glasses, VR headset, holographic display and medical wearables all belong to the **same user**;
- maintain **shared memory** across every device;
- continue a conversation **seamlessly** as the user moves from one device to another;
- adapt its behaviour to the **available device and context** (driving, exercising, coding, sleeping…);
- execute **local or remote tasks** through specialised agents;
- run in **self-hosted** or **hybrid cloud** mode;
- guarantee **privacy and full data ownership**.

### Product philosophy

This is **not** a chatbot app. It is a **Personal AI Infrastructure**: every user owns and operates their own instance of the system.

| Device | Role |
|---|---|
| Laptop / Desktop | Coding, terminal, filesystem, automation, heavy reasoning |
| Smartphone | Notifications, GPS, camera, microphone, on-the-go dialogue |
| Smartwatch | Biometric data, quick notifications, wake-word, gestures |
| Smart glasses | Visual overlays, navigation, real-time information |
| VR headset | Immersive interface, simulation, multimodal interaction |
| Holographic display | 3D output, ambient companion, presence |
| Medical wearables | Health data, alerts, longitudinal monitoring |

All devices belong to the **same personal mesh**, coordinated by a single AI identity.

### Core capabilities

#### 1. Web search and intelligent scraping

Specialised agents that fetch, summarise, validate and **cite** web sources in real time. The reference stack:

- **Crawl4AI** — Apache 2.0, Markdown-ready output for LLM pipelines
- **Firecrawl (self-hosted)** — recursive crawling for knowledge-base building
- **Jina Reader** — zero-setup URL → clean Markdown
- **ScrapeGraphAI** — schema-validated structured extraction

#### 2. Voice input and wake-word

A unified voice pipeline across every device:

- **Picovoice Porcupine** for ultra-low-latency on-device wake-word (works on MCUs, smartwatches, glasses)
- **openWakeWord** as a fully open alternative
- **faster-whisper** for accurate STT on the local server
- **Coqui TTS / Piper** for natural voice synthesis

#### 3. AR glasses and smart eyewear

- **Brilliant Labs Frame** — MIT-licensed Python/Flutter SDK, BLE-native, on-device Lua
- **MentraOS** — open-source OS for smart glasses (Mach1, Vuzix Z100, Even Realities G1)
- **XREAL Air** — Unity/Android SDK
- **Meta Wearables Device Access Toolkit** — preview, GA in 2026

#### 4. Virtual reality

- **OpenXR** as the cross-vendor standard
- **Monado** as the Linux-native open-source runtime
- **Meta OpenXR SDK** (Quest), **Valve Index** via Monado, **Pico** OpenXR 1.1 compliant

#### 5. Holographic and volumetric displays

- **Looking Glass Factory** — public Core SDK, Unity/Unreal plugins, light-field rendering
- **Voxon Photonics** — C++/Python SDK for true volumetric output
- **HYPERVSN** — for ambient holographic presence

#### 6. Wearables and medical devices

Open APIs and aggregators:

- **Oura Ring API v2** — sleep, HRV, readiness (OAuth 2.0)
- **Whoop API v2** — strain, recovery (OAuth 2.0 + webhooks)
- **Polar AccessLink**, **Garmin Health API**, **Withings**, **Fitbit / Google Health**
- **Dexcom CGM** — real-time glucose (FDA-cleared)
- **Apple HealthKit** / **Google Health Connect** for on-device aggregation
- **Open Wearables** as a unified open-source middleware
- **HAPI FHIR** + **SMART on FHIR** for clinical interoperability (HL7 FHIR R4/R5)

#### 7. Persistent shared memory

- **mem0** — multi-scope memory layer (user/agent/session/org)
- **Qdrant** — high-performance Rust vector store
- **Zep** — temporal knowledge graph for evolving preferences
- **Letta (ex-MemGPT)** — agent-managed memory paging

#### 8. Specialised agent orchestration

- **LangGraph** — graph-based orchestrator with checkpointing and time travel
- **Pydantic AI** — type-safe agents with validated structured output
- **CrewAI** / **AutoGen** as alternatives for role-based scenarios
- Compatible with **MCP** (Anthropic) and **A2A** (Google) protocols

### High-level architecture

```text
┌──────────────────────────────────────────────────────────────────┐
│                         IDENTITY LAYER                           │
│      OAuth · device pairing · token management · certificates    │
└──────────────────────────────────────────────────────────────────┘
                                │
┌──────────────────────────────────────────────────────────────────┐
│                  ORCHESTRATION & ROUTING LAYER                   │
│        LangGraph · MCP · A2A · capability routing · policies     │
└──────────────────────────────────────────────────────────────────┘
                                │
┌──────────────────────────────────────────────────────────────────┐
│                          MEMORY LAYER                            │
│   short-term · long-term · semantic · vector DB · health (FHIR)  │
└──────────────────────────────────────────────────────────────────┘
                                │
┌──────────┬──────────┬──────────┬──────────┬──────────┬───────────┐
│ Desktop  │ Mobile   │ Watch    │ Glasses  │   VR     │ Holo /    │
│ Agent    │ Agent    │ Agent    │ Agent    │  Agent   │ Medical   │
│          │          │          │          │          │ Agent     │
└──────────┴──────────┴──────────┴──────────┴──────────┴───────────┘
                                │
┌──────────────────────────────────────────────────────────────────┐
│                  PLUGIN & INTEGRATIONS LAYER                     │
│   productivity · smart home · dev tools · fitness · finance ·    │
│            web scraping · third-party APIs                       │
└──────────────────────────────────────────────────────────────────┘
```

### Distribution model

Every user can:

1. clone the repository
2. configure their own credentials
3. deploy their own instance
4. enrol their devices
5. use a custom personal domain

```text
jarvis.mydomain.com
assistant.firstname-lastname.dev
ai.personal-domain.com
```

Full control over: data, AI models, infrastructure, access policies.

### Repository structure

```text
jarvis/
├── server/                # core backend
│   ├── api/               # REST / WebSocket / gRPC
│   ├── auth/              # identity & device pairing
│   ├── memory/            # mem0 / Qdrant / Zep integrations
│   ├── llm/               # model abstraction & routing
│   ├── orchestration/     # LangGraph workflows
│   ├── routing/           # device & capability routing
│   └── scraping/          # Crawl4AI / Firecrawl pipelines
│
├── agents/                # device-side agents
│   ├── desktop-agent/
│   ├── mobile-agent/
│   ├── watch-agent/
│   ├── browser-agent/
│   ├── voice-agent/
│   ├── glasses-agent/     # Frame · MentraOS · XREAL
│   ├── vr-agent/          # OpenXR · Monado
│   ├── holo-agent/        # Looking Glass · Voxon
│   ├── medical-agent/     # Oura · Whoop · FHIR · HealthKit
│   └── scraping-agent/    # autonomous research
│
├── frontend/              # web UI & admin
├── plugins/               # plugin system
├── infra/                 # docker · kubernetes · terraform · monitoring
├── docs/                  # bilingual MkDocs Material site
├── scripts/               # dev & ops scripts
├── tests/                 # integration & E2E
└── .env.example           # configuration template
```

### Roadmap

- **Phase 1 — MVP:** desktop + mobile, single sign-on, persistent memory, conversation sync, web search agent.
- **Phase 2:** smartwatch + voice, intelligent notifications, biometric monitoring, intent recognition.
- **Phase 3:** smart glasses + AR overlays, browser automation, calendar/email integration, smart home.
- **Phase 4:** VR + holographic displays, multi-modal embodiment, ambient presence.
- **Phase 5:** medical wearables federation, FHIR-compatible health vault, longitudinal insights.

### Differentiator

> The value is not the chatbot. The real value is a **persistent AI identity that follows the user across every device**.

The hard problems are not the models. They are: identity management, synchronisation, context routing, permission management, privacy, device orchestration.

This is the foundation of a real Jarvis.

---

## 🇮🇹 Italiano

### Visione del progetto

L'obiettivo è costruire un assistente AI personale ispirato al J.A.R.V.I.S. di Iron Man: un'**identità AI unica** che vive su **più dispositivi contemporaneamente** restando legata a un singolo utente.

L'assistente deve essere in grado di:

- riconoscere che smartphone, laptop, smartwatch, occhiali AR, visore VR, display olografico e wearable medicali appartengono **allo stesso utente**;
- mantenere una **memoria condivisa** tra tutti i dispositivi;
- continuare una conversazione **senza soluzione di continuità** quando l'utente passa da un device a un altro;
- adattare il comportamento al **dispositivo disponibile e al contesto** (alla guida, durante l'allenamento, mentre programma, durante il sonno...);
- eseguire **task locali o remoti** tramite agenti specializzati;
- funzionare in modalità **self-hosted** o **hybrid cloud**;
- garantire **privacy e pieno controllo dei dati**.

### Filosofia del prodotto

Questo **non** è una chatbot app. È una **Personal AI Infrastructure**: ogni utente possiede e gestisce la propria istanza del sistema.

| Dispositivo | Ruolo |
|---|---|
| Laptop / Desktop | Coding, terminale, filesystem, automazioni, reasoning complesso |
| Smartphone | Notifiche, GPS, fotocamera, microfono, dialogo on-the-go |
| Smartwatch | Dati biometrici, notifiche rapide, wake-word, gesture |
| Occhiali smart | Overlay visivi, navigazione, informazioni in tempo reale |
| Visore VR | Interfaccia immersiva, simulazione, interazione multimodale |
| Display olografico | Output 3D, presenza ambientale, compagno visuale |
| Wearable medicali | Dati di salute, alert, monitoraggio longitudinale |

Tutti i dispositivi fanno parte della **stessa rete personale**, coordinata da un'unica identità AI.

### Funzionalità principali

#### 1. Ricerca e scraping intelligente

Agenti specializzati che recuperano, sintetizzano, validano e **citano** fonti dal web in tempo reale. Stack di riferimento:

- **Crawl4AI** — Apache 2.0, output Markdown pronto per pipeline LLM
- **Firecrawl (self-hosted)** — crawling ricorsivo per knowledge base
- **Jina Reader** — URL → Markdown pulito senza setup
- **ScrapeGraphAI** — estrazione strutturata schema-validata

#### 2. Input vocale e wake-word

Una pipeline vocale unificata su ogni dispositivo:

- **Picovoice Porcupine** per wake-word on-device a bassissima latenza (funziona su MCU, smartwatch, occhiali)
- **openWakeWord** come alternativa fully open
- **faster-whisper** per STT accurato sul server locale
- **Coqui TTS / Piper** per sintesi vocale naturale

#### 3. Occhiali AR e smart eyewear

- **Brilliant Labs Frame** — SDK Python/Flutter MIT, BLE nativo, Lua on-device
- **MentraOS** — OS open source per smart glasses (Mach1, Vuzix Z100, Even Realities G1)
- **XREAL Air** — SDK Unity/Android
- **Meta Wearables Device Access Toolkit** — in preview, GA nel 2026

#### 4. Realtà virtuale

- **OpenXR** come standard cross-vendor
- **Monado** come runtime open source nativo Linux
- **Meta OpenXR SDK** (Quest), **Valve Index** via Monado, **Pico** OpenXR 1.1 compliant

#### 5. Display olografici e volumetrici

- **Looking Glass Factory** — Core SDK pubblico, plugin Unity/Unreal, light-field rendering
- **Voxon Photonics** — SDK C++/Python per output volumetrico vero
- **HYPERVSN** — per presenza olografica ambient

#### 6. Wearable e dispositivi medicali

API aperte e aggregatori:

- **Oura Ring API v2** — sonno, HRV, readiness (OAuth 2.0)
- **Whoop API v2** — strain, recovery (OAuth 2.0 + webhook)
- **Polar AccessLink**, **Garmin Health API**, **Withings**, **Fitbit / Google Health**
- **Dexcom CGM** — glucosio in tempo reale (FDA-cleared)
- **Apple HealthKit** / **Google Health Connect** per aggregazione on-device
- **Open Wearables** come middleware open source unificato
- **HAPI FHIR** + **SMART on FHIR** per interoperabilità clinica (HL7 FHIR R4/R5)

#### 7. Memoria persistente condivisa

- **mem0** — memoria multi-scope (user/agent/session/org)
- **Qdrant** — vector store Rust ad alte prestazioni
- **Zep** — knowledge graph temporale per preferenze che evolvono
- **Letta (ex-MemGPT)** — paging della memoria gestito dall'agente

#### 8. Orchestrazione di agenti specializzati

- **LangGraph** — orchestratore a grafo con checkpointing e time travel
- **Pydantic AI** — agenti type-safe con output strutturato validato
- **CrewAI** / **AutoGen** come alternative per scenari role-based
- Compatibilità con i protocolli **MCP** (Anthropic) e **A2A** (Google)

### Architettura ad alto livello

```text
┌──────────────────────────────────────────────────────────────────┐
│                         IDENTITY LAYER                           │
│  OAuth · pairing dei device · gestione token · certificati       │
└──────────────────────────────────────────────────────────────────┘
                                │
┌──────────────────────────────────────────────────────────────────┐
│                  ORCHESTRATION & ROUTING LAYER                   │
│      LangGraph · MCP · A2A · capability routing · policy         │
└──────────────────────────────────────────────────────────────────┘
                                │
┌──────────────────────────────────────────────────────────────────┐
│                          MEMORY LAYER                            │
│  breve termine · lungo termine · semantica · vector DB · FHIR    │
└──────────────────────────────────────────────────────────────────┘
                                │
┌──────────┬──────────┬──────────┬──────────┬──────────┬───────────┐
│ Desktop  │ Mobile   │ Watch    │ Occhiali │   VR     │ Holo /    │
│ Agent    │ Agent    │ Agent    │ Agent    │  Agent   │ Medical   │
│          │          │          │          │          │ Agent     │
└──────────┴──────────┴──────────┴──────────┴──────────┴───────────┘
                                │
┌──────────────────────────────────────────────────────────────────┐
│                 LIVELLO PLUGIN E INTEGRAZIONI                    │
│   produttività · smart home · dev tools · fitness · finanza ·    │
│            web scraping · API di terze parti                     │
└──────────────────────────────────────────────────────────────────┘
```

### Modello di distribuzione

Ogni utente può:

1. clonare il repository
2. configurare le proprie credenziali
3. deployare la propria istanza
4. registrare i propri dispositivi
5. usare un dominio personale

```text
jarvis.miodominio.com
assistant.nomecognome.dev
ai.personal-domain.com
```

Pieno controllo su: dati, modelli AI, infrastruttura, policy di accesso.

### Struttura del repository

```text
jarvis/
├── server/                # backend principale
│   ├── api/               # REST / WebSocket / gRPC
│   ├── auth/              # identità & pairing
│   ├── memory/            # integrazioni mem0 / Qdrant / Zep
│   ├── llm/               # astrazione modelli
│   ├── orchestration/     # workflow LangGraph
│   ├── routing/           # routing device & capability
│   └── scraping/          # pipeline Crawl4AI / Firecrawl
│
├── agents/                # agenti device-side
│   ├── desktop-agent/
│   ├── mobile-agent/
│   ├── watch-agent/
│   ├── browser-agent/
│   ├── voice-agent/
│   ├── glasses-agent/     # Frame · MentraOS · XREAL
│   ├── vr-agent/          # OpenXR · Monado
│   ├── holo-agent/        # Looking Glass · Voxon
│   ├── medical-agent/     # Oura · Whoop · FHIR · HealthKit
│   └── scraping-agent/    # ricerca autonoma
│
├── frontend/              # UI web e admin
├── plugins/               # sistema plugin
├── infra/                 # docker · kubernetes · terraform · monitoring
├── docs/                  # sito bilingue MkDocs Material
├── scripts/               # script dev e ops
├── tests/                 # integration & E2E
└── .env.example           # template di configurazione
```

### Roadmap

- **Fase 1 — MVP:** desktop + mobile, login unico, memoria persistente, sync conversazioni, agente di ricerca web.
- **Fase 2:** smartwatch + voce, notifiche intelligenti, monitoraggio biometrico, riconoscimento intenti.
- **Fase 3:** occhiali smart + overlay AR, automazione browser, calendar/email, smart home.
- **Fase 4:** VR + display olografici, embodiment multi-modale, presenza ambientale.
- **Fase 5:** federazione di wearable medicali, health vault FHIR-compatibile, insight longitudinali.

### Differenziatore

> Il valore non è il chatbot. Il valore reale è una **identità AI persistente che accompagna l'utente su ogni dispositivo**.

Le sfide difficili non sono i modelli. Sono: identity management, sincronizzazione, context routing, gestione dei permessi, privacy, orchestrazione dei device.

Questa è la vera base per costruire un Jarvis reale.

---

<div align="center">

**Authored by [Federico Calò](https://federicocalo.dev) · [federicocalo.dev](https://federicocalo.dev)**
**Released under the [MIT License](./LICENSE) · Contributions welcome → [CONTRIBUTING.md](./CONTRIBUTING.md)**

</div>
