# Profile · VPS Small

**Target**: 2 vCPU, 4-8 GB RAM (Hetzner CCX13, OVH Value).
**Users**: 1.
**LLM**: cloud only (Anthropic Haiku, OpenAI GPT-4o-mini).

| Service | CPUs | Memory |
|---------|------|--------|
| server | 1.0 | 512 MB |
| postgres | 1.0 | 1.5 GB |
| redis | 0.25 | 192 MB |
| qdrant | 0.5 | 512 MB |

## Apply

```bash
cp infra/profiles/vps-small/.env.profile .env
export COMPOSE_FILE=docker-compose.yml:infra/profiles/vps-small/docker-compose.override.yml
docker compose up -d
```

⚠️ Production: set `JARVIS_JWT_PRIVATE_KEY_PEM` + `JARVIS_JWT_PUBLIC_KEY_PEM`
explicitly. The home/dev ephemeral fallback is single-worker only.
