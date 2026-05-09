---
title: "Catalog completo integrazioni"
description: "Catalogo enciclopedico di tutte le integrazioni di Open-Jarvis: dispositivi, servizi, API, protocolli, OS."
keywords: "integrazioni, catalog, wearable, smart home, AI providers, OAuth, IoT"
---

# Catalog completo integrazioni

Inventario di **tutte le integrazioni** del sistema Open-Jarvis. Per ognuna: stato, fase, riferimenti.

!!! tip "Stato"
    🟢 Implementato · 🟡 In progress · ⚪ Pianificato · 🟣 Vision long-term

## 🤖 LLM providers

| Provider | Modelli | Stato | Note |
|---|---|---|---|
| **Anthropic** | Claude Opus 4.7, Sonnet 4.6, Haiku 4.5 | 🟢 | Prompt caching, tool use |
| **OpenAI** | GPT-4.1, GPT-4.1-mini, GPT-4o | 🟢 | Tool use, structured output |
| **Groq** | Llama 3.3 70B, Mixtral | 🟢 | Bassa latenza |
| **Mistral AI** | Mistral Small 3.1, Large | ⚪ | EU-based |
| **Google** | Gemini 2.0 Flash | ⚪ | Multimodal |
| **Ollama** | Llama 3.x, Qwen 2.5, DeepSeek | 🟢 | 100% locale |
| **vLLM / TGI** | Self-hosted | ⚪ | Custom finetuned models |

## 🧠 Memory & vector store

| Sistema | Ruolo | Stato |
|---|---|---|
| **mem0** | Long-term memory layer | 🟡 |
| **Qdrant** | Vector store hybrid | 🟡 |
| **Zep / Graphiti** | Temporal knowledge graph | ⚪ |
| **Letta (MemGPT)** | Agent-managed paging | ⚪ |
| **ChromaDB** | Vector store dev/proto | ⚪ |
| **PostgreSQL + pgvector** | Vector store Postgres | ⚪ |
| **Redis** | Short-term cache | 🟡 |

## 🌐 Web search & scraping

| Tool | Tipo | Stato |
|---|---|---|
| **Crawl4AI** | Open source scraping | ⚪ |
| **Firecrawl** | Self-hosted recursive | ⚪ |
| **Jina Reader** | Zero-setup URL→Markdown | ⚪ |
| **ScrapeGraphAI** | LLM-powered extraction | ⚪ |
| **SearxNG** | Privacy meta-search | ⚪ |
| **Brave Search API** | Search API privacy | ⚪ |
| **GDELT** | Big data news global | ⚪ |
| **Currents API** | News REST | ⚪ |

## 📰 RSS & news aggregators

| Tool | Tipo | Stato |
|---|---|---|
| **Miniflux** | RSS reader self-hosted | ⚪ |
| **FreshRSS** | RSS reader PHP | ⚪ |
| **Bluesky AT Protocol** | Decentralized social | ⚪ |
| **Mastodon API** | ActivityPub | ⚪ |

## 📄 Document sources (RAG)

| Sorgente | Connettore | Stato |
|---|---|---|
| **Obsidian** | watchdog + Khoj plugin pattern | ⚪ |
| **Notion** | LlamaIndex NotionPageReader | ⚪ |
| **Google Drive** | Watch API + push | ⚪ |
| **Dropbox** | Webhooks | ⚪ |
| **Local filesystem** | watchdog + inotify | ⚪ |
| **Apple Notes** | AppleScript export | ⚪ |
| **Apple Mail** | mbox parsing | ⚪ |
| **Logseq** | watchdog Markdown | ⚪ |
| **Microsoft OneNote** | Graph API | ⚪ |
| **Joplin** | API REST | ⚪ |

## 🎙️ Voice pipeline

| Componente | Tool | Stato |
|---|---|---|
| Wake-word | **Picovoice Porcupine** | ⚪ |
| Wake-word open | **openWakeWord** | ⚪ |
| Wake-word ESP32 | **microWakeWord** | ⚪ |
| VAD | **Silero VAD** | ⚪ |
| STT | **faster-whisper** | ⚪ |
| STT lightweight | **Vosk** | ⚪ |
| TTS | **Piper** | ⚪ |
| TTS GPU | **Kokoro 82M** | ⚪ |
| Voice clone | **XTTS-v2** | ⚪ |
| Speaker diarization | **pyannote.audio** | ⚪ |

## 🏃 Health & medical wearables

