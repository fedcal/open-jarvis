# Profile · Home (PC casa)

**Hardware target**: PC casa, 16-32 GB RAM, no GPU dedicata.
**Utenti contemporanei**: 1.
**LLM consigliato**: `llama3.2:3b` Q4_K_M (Ollama, ~3 GB) o cloud fallback.

## Apply

```bash
cp infra/profiles/home/.env.profile .env
export COMPOSE_FILE=docker-compose.yml:infra/profiles/home/docker-compose.override.yml
docker compose up -d
```

## Resource limits

| Service | CPUs | Memory |
|---------|------|--------|
| server | 2.0 | 1 GB |
| postgres | 4.0 | 4 GB |
| redis | 0.5 | 384 MB |
| qdrant | 2.0 | 2 GB |

## Files

- [`docker-compose.override.yml`](docker-compose.override.yml) — `deploy.resources` limits
- [`postgresql.conf`](postgresql.conf) — Postgres tuning (`shared_buffers=2GB`, `work_mem=32MB`)
- [`redis.conf`](redis.conf) — `maxmemory=256mb`, `volatile-lru`
- [`.env.profile`](.env.profile) — environment template

## Documentation

- [Resource management — Home](../../../docs/it/operations/resource-management.md)
- [Local install (PC + Wi-Fi)](../../../docs/it/user-manual/install/local-lan.md)
