# Risoluzione problemi

Una raccolta dei problemi più comuni e di come risolverli velocemente.

## Diagnostica rapida

```bash
# Stato dei container
docker compose ps

# Log degli ultimi 200 messaggi
docker compose logs --tail=200 -f

# Verifica salute del server
curl http://localhost:8080/health

# Spazio su disco
df -h .

# Versione di Jarvis
docker compose exec server jarvis version
```

## Problemi comuni

### ❌ "Cannot connect to Docker daemon"

**Causa:** Docker non in esecuzione o l'utente non è nel gruppo `docker`.

```bash
sudo systemctl start docker
sudo usermod -aG docker $USER
newgrp docker
```

### ❌ "Port 8080 already in use"

**Causa:** un altro processo occupa la porta.

```bash
sudo lsof -i :8080      # identifica il processo
# poi modifica docker-compose.yml mappando una porta libera
```

### ❌ Il server resta `unhealthy` su `docker compose ps`

```bash
docker compose logs server --tail=100
```

Cerca:

- `database connection error` → vedi sotto
- `qdrant timeout` → vedi sotto
- `secret key not set` → controlla `.env`

### ❌ "database connection error"

```bash
docker compose logs postgres --tail=50
```

Se Postgres non parte:

```bash
docker compose down
docker volume rm open-jarvis_postgres_data   # ⚠️ cancella dati DB
docker compose up -d
```

### ❌ Qdrant non risponde

```bash
docker compose restart qdrant
sleep 5
curl http://localhost:6333/health
```

### ❌ LLM cloud restituisce 401 / 403

**Causa:** API key errata o scaduta.

1. Verifica la chiave nel provider (Anthropic Console, OpenAI Dashboard, ecc.)
2. Aggiorna `.env`
3. `docker compose up -d --force-recreate server`

### ❌ Ollama "model not found"

```bash
docker compose exec ollama ollama pull llama3.1:8b
```

### ❌ Il pairing del device mobile fallisce

- Verifica che desktop e mobile siano sulla **stessa rete LAN** (durante il primo pairing)
- Se usi un reverse-proxy, controlla che `JARVIS_PUBLIC_URL` sia corretto e raggiungibile
- Rigenera il QR code: `docker compose exec server jarvis enroll --type=mobile`

### ❌ Wake-word "Hey Jarvis" non risponde

1. Verifica permessi microfono dell'app/sistema
2. `docker compose logs voice-agent --tail=100`
3. Riallinea il modello wake-word: `jarvis voice retrain`

### ❌ Non ricevo le notifiche push

- iOS: controlla **Impostazioni → Jarvis → Notifiche**
- Android: controlla che l'app non sia in **batteria ottimizzata**
- Token push registrato? `jarvis device list --type=mobile`

### ❌ Memoria che "dimentica" troppo

**Causa:** TTL della short-term memory troppo corto.

```env
MEMORY_SHORT_TTL_HOURS=24    # default 6
```

### ❌ RAG non trova un documento che hai

```bash
docker compose exec server jarvis rag reindex --source=obsidian
```

## Backup e restore

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

## Reset completo

⚠️ **Cancella tutti i dati**:

```bash
docker compose down -v
docker compose up -d
```

## Raccolta log per supporto

```bash
docker compose logs > jarvis-logs.txt
```

Allega `jarvis-logs.txt` (rimuovendo segreti) quando apri una [issue su GitHub](https://github.com/fedcal/open-jarvis/issues).

> Vai a → [FAQ](faq.md)
