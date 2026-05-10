---
title: "Sizing calculator · Open-Jarvis"
description: "Script CLI scripts/sizing.py che genera i config ottimali date le risorse hardware disponibili (RAM, CPU, GPU)."
keywords: "open-jarvis sizing calculator, capacity planning, automation"
---

# Sizing calculator

`scripts/sizing.py` è un piccolo CLI che, date le risorse hardware
disponibili, stampa i valori raccomandati per:

- numero di worker uvicorn
- pool SQLAlchemy
- `postgresql.conf` (shared_buffers, work_mem, max_connections)
- Redis maxmemory
- Qdrant RAM proiettata
- Docker Compose `deploy.resources` per ogni servizio
- modello LLM raccomandato (locale vs cloud)

## Esecuzione

```bash
uv run scripts/sizing.py --ram 16 --cpu 4 --users 5 --gpu-vram 0
```

Esempio output:

```
== Sizing report ==
Profile match: vps-medium

Backend
  workers              : 4
  pool_size            : 5
  max_overflow         : 10
  total_pg_connections : 60

Postgres
  shared_buffers          : 1536MB
  effective_cache_size    : 4608MB
  work_mem                : 16MB
  maintenance_work_mem    : 384MB
  max_connections         : 100

Redis
  maxmemory               : 256mb
  maxmemory-policy        : volatile-lru

Qdrant
  recommended quantization: int8 scalar
  RAM @ 100k 384-dim      : ~54 MB
  RAM @ 1M 384-dim        : ~540 MB

LLM
  local model    : llama3.2:3b (Q4_K_M)  ~3 GB RAM
  cloud fallback : claude-haiku-4-5-20251001
  ollama parallel: 1 (single-user) — bump if multi-user

Docker compose deploy.resources
  server   limits: cpus=2.0 memory=2G
  postgres limits: cpus=2.0 memory=6G
  redis    limits: cpus=0.5 memory=384M
  qdrant   limits: cpus=1.0 memory=2G

Suggerimento: copia infra/profiles/vps-medium/ e personalizza
```

## Flag

| Flag | Default | Descrizione |
|------|---------|-------------|
| `--ram` | required | GB di RAM totali |
| `--cpu` | required | numero di vCPU |
| `--users` | 1 | utenti contemporanei attesi |
| `--gpu-vram` | 0 | GB di VRAM GPU disponibile |
| `--pure-async` | true | app è puramente async (no codice bloccante) |
| `--memory-vectors` | 100000 | quanti memory_items max prevedi |
| `--vector-dim` | 384 | dimensioni embedding (384 default, 1024 BGE-M3) |
| `--profile-out` | — | scrive un nuovo dir `infra/profiles/<name>/` |

## Esempio: generare un nuovo profilo

```bash
uv run scripts/sizing.py \
  --ram 64 --cpu 16 --users 50 --gpu-vram 24 \
  --vector-dim 1024 --memory-vectors 5000000 \
  --profile-out infra/profiles/team-50
```

Crea automaticamente:
- `infra/profiles/team-50/docker-compose.override.yml`
- `infra/profiles/team-50/postgresql.conf`
- `infra/profiles/team-50/redis.conf`
- `infra/profiles/team-50/README.md` con il report sopra

## Vedi anche

- [Resource management](resource-management.md)
- [Profili deployment](profiles.md)
