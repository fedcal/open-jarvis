---
title: "Gestione delle risorse · Open-Jarvis"
description: "Allocazione delle risorse hardware per server FastAPI, Postgres, Redis, Qdrant, Ollama, client desktop Tauri e mobile Ionic. 4 profili di deployment (home, VPS small/medium/large) con valori validati e citazioni alle fonti."
keywords: "open-jarvis sizing, capacity planning, fastapi workers, postgresql tuning, redis maxmemory, qdrant ram, ollama vram, ionic memory, tauri footprint"
---

# Gestione delle risorse · Open-Jarvis

Questa è la guida operativa completa per dimensionare correttamente
ogni componente di Open-Jarvis. Ogni numero che leggi è validato da
ricerche su fonti ufficiali (Apple, Android, PostgreSQL, Qdrant,
llama.cpp, Tauri, OpenTelemetry) — i link in fondo a ogni sezione
permettono di verificare e approfondire.

!!! info "TL;DR — i 4 profili"
    | Profilo | Hardware | Utenti | LLM consigliato | Quando usarlo |
    |---------|----------|--------|----------------|---------------|
    | **Home** | PC casa, 16-32 GB, no GPU | 1 | `llama3.2:3b` (Q4_K_M) o cloud | sviluppo, demo, uso personale |
    | **VPS Small** | 2 vCPU, 4-8 GB | 1 | solo cloud (Anthropic Haiku, GPT-4o-mini) | personale always-on |
    | **VPS Medium** | 4 vCPU, 16 GB | famiglia 4-5 | cloud + opzionale `llama3.2:3b` | famiglia |
    | **VPS Large** | 8 vCPU, 32 GB, GPU opz. | team 10-20 | `qwen2.5:14b` Q4 + cloud | piccolo team |

---

## 1 · Backend FastAPI

### Worker count

La regola di Gunicorn è **`(2 × CPU cores) + 1`**, ma per un'app FastAPI
**puramente async** (con `asyncpg`/`SQLAlchemy async`) un singolo worker
satura facilmente una piccola VPS perché l'event loop gestisce
centinaia di coroutine in parallelo. Più worker servono solo se hai
codice sincrono bloccante o vuoi isolamento processo-livello.

| Profilo | CPU | Formula `(2N+1)` | **Async raccomandato** | RAM per worker |
|---------|-----|-----------------|----------------------|---------------|
| Home | 8-16 | 17-33 | **2-4** | 150-300 MB |
| VPS Small | 2 | 5 | **2-3** | 150-300 MB |
| VPS Medium | 4 | 9 | **4-6** | 150-300 MB |
| VPS Large | 8 | 17 | **8-12** | 150-300 MB |

