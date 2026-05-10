---
title: "Operations · Open-Jarvis"
description: "Guide operative per il deploy, il sizing, il monitoraggio e l'allocazione delle risorse di Open-Jarvis."
---

# Operations

Tutto quello che serve per **gestire Open-Jarvis in produzione**:

- 🎯 [**Resource management**](resource-management.md) — sizing dettagliato per ogni componente (FastAPI, Postgres, Redis, Qdrant, Ollama, desktop, mobile) su 4 profili hardware. Numeri validati con citazioni alle fonti.
- 📦 [**Profili di deployment**](profiles.md) — file pronti all'uso in `infra/profiles/` per home / vps-small / vps-medium / vps-large.
- 📊 [**Observability stack**](observability.md) — VictoriaMetrics + Grafana + Loki + OpenTelemetry, con privacy guardrails per la telemetria client.
- 🔧 [**Sizing calculator**](sizing-calculator.md) — `scripts/sizing.py`: dato l'hardware, genera config ottimali.

## Filosofia

Open-Jarvis è **pensato per girare ovunque**: dal vecchio laptop in
camera al cluster di produzione. I profili sono coerenti — passare da
`home` a `vps-medium` senza riscrivere niente — e le risorse sono
sempre **opt-in**: nessun servizio pesante (es. Ollama) parte se non
lo abiliti esplicitamente con il `profile: local-llm`.

## Quando consultare queste guide

| Situazione | Vai a |
|-----------|------|
| "Quanta RAM mi serve?" | [resource-management](resource-management.md) |
| "Voglio fare deploy su una VPS Hetzner CCX13" | [profiles](profiles.md#vps-small) |
| "Ho un alert che spara: cosa scrappare?" | [observability](observability.md) |
| "Vorrei un profilo custom" | [sizing-calculator](sizing-calculator.md) |
| "Posso usare Ollama locale o conviene cloud?" | [LLM matrix](resource-management.md#5-llm-ollama--cloud) |
| "iOS taglia l'app: quale memoria?" | [Mobile section](resource-management.md#8-mobile-ionic--capacitor) |
