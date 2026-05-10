---
title: "Observability stack · Open-Jarvis"
description: "Stack di monitoraggio per Open-Jarvis: VictoriaMetrics + Grafana + Loki + OpenTelemetry. Alert Alertmanager, dashboard Grafana, sampling strategy, privacy guardrail per la telemetria client."
keywords: "open-jarvis monitoring, prometheus, victoriametrics, grafana, loki, opentelemetry, alerting, sli slo"
---

# Observability stack

Per gestire una flotta self-hosted (server + desktop + mobile + web)
servono **metriche**, **log** e **trace**. Questa pagina documenta lo
stack consigliato, i budget di risorse e gli alert critici.

!!! info "TL;DR per profilo"
    | Profilo | Stack metriche | Stack log | Tracing |
    |---------|---------------|-----------|---------|
    | **Home** | nessuno (Docker stats sufficient) | `docker logs` + structlog | nessuno |
    | **VPS Small** | VictoriaMetrics single-node | structlog JSON file | OTel SDK head-based 10% |
    | **VPS Medium** | VictoriaMetrics + Grafana | Loki single-tenant | OTel + Tempo |
    | **VPS Large** | VM cluster + Alertmanager | Loki HA | OTel + Tempo + tail sampling |

---

## 1 · Metriche server-side

### Cosa scrappare

