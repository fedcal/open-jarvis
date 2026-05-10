---
title: "Profili di deployment · Open-Jarvis"
description: "4 profili di deployment pronti all'uso (home, VPS small, VPS medium, VPS large) con file di configurazione concreti per Docker Compose, PostgreSQL, Redis."
keywords: "open-jarvis profili, deployment, home, vps, docker compose override, postgresql conf"
---

# Profili di deployment

Open-Jarvis fornisce **4 profili pronti** in `infra/profiles/`. Ogni
profilo è un set coerente di config che puoi montare sopra il
`docker-compose.yml` base.

| Profilo | Hardware | Tipo utilizzo |
|---------|----------|---------------|
| `home/` | PC casa, 16-32 GB, no GPU | sviluppo, demo, uso personale |
| `vps-small/` | 2 vCPU, 4-8 GB | personale always-on |
| `vps-medium/` | 4 vCPU, 16 GB | famiglia 4-5 |
| `vps-large/` | 8 vCPU, 32 GB | piccolo team 10-20 |

Le tabelle complete dei numeri sono in
[`resource-management.md`](resource-management.md). Qui trovi i file e
i comandi per applicarli.

## Struttura di un profilo

```
infra/profiles/<profile>/
├── docker-compose.override.yml    # limiti deploy.resources
├── postgresql.conf                # tuning Postgres
├── redis.conf                     # maxmemory + eviction
├── .env.profile                   # JARVIS_* + ports
└── README.md                      # quick-start
```

## Applicare un profilo

```bash
# Esempio: profilo home
cp infra/profiles/home/.env.profile .env
docker compose \
  -f docker-compose.yml \
  -f infra/profiles/home/docker-compose.override.yml \
  up -d
```

In alternativa esporta `COMPOSE_FILE`:

```bash
export COMPOSE_FILE=docker-compose.yml:infra/profiles/home/docker-compose.override.yml
docker compose up -d
```

## Switch fra profili

Il dato (volumi Postgres, Qdrant, Redis) è invariato — i profili
sovrascrivono solo i limiti di risorse e le config tuning. Per
spostarti da `vps-small` a `vps-medium`:

```bash
docker compose down
export COMPOSE_FILE=docker-compose.yml:infra/profiles/vps-medium/docker-compose.override.yml
docker compose up -d
```

Le migrazioni Alembic e gli utenti restano inalterati.

## Quale profilo scegli?

Decision tree:

```
Hai un dominio pubblico?
├─ No  → profilo "home" (vedi anche "Local install" senza dominio)
└─ Sì  → quanti utenti contemporanei?
         ├─ 1     → vps-small
         ├─ ≤5    → vps-medium  (famiglia)
         └─ ≤20   → vps-large   (team)
```

Per >20 utenti contemporanei, valuta lo split server in più nodi
(M-Voice + M-API + M-Worker) e Postgres replicato. Non è ancora
documentato — apri una discussion su GitHub se ne hai bisogno.

## Vedi anche

- [Resource management](resource-management.md)
- [Observability stack](observability.md)
- [Sizing calculator](sizing-calculator.md)
- [Local install (no domain)](../user-manual/install/local-lan.md)
- [Aggiornare Open-Jarvis](../user-manual/updates.md)
