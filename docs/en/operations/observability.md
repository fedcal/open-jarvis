---
title: "Observability stack · Open-Jarvis"
description: "Monitoring stack for Open-Jarvis: VictoriaMetrics + Grafana + Loki + OpenTelemetry. Alertmanager rules, Grafana dashboards, sampling strategies, privacy guardrails for client telemetry."
---

# Observability stack

For the full content see the [Italian version](../../it/operations/observability.md) — same content, both languages mirror.

## TL;DR per profile

| Profile | Metrics | Logs | Tracing |
|---------|---------|------|---------|
| **Home** | none (Docker stats enough) | `docker logs` + structlog | none |
| **VPS Small** | VictoriaMetrics single-node | structlog JSON file | OTel head-based 10% |
| **VPS Medium** | VictoriaMetrics + Grafana | Loki single-tenant | OTel + Tempo |
| **VPS Large** | VM cluster + Alertmanager | Loki HA | OTel + Tempo + tail sampling |

## What to scrape

| Service | Endpoint | Key metrics |
|---------|----------|-------------|
| FastAPI | `/metrics` via `prometheus-fastapi-instrumentator` | `http_request_duration_seconds`, `http_requests_total` |
| PostgreSQL | `postgres_exporter` | `pg_stat_replication_lag`, `pg_stat_activity` |
| Redis | `redis_exporter` | `redis_connected_clients`, `redis_memory_used_bytes` |
| Qdrant | `/metrics` native (port 6333) | collection size, search latency |
| Ollama | `ollama-metrics` sidecar | tokens/s, time-to-first-token |

## Prometheus 2.x vs VictoriaMetrics

For home-lab fleets under 100k active series, **VictoriaMetrics
single-node** is the default — ~5× less RAM than Prometheus, single
binary, `-retentionPeriod=1m`.

| | Prometheus 2.x | VictoriaMetrics |
|---|---------------|----------------|
| RAM (50k series) | 512 MB-1 GB | 200-400 MB |
| RAM (500k series) | 6-14 GB | ~1 GB |
| Disk (50k, 1mo) | 5-15 GB | 2-8 GB |

## Cardinality discipline

- Keep label cardinality < 10 unique values per metric
- Never use user IDs, request IDs, full URLs as labels
- Use native histograms with SLO-aligned `le` buckets
- Exemplars only on histograms

## Critical alerts

```yaml
groups:
  - name: jarvis.critical
    rules:
      - alert: PostgresReplicationLag
        expr: pg_stat_replication_lag_seconds > 10
        for: 5m

      - alert: OllamaDaemonDown
        expr: up{job="ollama-metrics"} == 0
        for: 2m

      - alert: JWTSigningFailureSpike
        expr: rate(auth_jwt_signing_failures_total[5m]) > 0.1

      - alert: RefreshTokenReuseAttempts
        expr: rate(auth_refresh_token_reuse_total[5m]) > 5
        annotations:
          summary: "Possible token theft"
```

## Client-side telemetry — privacy guardrails (mandatory)

```yaml
# OTel Collector config
processors:
  attributes/redact:
    actions:
      - key: http.url
        pattern: '\?.*$'
        replacement: '?<redacted>'
        action: update
      - key: user.email
        action: delete
      - key: ip.address
        pattern: '(\d+\.\d+\.\d+\.)\d+'
        replacement: '$1.0'
        action: update
```

**Never** collect: chat content, memory queries, full email, full IP.
**Always** opt-in gate before SDK init.

## Sources

- [Prometheus RAM sizing](https://www.robustperception.io/how-much-ram-does-prometheus-2-x-need-for-cardinality-and-ingestion/)
- [VictoriaMetrics docs](https://docs.victoriametrics.com/victoriametrics/single-server-victoriametrics/)
- [OTel sampling concepts](https://opentelemetry.io/docs/concepts/sampling/)
- [OTel sensitive data handling](https://opentelemetry.io/docs/security/handling-sensitive-data/)
- [awesome-prometheus-alerts](https://github.com/samber/awesome-prometheus-alerts)
- [FastAPI observability dashboard](https://grafana.com/grafana/dashboards/16110-fastapi-observability/)
