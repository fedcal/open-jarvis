# Troubleshooting

A collection of the most common problems and how to fix them quickly.

## Quick diagnostics

```bash
# Container status
docker compose ps

# Last 200 log lines
docker compose logs --tail=200 -f

# Server health
curl http://localhost:8080/health

# Disk space
df -h .

# Jarvis version
docker compose exec server jarvis version
```

## Common issues

### ❌ "Cannot connect to Docker daemon"

**Cause:** Docker not running or your user is not in the `docker` group.

```bash
sudo systemctl start docker
sudo usermod -aG docker $USER
newgrp docker
```

### ❌ "Port 8080 already in use"

**Cause:** another process is bound to the port.

```bash
sudo lsof -i :8080      # identify the process
# then edit docker-compose.yml mapping a free port
```

### ❌ Server stays `unhealthy` on `docker compose ps`

```bash
docker compose logs server --tail=100
```

Look for:

- `database connection error` → see below
- `qdrant timeout` → see below
- `secret key not set` → check `.env`

### ❌ "database connection error"

```bash
docker compose logs postgres --tail=50
```

If Postgres won't start:

```bash
docker compose down
docker volume rm open-jarvis_postgres_data   # ⚠️ deletes DB data
docker compose up -d
```

### ❌ Qdrant unresponsive

```bash
docker compose restart qdrant
sleep 5
curl http://localhost:6333/health
```

### ❌ Cloud LLM returns 401 / 403

**Cause:** wrong or expired API key.

1. Check the key in the provider (Anthropic Console, OpenAI Dashboard, …)
2. Update `.env`
3. `docker compose up -d --force-recreate server`

### ❌ Ollama "model not found"

```bash
docker compose exec ollama ollama pull llama3.1:8b
```

### ❌ Mobile device pairing fails

- Verify desktop and mobile are on the **same LAN** (for the first pairing)
- If you use a reverse-proxy, check `JARVIS_PUBLIC_URL` is correct and reachable
- Re-issue the QR code: `docker compose exec server jarvis enroll --type=mobile`

### ❌ "Hey Jarvis" wake-word not responding

1. Verify app/system microphone permissions
2. `docker compose logs voice-agent --tail=100`
3. Realign the wake-word model: `jarvis voice retrain`

### ❌ Not receiving push notifications

- iOS: check **Settings → Jarvis → Notifications**
- Android: check the app is not in **battery optimisation**
- Push token registered? `jarvis device list --type=mobile`

### ❌ Memory "forgets" too much

**Cause:** short-term memory TTL too low.

```env
MEMORY_SHORT_TTL_HOURS=24    # default 6
```

### ❌ RAG cannot find a document you have

```bash
docker compose exec server jarvis rag reindex --source=obsidian
```

## Backup and restore

### Backup

```bash
docker compose exec postgres pg_dump -U jarvis jarvis > backup-$(date +%F).sql
docker run --rm -v open-jarvis_qdrant_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/qdrant-$(date +%F).tar.gz /data
```

### Restore

```bash
cat backup.sql | docker compose exec -T postgres psql -U jarvis jarvis
```

## Full reset

⚠️ **Erases all data**:

```bash
docker compose down -v
docker compose up -d
```

## Collecting logs for support

```bash
docker compose logs > jarvis-logs.txt
```

Attach `jarvis-logs.txt` (after redacting secrets) when opening a [GitHub issue](https://github.com/fedcal/open-jarvis/issues).

> Continue to → [FAQ](faq.md)