| Servizio | Endpoint / exporter | Metriche chiave |
|----------|--------------------|-----------------|
| **FastAPI** | `/metrics` via [`prometheus-fastapi-instrumentator`](https://github.com/trallnag/prometheus-fastapi-instrumentator) | `http_request_duration_seconds` (histogram), `http_requests_total` |
| **PostgreSQL** | `postgres_exporter` → `pg_stat_*` | `pg_stat_replication_lag`, `pg_stat_activity`, `pg_stat_statements` |
| **Redis** | `redis_exporter` → `INFO` | `redis_connected_clients`, `redis_memory_used_bytes` |
| **Qdrant** | `/metrics` nativo (porta 6333, formato OpenMetrics) | collection size, search latency p50/p95 |
| **Ollama** | sidecar `ollama-metrics` (no `/metrics` nativo) | tokens/s, request duration, time-to-first-token |
| **Caddy** | `/metrics` nativo | `caddy_http_requests_total`, latency |

### Prometheus 2.x vs VictoriaMetrics

Per home-lab e fleet sotto 100k serie attive, **VictoriaMetrics
single-node** è il default. Confronto retention 1 mese:

| | Prometheus 2.x | VictoriaMetrics single-node |
|---|---------------|----------------------------|
| RAM (50k serie) | ~512 MB-1 GB | ~200-400 MB |
| RAM (500k serie) | 6-14 GB (spike 23 GB) | ~1 GB stabile |
| CPU sotto carico | 3-4 core | ~2.7 core |
| Disco (50k serie, 1 mese) | 5-15 GB | 2-8 GB |
| Singolo binario | sì | sì |
| Memory cap | nessuno | `-memory.allowedPercent=80` |

**Razionale**: VM usa ~5× meno RAM con compressione disco superiore.

**Fonti**: [Prometheus RAM sizing — Robust Perception](https://www.robustperception.io/how-much-ram-does-prometheus-2-x-need-for-cardinality-and-ingestion/) · [VictoriaMetrics docs](https://docs.victoriametrics.com/victoriametrics/single-server-victoriametrics/) · [Load test VM vs Prometheus](https://zetablogs.medium.com/prometheus-vs-victoria-metrics-load-testing-3fa0cc782912).

### Disciplina cardinalità

- Tieni i valori unici per label sotto **10 per serie**.
- **Mai** mettere user ID, request ID, full URL path come label.
- Usa **histogram nativi** (Prometheus) o `le` bucket allineati ai
  tuoi SLO per la latenza.
- **Exemplar** solo su histogram → linkano sample lenti a trace ID
  senza esplodere serie.

**Fonte**: [Prometheus cardinality guide — Last9](https://last9.io/blog/how-to-manage-high-cardinality-metrics-in-prometheus/) · [native histograms spec](https://prometheus.io/docs/specs/native_histograms/).

---

## 2 · Logging

### Loki vs JSON file + grep

`structlog` con `JSONRenderer` produce ~300-600 byte/riga. Con
compressione Loki snappy (~5-10×):

| Volume raw / giorno | Disco compresso Loki |
|---------------------|---------------------|
| 100 MB | 10-20 MB |
| 1 GB | 100-200 MB |
| 10 GB | 1-2 GB |

**Soglia di scelta**: sotto 500 MB/giorno il JSON file con `logrotate`
+ `jq grep` è più semplice e zero-cost. Sopra, Loki vale la complessità
operativa per la correlazione con i trace ID.

**Fonti**: [Loki storage compression](https://grafana.com/blog/2020/02/19/how-loki-reduces-log-storage/) · [Loki sizing](https://grafana.com/docs/loki/latest/setup/size/).

---

## 3 · Tracing

### OpenTelemetry SDK + Tempo / Jaeger

```python
# server/jarvis_server/telemetry.py
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="otel-collector:4317", insecure=True))
)
FastAPIInstrumentor().instrument_app(app)
```

### Sampling strategies

| Strategia | Costo collector | Quando |
|-----------|----------------|--------|
| **Head-based** (`TraceIdRatioBased`) | zero state, semplice | volumi <1000 RPS, perdita errori accettabile |
| **Tail-based** (OTel collector `tail_sampling` processor) | RAM 100-300 MB per buffer 30 s | quando devi tenere **tutti gli errori** + sampling al 5% del successo |

Per home-lab parti **head-based al 10%** + filter "always keep on
status_code=ERROR" sul collector. Tail sampling è operativamente
pesante.

**Fonti**: [OTel sampling concepts](https://opentelemetry.io/docs/concepts/sampling/) · [Tail sampling — controltheory](https://www.controltheory.com/resources/tail-sampling-with-the-otel-collector/) · [Jaeger vs Tempo](https://stackgen.com/blog/2024/08/09/jaeger-vs-grafana-tempo-a-comprehensive-comparison-for-distributed-tracing).

---

## 4 · Telemetria client (Angular web)

### Privacy guardrails — obbligatori

```typescript
// frontend/web/src/app/core/telemetry.service.ts
import { WebTracerProvider } from '@opentelemetry/sdk-trace-web';
// IMPORTANTE: opt-in gate
if (await this.userPrefs.telemetryEnabled()) {
  // Initialize SDK
}
```

**OTel Collector — Redaction processor** (config side):

```yaml
processors:
  attributes/redact:
    actions:
      - key: http.url
        action: update
        pattern: '\?.*$'
        replacement: '?<redacted>'
      - key: user.email
        action: delete
      - key: user.full_name
        action: delete
      - key: ip.address
        action: update
        pattern: '(\d+\.\d+\.\d+\.)\d+'
        replacement: '$1.0'
```

Cosa raccogliere lato client:
- page navigation timings
- SSE stream start-to-first-token latency
- error span (con stack trace pulito)

Cosa **NON** raccogliere mai:
- contenuto messaggi chat
- query memoria semantica
- email full
- IP completo

**Fonti**: [OTel handling sensitive data](https://opentelemetry.io/docs/security/handling-sensitive-data/) · [Dash0 scrubbing PII](https://www.dash0.com/guides/scrubbing-sensitive-data-with-opentelemetry).

---

## 5 · Alert critici

```yaml
# infra/profiles/<profile>/alertmanager-rules.yml
groups:
  - name: jarvis.critical
    rules:
      - alert: PostgresReplicationLag
        expr: pg_stat_replication_lag_seconds > 10
        for: 5m
        labels: { severity: critical }
        annotations:
          summary: "Replication lag > 10s"

      - alert: DiskFreeBelow20Pct
        expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.20
        for: 10m
        labels: { severity: warning }

      - alert: OllamaDaemonDown
        expr: up{job="ollama-metrics"} == 0
        for: 2m
        labels: { severity: critical }

      - alert: JWTSigningFailureSpike
        expr: rate(auth_jwt_signing_failures_total[5m]) > 0.1
        for: 1m
        labels: { severity: critical }
        annotations:
          summary: "JWT signing failures > 0.1/s — possible key rotation issue"

      - alert: RefreshTokenReuseAttempts
        expr: rate(auth_refresh_token_reuse_total[5m]) > 5
        for: 2m
        labels: { severity: critical }
        annotations:
          summary: "Refresh token reuse > 5/5m — possibile token theft"

      - alert: APIp95LatencyHigh
        expr: histogram_quantile(0.95, sum by (le, handler) (rate(http_request_duration_seconds_bucket[5m]))) > 1
        for: 5m
        labels: { severity: warning }

      - alert: ChatStreamFailureSpike
        expr: rate(http_requests_total{handler="/api/v1/chat",status=~"5.."}[5m]) > 0.5
        for: 3m
        labels: { severity: critical }
```

**Fonte**: [awesome-prometheus-alerts](https://github.com/samber/awesome-prometheus-alerts) · [Crunchy Data — alert PostgreSQL](https://www.crunchydata.com/blog/postgresql-monitoring-for-app-developers-alerts-troubleshooting).

---

## 6 · Dashboard Grafana minima

3 row group, panel parametrici su `$container`, `$route`, `$model`:

**Row 1 — Container resources** (uno per servizio):
- CPU: `rate(container_cpu_usage_seconds_total{name=~"$container"}[1m])`
- Memory RSS: `container_memory_rss{name=~"$container"}`

**Row 2 — API latency** (per route group):
- p50: `histogram_quantile(0.50, sum by (le) (rate(http_request_duration_seconds_bucket{handler=~"$route"}[5m])))`
- p95: idem con 0.95

**Row 3 — LLM throughput**:
- tokens/s per backend: `rate(ollama_tokens_generated_total{model=~"$model"}[1m])`
- TTFT p95: query Tempo client-measured span (linked panel)

JSON skeleton dashboard pronta in
`infra/profiles/<profile>/grafana-dashboard.json`.

**Fonti**: [FastAPI observability dashboard 16110](https://grafana.com/grafana/dashboards/16110-fastapi-observability/) · [blueswen full-stack example](https://github.com/blueswen/fastapi-observability).

---

## Vedi anche

- [Resource management](resource-management.md) — sizing dei singoli
  componenti
- [Profili deployment](profiles.md) — config concreti per profilo
- [Aggiornare Open-Jarvis](../user-manual/updates.md) — alert da
  aggiungere prima e dopo un upgrade
