---
title: Jarvis — Personal AI Infrastructure
description: Un assistente AI personale, open source e self-hosted, in stile Iron Man, che vive su tutti i tuoi dispositivi.
hide:
  - navigation
---

<div class="jarvis-hero" markdown>

# 🤖 Jarvis

**Personal AI Infrastructure**

Un assistente AI personale, open source e self-hosted, in stile Iron Man, che vive su tutti i tuoi dispositivi.

</div>

## Cos'è Jarvis

**Jarvis** è un'infrastruttura AI personale che porta su ogni tuo dispositivo un assistente unico, persistente e contestuale — ispirato al J.A.R.V.I.S. di Iron Man.

Non è un semplice chatbot: è una **rete distribuita di agenti specializzati** che vivono su laptop, smartphone, smartwatch, occhiali smart, visori VR, sistemi olografici e wearable medicali, tutti coordinati da un'identità AI unica e privata.

## Funzionalità chiave

<div class="grid cards" markdown>

- :material-web:{ .lg .middle } **Web search & scraping**

    ---

    Agenti che recuperano, sintetizzano e citano fonti dal web in tempo reale.
    Stack: Crawl4AI, Firecrawl, Jina Reader, ScrapeGraphAI.

- :material-microphone:{ .lg .middle } **Input vocale cross-device**

    ---

    Wake-word, speech-to-text e dialogo naturale su qualsiasi dispositivo.
    Stack: Porcupine, openWakeWord, faster-whisper, Piper TTS.

- :material-glasses:{ .lg .middle } **Realtà aumentata**

    ---

    Overlay informativi su Meta Ray-Ban, XREAL, Brilliant Frame e visori OpenXR.
    Stack: Frame SDK, MentraOS, XREAL SDK.

- :material-virtual-reality:{ .lg .middle } **Realtà virtuale**

    ---

    Interfaccia immersiva su Quest, Valve Index e qualsiasi headset OpenXR.
    Stack: OpenXR, Monado.

- :material-cube-outline:{ .lg .middle } **Display olografici**

    ---

    Integrazione con Looking Glass, Voxon e display volumetrici.
    Stack: Looking Glass Core SDK, Voxon SDK.

- :material-watch:{ .lg .middle } **Wearable medicali**

    ---

    Apple Watch, Wear OS, Garmin, Whoop, Oura — dati biometrici via HealthKit, Health Connect e FHIR.

- :material-brain:{ .lg .middle } **Memoria persistente**

    ---

    La conversazione ti segue da un dispositivo all'altro grazie a mem0, Qdrant, Zep.

- :material-shield-lock:{ .lg .middle } **Privacy by design**

    ---

    Self-hosted, dati sotto il tuo controllo, modelli locali o cloud a tua scelta.

</div>

## Inizia subito

```bash
git clone https://github.com/fedcal/open-jarvis.git
cd open-jarvis
cp .env.example .env
docker compose up -d
```

[Per iniziare :material-arrow-right:](getting-started/index.md){ .md-button .md-button--primary }
[Architettura :material-arrow-right:](architecture/index.md){ .md-button }

## Stato del progetto

!!! warning "Work in progress"
    Stiamo definendo l'architettura e i primi MVP. Cerchiamo contributori — vedi la pagina [Contribuire](contributing/index.md).

## Filosofia

> Il valore non è il chatbot. Il valore reale è una **identità AI persistente che accompagna l'utente su ogni dispositivo**.
