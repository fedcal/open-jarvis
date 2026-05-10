# Open-Jarvis · Deployment profiles

4 ready-to-use profiles. Numbers and rationale documented in
[`docs/it/operations/resource-management.md`](../../docs/it/operations/resource-management.md)
and [`docs/en/operations/resource-management.md`](../../docs/en/operations/resource-management.md).

| Profile | Hardware | Users | Recommended LLM |
|---------|----------|-------|-----------------|
| [`home/`](home/) | PC, 16-32 GB, no GPU | 1 | `llama3.2:3b` Q4 or cloud |
| [`vps-small/`](vps-small/) | 2 vCPU, 4-8 GB | 1 | cloud only |
| [`vps-medium/`](vps-medium/) | 4 vCPU, 16 GB | 4-5 | cloud + local `llama3.2:3b` |
| [`vps-large/`](vps-large/) | 8 vCPU, 32 GB, opt. GPU | 10-20 | `qwen2.5:14b` Q4 + cloud |

## Apply

```bash
# Pick a profile
PROFILE=vps-medium

cp infra/profiles/$PROFILE/.env.profile .env
export COMPOSE_FILE=docker-compose.yml:infra/profiles/$PROFILE/docker-compose.override.yml
docker compose up -d
```

## Switch profile

```bash
docker compose down
PROFILE=vps-large
export COMPOSE_FILE=docker-compose.yml:infra/profiles/$PROFILE/docker-compose.override.yml
docker compose up -d
```

Volumes (Postgres, Qdrant, Redis) survive the switch.

## Custom profile

Use the [sizing calculator](../../docs/it/operations/sizing-calculator.md):

```bash
uv run scripts/sizing.py \
  --ram 64 --cpu 16 --users 50 --gpu-vram 24 \
  --profile-out infra/profiles/team-50
```
