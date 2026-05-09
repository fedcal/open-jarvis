---
title: "Open-Jarvis · Iron Man-style open-source personal AI assistant"
description: "Open-Jarvis is an open-source, self-hosted personal AI assistant inspired by Iron Man's J.A.R.V.I.S. that lives across laptops, smartphones, smartwatches, AR glasses, VR headsets, holographic displays and medical wearables. Privacy by design, MIT licensed, multilingual."
keywords: "personal AI assistant, open source, self-hosted, Jarvis, Iron Man, private AI, specialised agents, LangGraph, personal RAG, smart home, medical wearables, AR VR holographic, multilingual"
hide:
  - navigation
---

<div class="jarvis-hero" markdown>

# 🤖 Jarvis

**Personal AI Infrastructure**

An open-source, self-hosted, Iron Man-style personal AI assistant living across all your devices.

</div>

## What is Jarvis

**Jarvis** is a personal AI infrastructure that brings a unique, persistent and context-aware assistant to every device you own — inspired by Iron Man's J.A.R.V.I.S.

It's not just a chatbot: it's a **distributed network of specialised agents** living on laptops, smartphones, smartwatches, smart glasses, VR headsets, holographic displays and medical wearables, all coordinated by a single private AI identity.

## Key features

<div class="grid cards" markdown>

- :material-web:{ .lg .middle } **Web search & scraping**

    ---

    Agents that fetch, summarise and cite web sources in real time.
    Stack: Crawl4AI, Firecrawl, Jina Reader, ScrapeGraphAI.

- :material-microphone:{ .lg .middle } **Cross-device voice**

    ---

    Wake-word, speech-to-text and natural dialogue on any device.
    Stack: Porcupine, openWakeWord, faster-whisper, Piper TTS.

- :material-glasses:{ .lg .middle } **Augmented reality**

    ---

    Informational overlays on Meta Ray-Ban, XREAL, Brilliant Frame and OpenXR headsets.
    Stack: Frame SDK, MentraOS, XREAL SDK.

- :material-virtual-reality:{ .lg .middle } **Virtual reality**

    ---

    Immersive interface on Quest, Valve Index and any OpenXR-compatible headset.
    Stack: OpenXR, Monado.

- :material-cube-outline:{ .lg .middle } **Holographic displays**

    ---

    Integration with Looking Glass, Voxon and volumetric displays.
    Stack: Looking Glass Core SDK, Voxon SDK.

- :material-watch:{ .lg .middle } **Medical wearables**

    ---

    Apple Watch, Wear OS, Garmin, Whoop, Oura — biometric data via HealthKit, Health Connect and FHIR.

- :material-brain:{ .lg .middle } **Persistent memory**

    ---

    The conversation follows you across devices thanks to mem0, Qdrant, Zep.

- :material-shield-lock:{ .lg .middle } **Privacy by design**

    ---

    Self-hosted, data under your control, local or cloud models at your choice.

</div>

## Quick start

```bash
git clone https://github.com/fedcal/open-jarvis.git
cd open-jarvis
cp .env.example .env
docker compose up -d
```

[Getting started :material-arrow-right:](getting-started/index.md){ .md-button .md-button--primary }
[Architecture :material-arrow-right:](architecture/index.md){ .md-button }

## Project status

!!! warning "Work in progress"
    We are defining the architecture and the first MVPs. We are looking for contributors — see the [Contributing](contributing/index.md) page.

## Philosophy

> The value is not the chatbot. The real value is a **persistent AI identity that follows the user across every device**.
