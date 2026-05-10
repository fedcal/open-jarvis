---
title: "Resource management · Open-Jarvis"
description: "Hardware resource allocation for FastAPI server, Postgres, Redis, Qdrant, Ollama, Tauri desktop and Ionic mobile clients. 4 deployment profiles (home, VPS small/medium/large) with validated values and source citations."
keywords: "open-jarvis sizing, capacity planning, fastapi workers, postgresql tuning, redis maxmemory, qdrant ram, ollama vram, ionic memory, tauri footprint"
---

# Resource management · Open-Jarvis

Operational guide for sizing every Open-Jarvis component. All numbers
are backed by official documentation (Apple, Android, PostgreSQL,
Qdrant, llama.cpp, Tauri, OpenTelemetry) — links at the end of each
section let you verify and dig deeper.

!!! info "TL;DR — the 4 profiles"
    | Profile | Hardware | Users | Recommended LLM | When |
    |---------|----------|-------|-----------------|------|
    | **Home** | Home PC, 16-32 GB, no GPU | 1 | `llama3.2:3b` (Q4_K_M) or cloud | dev, demo, personal |
    | **VPS Small** | 2 vCPU, 4-8 GB | 1 | cloud only (Anthropic Haiku, GPT-4o-mini) | personal always-on |
    | **VPS Medium** | 4 vCPU, 16 GB | family of 4-5 | cloud + optional `llama3.2:3b` | family |
    | **VPS Large** | 8 vCPU, 32 GB, opt. GPU | team 10-20 | `qwen2.5:14b` Q4 + cloud | small team |

---

## 1 · FastAPI backend

### Worker count

Gunicorn rule: **`(2 × CPU) + 1`**. But for a **purely async** FastAPI
app (asyncpg, async SQLAlchemy) a single worker can saturate a small
VPS — extra workers only help with blocking sync code or for
process-level isolation.

| Profile | CPU | Formula | **Async recommended** | RAM/worker |
|---------|-----|---------|----------------------|-----------|
| Home | 8-16 | 17-33 | **2-4** | 150-300 MB |
| VPS Small | 2 | 5 | **2-3** | 150-300 MB |
| VPS Medium | 4 | 9 | **4-6** | 150-300 MB |
| VPS Large | 8 | 17 | **8-12** | 150-300 MB |

