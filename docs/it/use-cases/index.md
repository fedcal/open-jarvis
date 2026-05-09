---
title: "Casi d'uso · 20 declinazioni di Open-Jarvis"
description: "Open-Jarvis non è solo per uso personale: scuola, azienda, sanità, governo, NGO, ricerca, makerspace, agritech, marittimo, musei. Tutte le declinazioni in cui si può usare."
keywords: "use cases, personal AI, enterprise, education, healthcare, government, NGO, research lab, makerspace, agritech"
---

# Casi d'uso di Open-Jarvis

> Open-Jarvis non è un chatbot. È un'**infrastruttura AI personale** che si adatta a qualsiasi contesto, da una singola persona a un'organizzazione complessa. **Nessun dato lascia la tua infrastruttura senza il tuo consenso esplicito**, e il software è **sempre gratuito e AGPL-3.0**.

## 1. 🏠 Personal — Il caso base

**Esempio.** Davide, sviluppatore freelance, vuole un assistente che conosca i suoi progetti e abitudini, senza che alcun dato attraversi server di terze parti.

- **Setup**: Docker Compose su laptop o Raspberry Pi 5 / mini-PC x86
- **LLM**: Ollama (Llama 3.1 8B, Gemma 3 leggero, Mistral 24B reasoning)
- **Memory**: mem0 + Qdrant locale
- **Voice**: openWakeWord + faster-whisper + Piper
- **Plugin**: CalDAV, Todoist, filesystem agent, Crawl4AI, Nextcloud
- **Privacy**: zero cloud obbligatorio, GDPR by design (utente = titolare)

## 2. 👨‍👩‍👧 Family / Household

**Esempio.** Famiglia Rossi, 4 membri (2 genitori + 2 figli 10 e 14 anni).

- **Multi-utente** profili isolati con memoria separata
- **RBAC**: `parent` (full access) vs `child` (filtri content age-gated)
- **Shared KB**: calendario familiare, ricette, contatti emergenza, lista spesa
- **Parental dashboard**: monitor query minori, limiti orari
- **Plugin**: CalDAV condiviso, Open Food Facts, geofencing, alert scuola, Grocy
- **Privacy**: GDPR Art. 8 (dati minori non escono dalla rete domestica)

## 3. 🚀 Small team / Startup (< 20 persone)

**Esempio.** Startup 8 persone distribuita Milano-Berlino-Lisbona.

- **Setup**: VPS privato (Hetzner, Scaleway, OVH), Docker Compose o k3s
- **Auth**: OIDC (Authentik / Authelia), no SAML enterprise
- **Shared KB**: docs, runbook, ADR
- **Bot bridge**: Slack/Discord via webhook + MCP
- **Memory scope**: org separato da user
- **Plugin**: GitHub/GitLab, Notion/Confluence, Linear/Jira, Loom transcripts, timezone scheduling
- **Privacy**: VPS privato, no vendor lock-in

## 4. 🏢 Enterprise / Corporate

Vedi pagina dedicata: [Enterprise architecture](../enterprise/architecture.md).

> Il codice è lo stesso, AGPL-3.0. La differenza è solo nella configurazione (SAML, SCIM, multi-tenant, compliance).

## 5. 🎓 Education

### 5a. Scuole K-12

**Esempio.** Istituto comprensivo per studenti 6-14 anni.

- **Profili per fascia età** con content filter progressivo (whitelist curricolari)
- **Consent workflow** GDPR Art. 8 + COPPA (per studenti internazionali)
- **Dashboard docenti** revisione sessioni anonimizzate
- **Deploy on-premise** rete scolastica
- **Plugin**: Wikipedia semplificata, Anki flashcard, KhanAcademy, geometria interattiva, MathJax
- **Compliance**: GDPR minori, COPPA (FTC 2025), FERPA (USA), KCSIE 2025 (UK)

### 5b. Università / academia

**Esempio.** Ricercatrice dottorato bioinformatica.

