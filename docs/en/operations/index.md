---
title: "Operations · Open-Jarvis"
description: "Operational guides for deploying, sizing, monitoring and managing Open-Jarvis resources."
---

# Operations

Everything you need to **run Open-Jarvis in production**:

- 🎯 [**Resource management**](resource-management.md) — detailed sizing for every component (FastAPI, Postgres, Redis, Qdrant, Ollama, desktop, mobile) across 4 hardware profiles. Numbers validated with citations.
- 📦 [**Deployment profiles**](profiles.md) — ready-to-use files in `infra/profiles/` for home / vps-small / vps-medium / vps-large.
- 📊 [**Observability stack**](observability.md) — VictoriaMetrics + Grafana + Loki + OpenTelemetry, with privacy guardrails for client telemetry.
- 🔧 [**Sizing calculator**](sizing-calculator.md) — `scripts/sizing.py`: given your hardware, generates optimal config.

## Philosophy

Open-Jarvis is **meant to run anywhere**: from an old laptop in your
bedroom to a production cluster. Profiles are consistent — going from
`home` to `vps-medium` requires no rewrites — and heavy services
(e.g. Ollama) are always **opt-in** via Compose profiles.

## When to consult these guides

| Situation | Go to |
|-----------|-------|
| "How much RAM do I need?" | [resource-management](resource-management.md) |
| "Deploying on a Hetzner CCX13 VPS" | [profiles](profiles.md#vps-small) |
| "Got an alert: what to scrape?" | [observability](observability.md) |
| "I want a custom profile" | [sizing-calculator](sizing-calculator.md) |
| "Local Ollama or cloud?" | [LLM matrix](resource-management.md#5-llm-ollama--cloud) |
| "iOS jetsamming my app: which memory budget?" | [Mobile section](resource-management.md#8-mobile-ionic--capacitor) |