!!! warning "JWT keypair single-worker in dev"
    Without `JARVIS_JWT_*_KEY_PEM` each worker rolls its own ephemeral
    ES256 keypair, breaking JWT verification. Use `--workers 1` in
    dev. See [Server runtime troubleshooting](../troubleshooting/server-runtime.md#signature-verification-failed).

**Sources**: [Gunicorn Design](https://gunicorn.org/design/) · [FastAPI deployment](https://fastapi.tiangolo.com/deployment/server-workers/) · [Sentry — uvicorn workers](https://sentry.io/answers/number-of-uvicorn-workers-needed-in-production/).

### SQLAlchemy connection pool

Each worker opens its own pool. Real Postgres connections are
`workers × (pool_size + max_overflow)` and **must stay** below
Postgres `max_connections`.

| Profile | Workers | `pool_size` | `max_overflow` | Total conns | PG `max_connections` |
|---------|---------|-------------|---------------|------------|---------------------|
| Home | 3 | 5 | 10 | 45 | 50 |
| VPS Small | 2 | 3 | 5 | 16 | 25 |
| VPS Medium | 5 | 5 | 10 | 75 | 100 |
| VPS Large | 10 | 5 | 10 | 150 | 200 |

For VPS Large consider **PgBouncer** (transaction pooling) →
multiplexes 150 clients onto 10-20 real Postgres connections.

**Sources**: [SQLAlchemy pooling](https://docs.sqlalchemy.org/en/20/core/pooling.html).

---

## 2 · PostgreSQL 16

[pgtune](https://pgtune.leopard.in.ua/) heuristics for "Web Application":

| Parameter | Rule | Note |
|-----------|------|------|
| `shared_buffers` | 25% of dedicated RAM | cap at 8 GB on Linux |
| `effective_cache_size` | 75% of dedicated RAM | planner hint only |
| `work_mem` | `(RAM × 0.25) / max_connections` | per sort node, can multiply |
| `maintenance_work_mem` | 5% RAM, max 2 GB | only during VACUUM/REINDEX |
| `max_connections` | keep low, pool app-side | each idle conn ~5-10 MB |
| `wal_buffers` | `shared_buffers / 32`, max 16 MB | auto if `-1` |
| `random_page_cost` | **1.1 on SSD/NVMe**, 4.0 on HDD | critical on SSD |
| `checkpoint_completion_target` | 0.9 | spreads I/O over 90% interval |

### Per-profile values

Assuming Postgres has exclusive access to the listed RAM (for
co-located deployments, reduce by 40-50%):

| Param | Home (PG 8 GB) | VPS Small (PG 2 GB) | VPS Medium (PG 6 GB) | VPS Large (PG 16 GB) |
|-------|---------------|--------------------|---------------------|---------------------|
| `shared_buffers` | `2GB` | `512MB` | `1536MB` | `4GB` |
| `effective_cache_size` | `6GB` | `1536MB` | `4608MB` | `12GB` |
| `work_mem` | `32MB` | `8MB` | `16MB` | `32MB` |
| `maintenance_work_mem` | `512MB` | `128MB` | `384MB` | `1GB` |
| `max_connections` | `50` | `25` | `100` | `200` |
| `wal_buffers` | `16MB` | `8MB` | `16MB` | `16MB` |
| `random_page_cost` | `1.1` | `1.1` | `1.1` | `1.1` |

Ready files in `infra/profiles/<profile>/postgresql.conf`.

**Sources**: [pgtune.leopard.in.ua](https://pgtune.leopard.in.ua/) · [PostgreSQL Tuning Wiki](https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server) · [Crunchy Data tuning](https://www.crunchydata.com/blog/optimize-postgresql-server-performance) · [EnterpriseDB memory](https://www.enterprisedb.com/postgres-tutorials/how-tune-postgresql-memory).

---

## 3 · Redis 7

Open-Jarvis uses Redis only for **ephemeral data with explicit TTL**
(rate limits, MFA challenges, sessions). Eviction policy: **`volatile-lru`**.

```ini
# redis.conf
maxmemory 256mb
maxmemory-policy volatile-lru
maxmemory-samples 10
```

| Profile | `maxmemory` | Rationale |
|---------|-------------|-----------|
| Home | 256 MB | Generous |
| VPS Small | 128 MB | Leaves room for Postgres + app |
| VPS Medium | 256 MB | Family of 5 |
| VPS Large | 512 MB | Spike headroom |

**Sources**: [Redis eviction policies](https://redis.io/docs/latest/develop/reference/eviction/).

---

## 4 · Qdrant — vector store

```
RAM (bytes) = num_vectors × dimension × 4 × 1.5
```

`1.5×` covers HNSW graph + metadata.

### Quantization (recommended)

Best-practice production: keep float32 vectors **on-disk**, only
quantized in RAM. Qdrant re-scores top-K from disk.

| Profile | float32 | int8 (4× compress) | binary (32×, ≥1024 dim only) |
|---------|---------|-------------------|---------------------------|
| 100K × 384 dim | 216 MB | 54 MB | not recommended |
| 500K × 384 dim | 1.1 GB | 274 MB | not recommended |
| 1M × 384 dim | 2.2 GB | 540 MB | not recommended |
| 1M × 1024 dim | 5.8 GB | 1.4 GB | 180 MB |

**Open-Jarvis default**: int8 scalar quantization at 384 dim. Under
300 MB even at 500K user memories.

**Sources**: [Qdrant capacity planning](https://qdrant.tech/documentation/guides/capacity-planning/) · [scalar quantization](https://qdrant.tech/articles/scalar-quantization/).

---

## 5 · LLM (Ollama / cloud)

### RAM/VRAM matrix (Q4_K_M)

| Model | Params | Q4_K_M file | Inf RAM 4k ctx | Inf RAM 8k ctx | Full-GPU VRAM |
|-------|--------|-------------|----------------|----------------|---------------|
| llama3.2:1b | 1.2 B | 0.75 GB | 1.3 GB | 1.5 GB | 2 GB |
| llama3.2:3b | 3.2 B | 1.9 GB | 2.6 GB | 2.9 GB | 4 GB |
| qwen2.5:7b | 7.6 B | 4.4 GB | 5.2 GB | 5.8 GB | 8 GB |
| llama3.1:8b | 8 B | 4.7 GB | 5.5 GB | 6.2 GB | 8 GB |
| qwen2.5:14b | 14.7 B | 8.9 GB | 10.0 GB | 11.0 GB | 12 GB |
| mixtral:8x7b | 46.7 B | 26.5 GB | 27.5 GB | 28.5 GB | 32 GB (2×16) |
| llama3.3:70b | 70 B | 42.5 GB | 43.5 GB | 45.6 GB | 48 GB (2×24) |

**Q4_K_M** is the default: ~0.5% perplexity loss vs F16, **4× less RAM**.

### Throughput (tokens/s, 7B Q4_K_M)

| Hardware | tok/s |
|----------|-------|
| Ryzen 7 5800X CPU only | 5-9 |
| Apple M2 Pro (Metal) | ~38 |
| Apple M3 Max (Metal) | ~66 |
| RTX 4060 8 GB | 55-65 |
| RTX 4090 24 GB | 150-188 |
| A100 80 GB (vLLM) | 400-600 |

### Recommended LLM per profile

| Profile | Local | Cloud fallback |
|---------|-------|----------------|
| Home | `llama3.2:3b` Q4_K_M | `claude-haiku-4-5-20251001` |
| VPS Small | none | **cloud only** |
| VPS Medium | `llama3.2:3b` opt. | `claude-haiku-4-5` for complex tasks |
| VPS Large | `qwen2.5:14b` Q4 (12 GB VRAM) | `claude-sonnet-4-6` for reasoning |

### Ollama concurrency

Default Ollama serializes requests. For multi-user:

```bash
OLLAMA_NUM_PARALLEL=4 ollama serve
```

KV-cache cost is **multiplicative**: `KV × NUM_PARALLEL`.

### Embedder

| Model | Params | RAM | Dim | Lang | tok/s CPU |
|-------|--------|-----|-----|------|-----------|
| all-MiniLM-L6-v2 | 22 M | 50 MB | 384 | EN | 600-1000 |
| nomic-embed-text-v1.5 | 137 M | 300 MB | 768/512 | EN-first | 150-300 |
| mxbai-embed-large | 335 M | 700 MB | 1024 | EN-first | 80-150 |
| **BGE-M3** | 570 M | 1.2 GB | 1024 | **100+** | 40-80 |

### Cloud vs local cost

| Provider | Input $/1k | Output $/1k |
|----------|-----------|-------------|
| Anthropic Claude Haiku 4.5 | 0.0010 | 0.0050 |
| OpenAI GPT-4o mini | 0.00015 | 0.00060 |
| Groq Llama-3.3-70B | 0.00059 | 0.00079 |
| Local Ryzen 9 (electricity) | ~0.0000004 | ~0.0000004 |

**Sources**: [llama.cpp memory math](https://github.com/ggml-org/llama.cpp/discussions/3847) · [Ollama PR #3418](https://github.com/ollama/ollama/pull/3418).

---

## 6 · Docker Compose `deploy.resources`

Docker enforces limits via **cgroups v2** (Linux 5.10+).

### Home (16 GB)

```yaml
services:
  server:
    deploy:
      resources:
        limits:       { cpus: "2.0", memory: "1G" }
        reservations: { cpus: "0.5", memory: "512M" }
  postgres:
    deploy:
      resources:
        limits:       { cpus: "4.0", memory: "4G" }
  redis:
    deploy:
      resources:
        limits:       { cpus: "0.5", memory: "384M" }
  qdrant:
    deploy:
      resources:
        limits:       { cpus: "2.0", memory: "2G" }
```

### Other profiles

| Profile | server | postgres | redis | qdrant |
|---------|--------|----------|-------|--------|
| **VPS Small** (2 vCPU, 4 GB) | 1.0/512M | 1.0/1.5G | 0.25/192M | 0.5/512M |
| **VPS Medium** (4 vCPU, 16 GB) | 2.0/2G | 2.0/6G | 0.5/384M | 1.0/2G |
| **VPS Large** (8 vCPU, 32 GB) | 4.0/4G | 4.0/16G | 1.0/768M | 2.0/6G |

Ready files: `infra/profiles/<profile>/docker-compose.override.yml`.

**Sources**: [Docker resource constraints](https://docs.docker.com/engine/containers/resource_constraints/).

---

## 7 · Desktop client

### Tauri 2 vs alternatives

| Metric | **Tauri 2** | Electron 31 | PWA | Native |
|--------|------------|------------|-----|--------|
| Bundle | 3-10 MB | 50-150 MB | <1 MB | 5-30 MB |
| RSS idle | 20-80 MB | 100-300 MB | shared | 15-60 MB |
| RSS chat SSE | 40-150 MB | 200-500 MB | +10-30 MB | 30-100 MB |
| Cold start | 200-500 ms | 1000-2000 ms | ~0 | 100-400 ms |

**Open-Jarvis chose Tauri 2** for the desktop client: ~5× less RAM
than Electron, deny-by-default per-window capabilities, single
`tauri-action` CI pipeline distributes `.dmg`/`.msi`/`.AppImage`/etc.

**Sources**: [Tauri 2 release](https://v2.tauri.app/blog/tauri-20/) · [pkgpulse Electron vs Tauri](https://www.pkgpulse.com/blog/electron-vs-tauri-2026).

---

## 8 · Mobile (Ionic + Capacitor)

### iOS — Jetsam high-water mark

iOS terminates processes when `task_vm_info.phys_footprint` exceeds
the HWM. **Never measure with `resident_size`** — only `phys_footprint`.

| Device | Total RAM | Jetsam HWM (~) |
|--------|-----------|----------------|
| iPhone X | 3 GB | 1.6-1.8 GB |
| iPhone 12/13 | 4 GB | ~2.1 GB |
| iPhone 14 Pro / 15 Pro | 8 GB | ~3.5-4 GB |

For heavy ML request the **Increased Memory Limit entitlement**.

### Android — heap caps

| Device tier | `heapgrowthlimit` | `largeHeap=true` |
|-------------|-------------------|------------------|
| 3-4 GB | 192-256 MB | 512 MB |
| 6-8 GB | 256-384 MB | 512-768 MB |
| 12 GB+ flagship | 384 MB | 1 GB |

`largeHeap` is discouraged in production.

### Background execution

| Platform | Keep wake-word alive |
|----------|---------------------|
| **iOS** | Audio background mode (`AVAudioSession` `.record`) — red mic indicator always visible. Apple reserves OS-level wake word for Siri. |
| **Android** | Foreground Service `microphone` + `FOREGROUND_SERVICE_MICROPHONE` (Android 14+) + battery whitelist. |

WebSocket idle in background:
- iOS: dies. Reconnect on `applicationWillEnterForeground` + silent push wakeup.
- Android: dies in Doze without FGS; survives with FGS.

### Battery cost

| Operation | Cost |
|-----------|------|
| Porcupine wake-word continuous | ~1-2% / hour CPU; 0.1-0.3% if DSP offload |
| WebSocket ping 30 s | ~0.5-1% / hour |
| WebSocket ping **120 s** | ~0.2-0.4% / hour |
| Whisper-tiny 30 s clip on-device | ~0.5-1.5% / inference |

Golden rule: LTE radio drains more than CPU. Extend WebSocket pings
to 120 s and batch API calls.

### Storage

| Storage | iOS | Android |
|---------|-----|---------|
| IndexedDB quota | 15% disk | 60% disk (cap 80% free) |
| Safari ITP eviction | 7 days w/o `persist()` | N/A |
| `@capacitor-community/sqlite` native | sandbox, GB | sandbox, GB |
| Capacitor Preferences | Keychain, ≤2 KB/item | EncryptedSharedPreferences, ≤100 KB |

Call `navigator.storage.persist()` on first launch.

### App footprint targets

| Metric | Target |
|--------|--------|
| Install size (IPA/AAB) | 25-45 MB |
| JS bundle gzipped | 1.5-3 MB |
| RSS cold idle | 80-130 MB |
| RSS active chat | 150-200 MB |
| RSS Whisper-tiny spike | 250-350 MB |
| RSS Whisper-base spike | 400-500 MB (OOM risk on 4 GB) |

**Sources**: [iOS Jetsam](https://www.besthub.dev/articles/uncovering-ios-oom-from-kernel-mechanics-to-real-world-monitoring-solutions-e54e1fb1d13a) · [Apple Background Modes](https://developer.apple.com/documentation/xcode/configuring-background-execution-modes) · [Android LMK](https://developer.android.com/topic/performance/vitals/lmk) · [WebKit storage](https://webkit.org/blog/14403/updates-to-storage-policy/).

---

## See also

- [Deployment profiles](profiles.md)
- [Observability stack](observability.md)
- [Sizing calculator](sizing-calculator.md)
- [Local install (PC + Wi-Fi)](../user-manual/install/local-lan.md)