- **Zotero integration** (plugin llm-for-zotero / ARIA)
- **Jupyter AI** per assistenza inline
- **MathJax + LaTeX** rendering
- **RAG su PDF paper** (Firecrawl + Qdrant)
- **Citazione obbligatoria** delle fonti
- **Plugin**: Zotero, Jupyter AI, arXiv MCP, OpenAlex, Semantic Scholar, Mendeley, LaTeX
- **Compliance**: paper non pubblicati restano locali; conformità AI policy Nature/Science

### 5c. Lifelong learning

- **Anki integration** spaced repetition
- **Profilo apprendimento** lacune tracciate
- **Tutor socratico**: domande prima di dare soluzioni
- **Multilingua** target language

## 6. 🏥 Healthcare

### 6a. Paziente individuale

**Esempio.** Elena, 68 anni, diabetica, vuole tracciare CGM Dexcom + cartella clinica personale.

- **Medical agent + HAPI FHIR R4**
- **Dexcom CGM + Oura Ring** real-time
- **Alert configurabili** smartphone + smartwatch
- **Export FHIR** per medico curante
- **Privacy**: dati on-device o self-hosted, formato FHIR portabile

### 6b. Studio medico singolo

**Esempio.** Medico medicina generale, 1200 pazienti.

- **FHIR MCP Server** (Momentum) + OpenEMR / Open Hospital
- **RAG** linee guida cliniche / farmacologiche
- **Triage agent** classifica urgenze
- **Pseudonimizzazione automatica** nei log
- **Compliance**: GDPR Art. 9 dati sanitari, deploy on-premise obbligatorio, no LLM cloud per dati paziente

### 6c. Casa di riposo / RSA

**Esempio.** RSA 80 ospiti.

- **Hub IoT** (Home Assistant) aggrega wearable + sensori caduta
- **Alert medico** soglie HR / SpO2 / inattività
- **Interfaccia voice-first** per staff
- **Portale famiglia** accesso limitato
- **Plugin**: Home Assistant, FHIR, turni infermieri, push staff, comunicazione famiglia

## 7. 🏛️ Government / Public sector

**Esempio Comune.** Comune 15.000 abitanti.

- **KB su atti comunali** auto-aggiornati via Crawl4AI
- **Multi-canale**: web, Telegram, WhatsApp opzionale
- **Escalation umana** per richieste complesse
- **Deploy cloud PA qualificato AgID** o on-premise

**Forze dell'ordine.** Deploy air-gapped, KB normativa, modello LLM completamente locale.

- **Plugin**: Crawl4AI auto-aggiornamento atti, modulistica PDF, FAQ engine, PEC integration
- **Compliance**: EU AI Act ("rischio limitato" — trasparenza obbligatoria), AgID Guidelines (IT), FedRAMP-equivalent (US), AI Act art. obbligo alfabetizzazione AI dal feb 2025

## 8. ❤️ NGO / Non-profit

**Esempio.** ONG umanitaria, 200 volontari in 12 paesi, supporto rifugiati.

- **Multi-tenant per paese** sync selettivo verso coordinamento
- **Traduzione locale** NLLB-200 (Meta, MIT) per 200 lingue
- **KB casi sociali** con pseudonimizzazione obbligatoria
- **Coordinamento volontari** scheduling, task, availability
- **Plugin**: NLLB-200, Signal/WhatsApp bridge, scheduling, Nextcloud, anonimizzazione
- **Privacy**: dati beneficiari extremely sensitive, mai cloud USA per refugees

## 9. 🔬 Research labs

**Esempio.** Laboratorio fisica computazionale, 15 ricercatori.

- **RAG corpus scientifico** (paper interni, preprint, dataset)
- **Jupyter AI** assistenza inline
- **Citazione obbligatoria** (paper, DOI, notebook, dataset version)
- **Git tracking** per riproducibilità
- **API federata** cross-institute via OAuth2
- **Plugin**: Jupyter AI, arXiv/OpenAlex MCP, Zotero, DVC, Semantic Scholar, LaTeX, GitHub

## 10. 🛠️ Makerspace / Fab Lab

**Esempio.** Makerspace 80 membri, condivisione 3D printer / laser / CNC.

- **Plugin prenotazione** macchinari (CalDAV)
- **KB tecnica** per ogni macchinario
- **Accountability** sessioni loggate (utente, durata, materiali)
- **Alert manutenzione** ore d'uso
- **Voice in officina** noise-robust faster-whisper
- **Plugin**: CalDAV booking, Home Assistant stato, inventory, wiki tecnica