| Provider | Auth | Stato |
|---|---|---|
| **Oura Ring v2** | OAuth 2.0 | ⚪ |
| **Whoop v2** | OAuth + webhook | ⚪ |
| **Polar AccessLink** | OAuth 2.0 | ⚪ |
| **Garmin Health API** | OAuth 1.0a | ⚪ |
| **Withings** | OAuth 2.0 | ⚪ |
| **Fitbit / Google Health** | Google OAuth | ⚪ |
| **Dexcom CGM** | OAuth 2.0 | ⚪ |
| **Apple HealthKit** | iOS companion | ⚪ |
| **Google Health Connect** | Android SDK | ⚪ |
| **Open Wearables** middleware | REST | ⚪ |
| **HAPI FHIR** vault | FHIR R4 | ⚪ |

## 💰 Finance

| Provider | Categoria | Stato |
|---|---|---|
| **TrueLayer** | Banking PSD2 EU | ⚪ |
| **GoCardless Bank Data** | Banking PSD2 EU | ⚪ |
| **Tink (Visa)** | Banking enterprise | 🟣 |
| **Plaid** | Banking USA | 🟣 |
| **Interactive Brokers** | Broker globale | ⚪ |
| **Alpaca** | Broker US | ⚪ |
| **Coinbase** | Crypto exchange | ⚪ |
| **Binance** | Crypto exchange | ⚪ |
| **Kraken** | Crypto exchange | ⚪ |
| **Etherscan** | Blockchain ETH | ⚪ |
| **Zerion** | Cross-chain crypto | ⚪ |
| **Firefly III** | Tracker self-hosted | ⚪ |
| **Maybe / Sure** | Tracker AI-ready | ⚪ |
| **Wallos** | Subscription tracker | ⚪ |

## 🏠 Smart home

| Sistema | Protocollo | Stato |
|---|---|---|
| **Home Assistant** | REST + WebSocket | ⚪ |
| **Matter 1.5** | python-matter-server | ⚪ |
| **Thread / OpenThread** | OTBR | ⚪ |
| **Zigbee 3.0** | zigpy + Z2M / ZHA | ⚪ |
| **MQTT (Mosquitto)** | Event bus | ⚪ |
| **EMQX** | Event bus enterprise | ⚪ |
| **Frigate** | NVR computer vision | ⚪ |
| **ESPHome** | Custom devices | ⚪ |
| **Tasmota** | Firmware ESP | ⚪ |
| **deCONZ** | Zigbee gateway | ⚪ |

## 👓 AR / VR / glasses

| Device | SDK | Stato |
|---|---|---|
| **Brilliant Frame** | Python/Flutter MIT | ⚪ |
| **MentraOS** (Mach1, Vuzix Z100, G1) | TypeScript | ⚪ |
| **XREAL Air** | Unity / Android | ⚪ |
| **Meta Ray-Ban** | Wearables Toolkit | 🟣 |
| **Meta Quest** | OpenXR / Meta SDK | ⚪ |
| **Valve Index** | OpenXR via Monado | ⚪ |
| **Pico** | OpenXR 1.1 | ⚪ |
| **Varjo** | OpenXR quad-view | 🟣 |
| **Apple Vision Pro** | visionOS | 🟣 |

## ✨ Holographic & 3D

| Device | SDK | Stato |
|---|---|---|
| **Looking Glass Factory** | Core SDK Unity/Unreal | ⚪ |
| **Voxon Photonics** | C++ / Python | ⚪ |
| **HYPERVSN** | Proprietary | 🟣 |

## 🛠️ Maker (Blender + 3D printing)

| Tool | Tipo | Stato |
|---|---|---|
| **Blender bpy** | Python automation | ⚪ |
| **TRELLIS-2** | AI 3D gen self-hosted | ⚪ |
| **SPAR3D** | AI 3D gen self-hosted | ⚪ |
| **TripoSR** | Rapid prototyping | ⚪ |
| **Meshy API** | AI 3D cloud | ⚪ |
| **CSM API** | AI 3D cloud | ⚪ |
| **Klipper + Moonraker** | Stampante | ⚪ |
| **OctoPrint** | Stampante | ⚪ |
| **OctoEverywhere Gadget** | AI failure detection | ⚪ |
| **Bambu Lab** (X1, P1, A1) | MQTT 8883 | ⚪ |
| **PrusaLink / Prusa Connect** | REST | ⚪ |
| **PrusaSlicer / OrcaSlicer** | Slicer CLI | ⚪ |
| **mcp-3D-printer-server** | MCP unification | ⚪ |

## 🔌 Smartwatch & smartphone

| Sistema | Tipo | Stato |
|---|---|---|
| **Apple Watch** | WatchKit | ⚪ |
| **Wear OS** | Pixel/Galaxy Watch | ⚪ |
| **Garmin Connect IQ** | Native app | ⚪ |
| **PineTime + InfiniTime** | BLE bridge | ⚪ |
| **Bangle.js 2** | JS programmable | ⚪ |
| **iOS App Intents** | Siri integration | ⚪ |
| **Android Tasker MCP** | Automation | ⚪ |
| **Termux** | Linux env Android | ⚪ |
| **KDE Connect** | Cross-device sync | ⚪ |

