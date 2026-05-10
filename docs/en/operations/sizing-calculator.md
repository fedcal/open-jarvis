---
title: "Sizing calculator · Open-Jarvis"
description: "scripts/sizing.py CLI to generate optimal config for given hardware (RAM, CPU, GPU)."
---

# Sizing calculator

`scripts/sizing.py` is a small CLI that, given your hardware, prints
recommended values for:

- uvicorn worker count
- SQLAlchemy pool
- `postgresql.conf` (shared_buffers, work_mem, max_connections)
- Redis maxmemory
- Qdrant projected RAM
- Docker Compose `deploy.resources` per service
- Recommended LLM model (local vs cloud)

## Usage

```bash
uv run scripts/sizing.py --ram 16 --cpu 4 --users 5 --gpu-vram 0
```

## Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--ram` | required | total GB of RAM |
| `--cpu` | required | number of vCPUs |
| `--users` | 1 | expected concurrent users |
| `--gpu-vram` | 0 | available GPU VRAM in GB |
| `--pure-async` | true | app is fully async (no blocking code) |
| `--memory-vectors` | 100000 | max memory_items expected |
| `--vector-dim` | 384 | embedding dim (384 default, 1024 BGE-M3) |
| `--profile-out` | — | writes new dir `infra/profiles/<name>/` |

## Generate a custom profile

```bash
uv run scripts/sizing.py \
  --ram 64 --cpu 16 --users 50 --gpu-vram 24 \
  --vector-dim 1024 --memory-vectors 5000000 \
  --profile-out infra/profiles/team-50
```

Auto-creates:
- `infra/profiles/team-50/docker-compose.override.yml`
- `infra/profiles/team-50/postgresql.conf`
- `infra/profiles/team-50/redis.conf`
- `infra/profiles/team-50/README.md`

## See also

- [Resource management](resource-management.md)
- [Profiles](profiles.md)
