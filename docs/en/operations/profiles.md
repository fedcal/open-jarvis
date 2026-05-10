---
title: "Deployment profiles · Open-Jarvis"
description: "4 ready-to-use deployment profiles (home, VPS small/medium/large) with concrete config files for Docker Compose, PostgreSQL, Redis."
---

# Deployment profiles

Open-Jarvis ships **4 ready profiles** in `infra/profiles/`. Each is a
coherent set of configs you can layer on top of the base
`docker-compose.yml`.

| Profile | Hardware | Use case |
|---------|----------|----------|
| `home/` | Home PC, 16-32 GB, no GPU | dev, demo, personal |
| `vps-small/` | 2 vCPU, 4-8 GB | personal always-on |
| `vps-medium/` | 4 vCPU, 16 GB | family of 4-5 |
| `vps-large/` | 8 vCPU, 32 GB | small team 10-20 |

Full number tables are in [`resource-management.md`](resource-management.md).
Here you find files and commands.

## Profile structure

```
infra/profiles/<profile>/
├── docker-compose.override.yml    # deploy.resources limits
├── postgresql.conf                # Postgres tuning
├── redis.conf                     # maxmemory + eviction
├── .env.profile                   # JARVIS_* + ports
└── README.md                      # quick-start
```

## Apply a profile

```bash
cp infra/profiles/home/.env.profile .env
docker compose \
  -f docker-compose.yml \
  -f infra/profiles/home/docker-compose.override.yml \
  up -d
```

Or export `COMPOSE_FILE`:

```bash
export COMPOSE_FILE=docker-compose.yml:infra/profiles/home/docker-compose.override.yml
docker compose up -d
```

## Switch between profiles

Data (Postgres, Qdrant, Redis volumes) is invariant. Profiles only
override resource limits and tuning.

```bash
docker compose down
export COMPOSE_FILE=docker-compose.yml:infra/profiles/vps-medium/docker-compose.override.yml
docker compose up -d
```

Alembic migrations and users stay intact.

## Decision tree

```
Do you have a public domain?
├─ No  → "home" profile (also see "Local install" without domain)
└─ Yes → How many concurrent users?
         ├─ 1     → vps-small
         ├─ ≤5    → vps-medium
         └─ ≤20   → vps-large
```

For >20 concurrent users, consider splitting servers (Voice + API +
Worker) and Postgres replication. Not yet documented — open a
discussion on GitHub.

## See also

- [Resource management](resource-management.md)
- [Observability stack](observability.md)
- [Sizing calculator](sizing-calculator.md)
- [Local install](../user-manual/install/local-lan.md)