## 🛡️ Identity & auth providers

| Provider | Tipo | Stato |
|---|---|---|
| **Authentik** | OIDC self-hosted | ⚪ |
| **Keycloak** | OIDC enterprise | ⚪ |
| **Authelia** | Lightweight | ⚪ |
| **Zitadel** | Developer-first | ⚪ |
| **Apple Sign In** | OIDC | 🟣 |
| **Google Sign In** | OIDC | 🟣 |
| **GitHub OAuth** | Dev workflow | 🟣 |
| **WebAuthn / Passkey** | FIDO2 | ⚪ |
| **YubiKey 5** | Hardware FIDO2 | ⚪ |
| **TOTP** (Aegis, Authy, 1Password) | RFC 6238 | ⚪ |

## 📨 Email & messaging

| Tipo | Provider | Stato |
|---|---|---|
| Transactional | **Postmark** | ⚪ |
| Transactional | **Resend** | ⚪ |
| Transactional | **AWS SES** | ⚪ |
| Self-hosted | **Postal** | ⚪ |
| Self-hosted | **Mailcow** | 🟣 |
| Push iOS | **APNS** | ⚪ |
| Push Android | **FCM** | ⚪ |
| Notifications self-hosted | **ntfy.sh** | ⚪ |

## 💻 Developer tools

| Tool | Tipo | Stato |
|---|---|---|
| **Cline** (VS Code) | Coding agent | ⚪ |
| **Continue.dev** | Plugin VS Code/JetBrains | ⚪ |
| **Aider** | CLI Git-aware | ⚪ |
| **OpenHands** | Agentic browser UI | 🟣 |
| **Goose** (Block) | CLI + desktop | 🟣 |
| **Claude Code** | CLI Anthropic | ⚪ |
| **GitHub API** | Repo management | ⚪ |
| **GitLab API** | Repo management | 🟣 |
| **Linear** | Issue tracker | 🟣 |
| **Jira Cloud** | Issue tracker | 🟣 |

## 🔧 Infrastructure & DevOps

| Tool | Ruolo | Stato |
|---|---|---|
| **Docker / Compose** | Container | 🟢 |
| **Kubernetes / Helm** | Orchestration | 🟣 |
| **Caddy** | Reverse proxy + TLS | 🟢 |
| **Traefik** | Reverse proxy K8s | ⚪ |
| **Cloudflare Tunnel** | Zero-trust ingress | ⚪ |
| **WireGuard** | VPN mesh | ⚪ |
| **Tailscale** | Managed VPN | ⚪ |
| **HashiCorp Vault** | Secret management | ⚪ |
| **age + sops** | Secret encryption | ⚪ |
| **Prometheus + Grafana** | Metrics | ⚪ |
| **Loki + Promtail** | Logs | ⚪ |
| **OpenTelemetry** | Tracing | ⚪ |
| **Sentry** | Error tracking | ⚪ |
| **Wazuh** | SIEM/XDR | ⚪ |

## 🧬 Standard & protocolli

| Standard | Layer | Stato |
|---|---|---|
| **MCP** (Anthropic) | Agent → Tool | ⚪ |
| **A2A** (Linux Foundation) | Agent → Agent | ⚪ |
| **AG-UI** (CopilotKit) | Agent → UI | 🟣 |
| **OAuth 2.1 + PKCE** | Auth | 🟢 |
| **OIDC** | Auth | ⚪ |
| **WebAuthn / FIDO2** | Auth | ⚪ |
| **JWT ES256** | Token | 🟢 |
| **HL7 FHIR R4/R5** | Health interop | ⚪ |
| **SMART on FHIR** | OAuth + FHIR | ⚪ |
| **OpenXR** | XR cross-vendor | ⚪ |
| **Matter 1.5** | Smart home | ⚪ |
| **Thread 1.4** | IoT mesh | ⚪ |
| **Zigbee 3.0** | IoT | ⚪ |
| **MQTT 5.0** | Pub/sub | ⚪ |
| **WebRTC** | Real-time AV | 🟣 |
| **gRPC** | Service-to-service | 🟣 |
| **GraphQL** | API alternative | 🟣 |

## 🌍 Internazionalizzazione

| Lingua | Stato traduzione |
|---|---|
| Italiano | 🟢 (default) |
| English | 🟢 |
| Español | 🟣 |
| Français | 🟣 |
| Deutsch | 🟣 |
| Português | 🟣 |
| 日本語 (giapponese) | 🟣 |

## ➕ Suggerisci una nuova integrazione

Apri una [discussion](https://github.com/fedcal/open-jarvis/discussions) o issue con label `type:feature` + label `area:integrations`. Le richieste della community popolano la roadmap.

> **Nota:** lo stato è aggiornato in sincrono con la [pagina Stato](../status.md). Se vedi discrepanze, apri PR.