## 11. 🎨 Content creator / Solopreneur

**Esempio.** Giulia, podcast settimanale + blog + YouTube.

- **Pipeline audio**: faster-whisper → LLM (show notes, titoli)
- **RAG archivio personale** evita ripetizioni
- **Social scheduler** orari ottimali
- **Email management** classificazione + risposte
- **Plugin**: faster-whisper, RSS, Crawl4AI trend, Buffer/Hootsuite, SEO, YouTube Data API, Notion CMS

## 12. 💻 Developer team open source

**Esempio.** Progetto OS 3 maintainer + 400 contributor.

- **GitHub/GitLab webhook** triage issue
- **Release notes generation** automatica
- **Doc diff**: codice cambia → propone update doc
- **Plugin**: GitHub MCP, GitLab API, semver, MkDocs/Sphinx, coverage report, Discord/Slack bridge

## 13. 🏢 Co-working space

- **Booking desk + sale**: CalDAV + interfaccia conversazionale
- **Directory membri** matching competenze (opt-in)
- **FAQ bot** Slack/Discord community
- **Plugin**: CalDAV, Stripe membership, Home Assistant accessi IoT

## 14. 🕊️ Religious / Spiritual

**Esempio.** Parrocchia + comunità.

- **KB testi religiosi** (Bibbia, Corano, Talmud, buddist — pubblico dominio)
- **Calendario liturgico** CalDAV
- **Modalità ascolto** con disclaimer esplicito ("non sostituisce counseling umano")
- **Multilingua** comunità diasporiche
- **Compliance**: EU AI Act trasparenza obbligatoria

## 15. ⚽ Sports team

**Esempio.** Società ciclismo amatoriale 30 atleti.

- **Garmin/Polar/Strava** dati allenamento
- **Analisi carico/recupero** per atleta
- **Plugin tattica** GPX gara
- **Logistica gare** condivisa
- **Plugin**: Garmin, Strava, Oura, plugin W/kg TSS, CalDAV
- **Privacy**: consenso individuale, aggregati anonimi per team

## 16. ⚖️ Studio legale (piccolo)

**Esempio.** Studio 4 avvocati + 2 praticanti.

- **RAG giurisprudenza** (DeJure, EUR-Lex, Cassazione open)
- **Drafting assistito** (revisione umana obbligatoria)
- **Time tracking** + fatturazione
- **Scadenze processuali** alert multipli
- **Deploy completamente on-premise** (segreto professionale art. 622 c.p.)
- **Plugin**: EUR-Lex scraper, DeJure, generazione atti, time tracker, Suzie Law open framework

## 17. 🌾 Smart farming / Agritech

**Esempio.** Azienda agricola 200 ettari.

- **Hub IoT** ThingsBoard (open) o Home Assistant
- **Query naturale** dati IoT ("umidità campo B ultimi 3 giorni")
- **KB agronomica** (EPPO database)
- **Alert anomalie** (siccità, gelo, fitopatie)
- **Manutenzione macchinari**
- **Plugin**: ThingsBoard, Home Assistant, EPPO, Meteostat, parco macchine, tracciabilità (blockchain-ready)

## 18. 🚗 Autonomous vehicle / In-car AI

**Esempio.** Appassionato auto custom AI offline.

- **Hardware**: Raspberry Pi 5 / NVIDIA Jetson Orin in auto
- **Voice-first sempre offline**: Porcupine + faster-whisper + Piper
- **OsmAnd offline** maps
- **OTA update** quando in WiFi domestico
- **Bridge sperimentale** Android Auto / CarPlay
- **Privacy**: zero cloud durante guida

## 19. ⛵ Maritime / boats

**Esempio.** Ketch a vela 14 metri.

- **Mini-PC nautico** + iridium/SSB per ocean
- **Mesh WiFi** equipaggio
- **NMEA 2000** vento, profondità, motori
- **KB normativa** doganale/sanitaria portuale
- **Cartografia OpenSeaMap + Grib** offline
- **Plugin**: OpenCPN, NMEA 2000 bridge, Grib2, normativa portuale, log automatico, Iridium messaging