!!! warning "JWT keypair single-worker in dev"
    Senza `JARVIS_JWT_*_KEY_PEM` ogni worker genera la propria coppia
    di chiavi ES256 ephemera, rompendo la verifica JWT. In dev usa
    `--workers 1`. Vedi [Server runtime troubleshooting](../troubleshooting/server-runtime.md#signature-verification-failed).

**Fonti**: [Gunicorn Design](https://gunicorn.org/design/) · [FastAPI deployment](https://fastapi.tiangolo.com/deployment/server-workers/) · [Sentry — uvicorn workers](https://sentry.io/answers/number-of-uvicorn-workers-needed-in-production/).

### SQLAlchemy connection pool

Ogni worker apre il **proprio pool indipendente**, quindi le
connessioni reali al Postgres sono `workers × (pool_size + max_overflow)`
e **devono restare** sotto `max_connections` di Postgres.

| Profilo | Workers | `pool_size` | `max_overflow` | Connessioni totali | `max_connections` PG |
|---------|---------|------------|---------------|------------------|---------------------|
| Home | 3 | 5 | 10 | 45 | 50 |
| VPS Small | 2 | 3 | 5 | 16 | 25 |
| VPS Medium | 5 | 5 | 10 | 75 | 100 |
| VPS Large | 10 | 5 | 10 | 150 | 200 |

```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_pre_ping=True,
    pool_recycle=3600,
)
```

Per il profilo **VPS Large** considera **PgBouncer** in transaction
pooling: multiplexa 150 client su 10-20 connessioni reali Postgres.

**Fonti**: [SQLAlchemy pooling](https://docs.sqlalchemy.org/en/20/core/pooling.html) · [Pool size & overflow per ASGI](https://www.pythontutorials.net/blog/how-to-properly-set-pool-size-and-max-overflow-in-sqlalchemy-for-asgi-app/).

---

## 2 · PostgreSQL 16

Le euristiche da [pgtune](https://pgtune.leopard.in.ua/) per workload
di tipo "Web Application":

| Parametro | Regola | Note |
|-----------|--------|------|
| `shared_buffers` | 25% RAM dedicata | Cap a 8 GB su Linux |
| `effective_cache_size` | 75% RAM dedicata | Solo hint per il planner |
| `work_mem` | `(RAM × 0.25) / max_connections` | Per sort node, può moltiplicarsi |
| `maintenance_work_mem` | 5% RAM, max 2 GB | Solo durante VACUUM/REINDEX |
| `max_connections` | tieni basso, pool app-side | Ogni connessione idle ~5-10 MB |
| `wal_buffers` | `shared_buffers / 32`, max 16 MB | Auto se `-1` (default Postgres 9.1+) |
| `random_page_cost` | **1.1 su SSD/NVMe**, 4.0 su HDD | Critico per SSD |
| `checkpoint_completion_target` | 0.9 | Spreade I/O su 90% intervallo |

### Valori per profilo

Assumendo che Postgres abbia accesso esclusivo alla RAM indicata
(per servizi co-locali, riduci del 40-50%):

| Parametro | Home (PG 8 GB) | VPS Small (PG 2 GB) | VPS Medium (PG 6 GB) | VPS Large (PG 16 GB) |
|-----------|---------------|--------------------|---------------------|---------------------|
| `shared_buffers` | `2GB` | `512MB` | `1536MB` | `4GB` |
| `effective_cache_size` | `6GB` | `1536MB` | `4608MB` | `12GB` |
| `work_mem` | `32MB` | `8MB` | `16MB` | `32MB` |
| `maintenance_work_mem` | `512MB` | `128MB` | `384MB` | `1GB` |
| `max_connections` | `50` | `25` | `100` | `200` |
| `wal_buffers` | `16MB` | `8MB` | `16MB` | `16MB` |
| `random_page_cost` | `1.1` | `1.1` | `1.1` | `1.1` |

I file pronti all'uso sono in `infra/profiles/<profile>/postgresql.conf`.

**Fonti**: [pgtune.leopard.in.ua](https://pgtune.leopard.in.ua/) · [PostgreSQL Tuning Wiki](https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server) · [Crunchy Data — server tuning](https://www.crunchydata.com/blog/optimize-postgresql-server-performance) · [EnterpriseDB — memory tuning](https://www.enterprisedb.com/postgres-tutorials/how-tune-postgresql-memory).

---

## 3 · Redis 7

Open-Jarvis usa Redis solo per dati **effimeri con TTL esplicito**
(rate-limit, MFA challenge, sessioni). Policy di eviction consigliata:
**`volatile-lru`** (semanticamente safe — non evicta mai chiavi senza TTL).

```ini
# redis.conf
maxmemory 256mb
maxmemory-policy volatile-lru
maxmemory-samples 10
```

| Profilo | `maxmemory` | Razionale |
|---------|------------|-----------|
| Home | 256 MB | Generoso, dati session sono KB |
| VPS Small | 128 MB | Lascia spazio a Postgres + app |
| VPS Medium | 256 MB | Famiglia 5 utenti |
| VPS Large | 512 MB | Headroom per spike rate-limit |

`maxmemory-samples 10` (default 5) migliora l'approssimazione LRU
con costo CPU marginale.

!!! warning "`volatile-ttl` è sbagliato per rate-limit"
    Evicterebbe preferenzialmente i contatori più freschi, distruggendo
    l'utilità del rate-limit.

**Fonti**: [Redis eviction policies](https://redis.io/docs/latest/develop/reference/eviction/).

---

## 4 · Qdrant — vector store

### Formula RAM (no quantization)

```
RAM (bytes) = num_vectors × dimension × 4 × 1.5
```

Il `1.5×` copre HNSW graph + metadata + segment overhead.

### Quantization (raccomandata)

Best-practice produzione: tieni i vettori float32 **on-disk**, in RAM
solo i vettori quantizzati. Qdrant fa re-scoring sui top-K dal disco.

| Profilo | float32 | int8 (4× compress) | binary (32×, solo ≥1024 dim) |
|---------|---------|-------------------|---------------------------|
| 100K × 384 dim | 216 MB | 54 MB | non raccomandato |
| 500K × 384 dim | 1.1 GB | 274 MB | non raccomandato |
| 1M × 384 dim | 2.2 GB | 540 MB | non raccomandato |
| 1M × 1024 dim | 5.8 GB | 1.4 GB | 180 MB |

**Default Open-Jarvis**: int8 scalar quantization a 384 dim. Sotto 300
MB anche con 500K memorie utente.

**Fonti**: [Qdrant capacity planning](https://qdrant.tech/documentation/guides/capacity-planning/) · [scalar quantization](https://qdrant.tech/articles/scalar-quantization/) · [memory consumption](https://qdrant.tech/articles/memory-consumption/).

---

## 5 · LLM (Ollama / cloud)

### Matrice RAM/VRAM (Q4_K_M)

| Modello | Param | File Q4_K_M | Inferenza 4k ctx | Inferenza 8k ctx | VRAM full-GPU |
|---------|-------|-------------|-----------------|-----------------|---------------|
| llama3.2:1b | 1.2 B | 0.75 GB | 1.3 GB | 1.5 GB | 2 GB |
| llama3.2:3b | 3.2 B | 1.9 GB | 2.6 GB | 2.9 GB | 4 GB |
| qwen2.5:7b | 7.6 B | 4.4 GB | 5.2 GB | 5.8 GB | 8 GB |
| llama3.1:8b | 8 B | 4.7 GB | 5.5 GB | 6.2 GB | 8 GB |
| gemma2:9b | 9 B | 5.4 GB | 6.2 GB | 6.8 GB | 10 GB |
| qwen2.5:14b | 14.7 B | 8.9 GB | 10.0 GB | 11.0 GB | 12 GB |
| mixtral:8x7b | 46.7 B | 26.5 GB | 27.5 GB | 28.5 GB | 32 GB (2×16) |
| llama3.3:70b | 70 B | 42.5 GB | 43.5 GB | 45.6 GB | 48 GB (2×24) |

**Q4_K_M** è il default: perde ~0.5% di perplessità vs F16 ma usa **4×
meno RAM**. Q4_0 è "quasi uguale come dimensioni ma ~2.3% peggiore"
→ evita.

### Throughput (tokens/secondo, 7B Q4_K_M)

| Hardware | tok/s |
|----------|-------|
| Ryzen 7 5800X CPU only | 5-9 |
| Apple M2 Pro (Metal) | ~38 |
| Apple M3 Max (Metal) | ~66 |
| RTX 4060 8 GB | 55-65 |
| RTX 4090 24 GB | 150-188 |
| A100 80 GB (vLLM) | 400-600 |

### LLM raccomandato per profilo

| Profilo | Locale | Cloud fallback |
|---------|--------|----------------|
| Home | `llama3.2:3b` Q4_K_M (~3 GB) | `claude-haiku-4-5-20251001` |
| VPS Small | nessuno (no GPU, RAM scarsa) | **solo cloud** |
| VPS Medium | `llama3.2:3b` opz. | `claude-haiku-4-5` per task complessi |
| VPS Large | `qwen2.5:14b` Q4 (12 GB VRAM) | `claude-sonnet-4-6` per ragionamento |

### Concurrency Ollama

Per default Ollama serializza le richieste (1 alla volta). Per
multi-utente:

```bash
OLLAMA_NUM_PARALLEL=4 ollama serve
```

Costo memoria moltiplicativo: `KV_cache × NUM_PARALLEL`. Su un 7B con
32k context (~3 GB KV) → `NUM_PARALLEL=4` aggiunge ~9 GB.

### Embedder

| Modello | Param | RAM | Dim | Lingua | tok/s CPU |
|---------|-------|-----|-----|--------|-----------|
| all-MiniLM-L6-v2 | 22 M | 50 MB | 384 | EN | 600-1000 |
| nomic-embed-text-v1.5 | 137 M | 300 MB | 768/512 | EN-first | 150-300 |
| mxbai-embed-large | 335 M | 700 MB | 1024 | EN-first | 80-150 |
| **BGE-M3** | 570 M | 1.2 GB | 1024 | **100+** | 40-80 |

Open-Jarvis dev usa `DeterministicEmbedder` (hash, 50 KB RAM, zero
ML). Per produzione la scelta dipende dalle lingue richieste:
**BGE-M3** se serve italiano/multilingua, altrimenti `nomic`.

### Costi cloud vs locale

| Provider | Input $/1k | Output $/1k |
|----------|-----------|-------------|
| Anthropic Claude Haiku 4.5 | 0.0010 | 0.0050 |
| OpenAI GPT-4o mini | 0.00015 | 0.00060 |
| Groq Llama-3.3-70B | 0.00059 | 0.00079 |
| Together Llama-3.3-70B | 0.00088 | 0.00088 |
| Locale Ryzen 9 (elettricità) | ~0.0000004 | ~0.0000004 |

Cloud è 1000-10000× più caro per token rispetto alla sola elettricità,
ma elimina il costo hardware, dà accesso a modelli frontier e velocità
~50× superiori.

**Fonti**: [llama.cpp memory math](https://github.com/ggml-org/llama.cpp/discussions/3847) · [llama.cpp #2094 perplexity Q4 vs F16](https://github.com/ggml-org/llama.cpp/discussions/2094) · [Ollama PR #3418 NUM_PARALLEL](https://github.com/ollama/ollama/pull/3418) · [Ollama FAQ](https://docs.ollama.com/faq) · [BentoML embedding guide](https://www.bentoml.com/blog/a-guide-to-open-source-embedding-models) · [pricepertoken.com](https://pricepertoken.com/).

---

## 6 · Docker Compose `deploy.resources`

Docker enforce i limiti via **cgroups v2** (Linux kernel 5.10+). Verifica:

```bash
cat /sys/fs/cgroup/cgroup.controllers   # esiste = cgroups v2
docker info | grep -i cgroup
```

`memory` exceeded → kernel OOM killer (container killed, riparte se
`restart: unless-stopped`). `cpus` exceeded → throttling, no kill.

### Profilo Home (16 GB)

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
        reservations: { cpus: "1.0", memory: "2G" }
  redis:
    deploy:
      resources:
        limits:       { cpus: "0.5", memory: "384M" }
  qdrant:
    deploy:
      resources:
        limits:       { cpus: "2.0", memory: "2G" }
```

### VPS Small (2 vCPU, 4 GB)

| Service | cpus | memory |
|---------|------|--------|
| server | 1.0 | 512M |
| postgres | 1.0 | 1.5G |
| redis | 0.25 | 192M |
| qdrant | 0.5 | 512M |
| caddy | 0.25 | 64M |

### VPS Medium (4 vCPU, 16 GB)

| Service | cpus | memory |
|---------|------|--------|
| server | 2.0 | 2G |
| postgres | 2.0 | 6G |
| redis | 0.5 | 384M |
| qdrant | 1.0 | 2G |
| caddy | 0.5 | 128M |

### VPS Large (8 vCPU, 32 GB)

| Service | cpus | memory |
|---------|------|--------|
| server | 4.0 | 4G |
| postgres | 4.0 | 16G |
| redis | 1.0 | 768M |
| qdrant | 2.0 | 6G |
| caddy | 0.5 | 256M |

File pronti all'uso: `infra/profiles/<profile>/docker-compose.override.yml`.

**Fonti**: [Docker resource constraints](https://docs.docker.com/engine/containers/resource_constraints/).

---

## 7 · Desktop client

### Tauri 2 vs alternative

| Metrica | **Tauri 2** | Electron 31 | PWA | Native |
|---------|------------|------------|-----|--------|
| Bundle | 3-10 MB | 50-150 MB | <1 MB | 5-30 MB |
| RSS idle | 20-80 MB | 100-300 MB | shared browser | 15-60 MB |
| RSS chat SSE | 40-150 MB | 200-500 MB | +10-30 MB tab | 30-100 MB |
| Cold start | 200-500 ms | 1000-2000 ms | ~0 / 300-800 ms | 100-400 ms |
| Sicurezza | per-window CSP + capabilities | nodeIntegration legacy | sandbox browser | nativa |

**Open-Jarvis** sceglie **Tauri 2** per il client desktop:
~5× meno RAM di Electron, capability per-window deny-by-default,
distribuibile come `.dmg`/`.msi`/`.AppImage`/`.deb`/`.rpm` da una
singola pipeline `tauri-action`.

**Fonti**: [Tauri 2 release](https://v2.tauri.app/blog/tauri-20/) · [pkgpulse — Electron vs Tauri 2026](https://www.pkgpulse.com/blog/electron-vs-tauri-2026) · [levminer real-world Tauri vs Electron](https://www.levminer.com/blog/tauri-vs-electron).

---

## 8 · Mobile (Ionic + Capacitor)

### iOS — Jetsam HWM

iOS termina i processi quando superano il high-water mark del
`phys_footprint`. **Mai usare `resident_size`** per il monitoring,
solo `task_vm_info.phys_footprint`.

| Device | RAM totale | Jetsam HWM (~) |
|--------|-----------|---------------|
| iPhone X | 3 GB | 1.6-1.8 GB |
| iPhone 12/13 | 4 GB | ~2.1 GB |
| iPhone 14 Pro / 15 Pro | 8 GB | ~3.5-4 GB |

Per ML pesante chiedi l'**Increased Memory Limit entitlement**
(`com.apple.developer.kernel.increased-memory-limit`).

### Android — heap caps

| Device tier | `heapgrowthlimit` | `largeHeap=true` |
|-------------|-------------------|-----------------|
| 3-4 GB | 192-256 MB | 512 MB |
| 6-8 GB | 256-384 MB | 512-768 MB |
| 12 GB+ flagship | 384 MB | 1 GB |

`largeHeap` è scoraggiato in produzione (signal di poor memory mgmt).

### Background execution

| Mobile platform | Mantenere wake-word attivo |
|----------------|---------------------------|
| **iOS** | Audio background mode (`AVAudioSession` `.record`) — indicatore mic rosso sempre visibile; force-quit dell'utente termina la sessione. **Apple riserva la wake-word OS-level a Siri.** |
| **Android** | Foreground Service `microphone` + permesso `FOREGROUND_SERVICE_MICROPHONE` (Android 14+) + battery optimization whitelist. |

WebSocket idle in background:
- iOS: cade. Reconnect on `applicationWillEnterForeground` + silent push come wakeup.
- Android: cade in Doze senza FGS. Con FGS attivo sopravvive (modem perceptible).

### Battery cost (ordine di grandezza)

| Operazione | Costo |
|-----------|-------|
| Porcupine wake-word continuo | ~1-2% / ora (CPU); 0.1-0.3% se DSP offload |
| WebSocket ping 30 s | ~0.5-1% / ora (radio non sleep) |
| WebSocket ping **120 s** | ~0.2-0.4% / ora |
| Whisper-tiny 30 s clip on-device | ~0.5-1.5% per inferenza |
| QR pairing (camera 5 s) | ~0.2-0.5% one-shot |

**Regola d'oro**: il radio LTE drena più della CPU. Estendi il ping
WebSocket a 120 s, batch le richieste API.

### Storage

| Storage | iOS | Android |
|---------|-----|---------|
| IndexedDB quota | 15% disk app | 60% disk (cap 80% free) |
| Safari ITP eviction | 7 giorni se nessun `persist()` | N/A |
| **`@capacitor-community/sqlite` nativo** | sandbox app, GB | sandbox app, GB |
| Capacitor Preferences | Keychain, ≤2 KB/item | EncryptedSharedPreferences, ≤100 KB total |

Chiama `navigator.storage.persist()` al primo avvio per evitare
l'eviction Safari. **Mai** salvare cronologia chat in `Preferences` —
usa SQLite.

### Footprint app target

| Metrica | Target |
|---------|--------|
| Install size (IPA/AAB) | 25-45 MB |
| JS bundle gzipped | 1.5-3 MB |
| RSS cold idle | 80-130 MB |
| RSS chat attiva | 150-200 MB |
| RSS spike Whisper-tiny | 250-350 MB |
| RSS spike Whisper-base | 400-500 MB (rischio OOM su 4 GB) |

**Decisione design**: Whisper-tiny on-device su device 4 GB; Whisper-base
o più grande → server-side.

**Fonti**: [iOS OOM / Jetsam](https://www.besthub.dev/articles/uncovering-ios-oom-from-kernel-mechanics-to-real-world-monitoring-solutions-e54e1fb1d13a) · [Apple Background Modes](https://developer.apple.com/documentation/xcode/configuring-background-execution-modes) · [Android LMK](https://developer.android.com/topic/performance/vitals/lmk) · [Android FGS types Android 14](https://developer.android.com/about/versions/14/changes/fgs-types-required) · [Doze & App Standby](https://developer.android.com/training/monitoring-device-state/doze-standby) · [Picovoice Porcupine FAQ](https://picovoice.ai/docs/faq/porcupine/) · [WebKit storage policy](https://webkit.org/blog/14403/updates-to-storage-policy/) · [W3C/Qualcomm mobile energy](https://www.w3.org/2012/10/Qualcomm-paper.pdf).

---

## 9 · Vedi anche

- [Profili di deployment](profiles.md) — config files dettagliati per
  home / vps-small / vps-medium / vps-large
- [Observability stack](observability.md) — Prometheus / VictoriaMetrics,
  Grafana, Loki, OpenTelemetry, alert rules
- [Sizing calculator](sizing-calculator.md) — script CLI per generare
  i config ottimali date le risorse disponibili
- [Local install (PC + Wi-Fi)](../user-manual/install/local-lan.md) — il
  setup home reale
- [Update Open-Jarvis](../user-manual/updates.md) — best practice per
  aggiornare senza interruzione

## 10 · Cambiamenti previsti

- M2 voice → impatto: GPU per faster-whisper-server (default
  `tiny.en` → 1 GB VRAM, `medium.en` → 5 GB VRAM)
- M3 RAG → embedder BGE-M3 always-on (1.2 GB extra RAM al server)
- M4 health → un container `fhir-server` (HAPI FHIR JVM ~1 GB heap)

I profili saranno aggiornati. Tieni d'occhio
[`status.md`](../status.md).