## 20. 🏛️ Musei / cultura

**Esempio.** Museo arte moderna 50.000 visitatori/anno.

- **KB collezione** schede opere, biografie, contesto
- **Multilingua** NLLB-200 per 20+ lingue
- **App mobile PWA + totem touch + QR per opera**
- **Backend on-premise** GDPR visitor analytics
- **ReInHerit toolkit** (H2020) per musei EU
- **Plugin**: Wikidata/Europeana metadati aperti, QR scanner, audio guide, Coqui TTS multilingua

## 📊 Matrice di decisione

| Criterio | Personal | Family | Small Team | Enterprise | K-12 | Healthcare | Gov/NGO | Research |
|---|---|---|---|---|---|---|---|---|
| **Utenti** | 1 | 2-6 | 5-20 | 20+ | 50-1000+ | 1-500+ | 10-10K+ | 5-50 |
| **Dati sensibili** | Bassi | Medi | Medi | Alti | Alti (minori) | Molto alti | Alti | Medi-Alti |
| **Internet** | No | No | Opz. | Opz. | No | No | No | Opz. |
| **Budget IT** | Zero | Zero | Basso | Medio | Basso | Medio | Basso-Medio | Basso |
| **Expertise IT** | Media | Bassa | Media | Alta | Bassa | Bassa | Bassa | Alta |
| **Auth** | Locale | RBAC | OIDC | SAML+LDAP | RBAC ruolo | RBAC+Audit | OIDC/SAML | OIDC |
| **LLM** | Ollama | Ollama | Ollama/ibrido | On-prem dedicato | Ollama | On-prem obbligatorio | On-prem | Ollama/ibrido |
| **Memory scope** | user | user+family | user+org | org+dept | user+class | user+clinician | user+org | user+lab |
| **Compliance** | GDPR | GDPR minori | GDPR | NIS2+GDPR | COPPA/Art.8 | GDPR Art.9/HIPAA | EU AI Act/AgID | GDPR+integ. AI |
| **Plugin core** | Calendar, Files | Calendar, Parental | KB, Chat bridge | SSO, Audit, RBAC | Filter, Anki | FHIR, Alert | RAG normativa | Jupyter, Zotero |

### Guida rapida

| Domanda | Profilo |
|---|---|
| 1 utente, privacy assoluta? | **Personal** — 1 ora con Docker Compose |
| Famiglia con bambini? | **Family** + RBAC genitori |
| Startup < 20? | **Small team** + Authentik OIDC |
| Dati sanitari/legali? | **On-premise obbligatorio** |
| Scuola/università? | **Education** (consenso + citazioni) |
| Ente pubblico EU? | **Government** + AI Act + AgID |
| Zero connessione internet? | **Air-gapped** (tutti i profili supportati) |
| Niente team IT? | **Personal/Family** — installer one-command |

---

> Open-Jarvis è costruito sul principio che l'**AI potente non debba essere un privilegio di chi può pagare abbonamenti cloud**. Dal privato cittadino al laboratorio scientifico, dal makerspace al comune di montagna: l'infrastruttura è la stessa, la libertà è la stessa, il codice è sempre **AGPL-3.0**.

## Riferimenti

- [Leon AI](https://getleon.ai/)
- [Vellum 8 Best Open-Source Personal AI Assistants](https://www.vellum.ai/blog/best-open-source-personal-ai-assistants)
- [Keycloak](https://www.keycloak.org/) e [Authelia](https://www.authelia.com/)
- [SchoolAI FERPA/COPPA](https://schoolai.com/blog/ensuring-ferpa-coppa-compliance-school-ai-infrastructure)
- [FHIR MCP Server Momentum](https://www.themomentum.ai/blog/introducing-fhir-mcp-server-natural-language-interface-for-healthcare-data)
- [EU AI Act](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)
- [Jupyter AI](https://github.com/jupyterlab/jupyter-ai)
- [ReInHerit Museum Toolkit](https://www.mdpi.com/2571-9408/8/7/277)
- [Suzie Law open source](https://www.artificiallawyer.com/2026/05/07/scissero-launches-suzie-law-open-source-ai-assistant/)
