# Per iniziare

Guida rapida per avere la tua istanza di **Jarvis** operativa in pochi minuti.

## Requisiti

- **Docker** ≥ 24 e **Docker Compose** ≥ 2.20
- **Python** ≥ 3.12 (per agenti server-side)
- **Node.js** ≥ 20 (per frontend e agenti web)
- **Git**
- (opzionale) GPU NVIDIA con CUDA per modelli locali via Ollama

## 1. Clonazione del repository

```bash
git clone https://github.com/fedcal/open-jarvis.git
cd open-jarvis
```

## 2. Configurazione delle variabili di ambiente

Copia il template e personalizzalo:

```bash
cp .env.example .env
```

!!! warning "Sicurezza"
    Il file `.env` è gitignored di proposito: contiene i tuoi token personali e non deve mai essere committato.
    Solo `.env.example` viene tracciato dal repository — è il template per gli altri sviluppatori.

Variabili minime da impostare per l'MVP:

```env
SERVER_SECRET_KEY=...      # genera con: openssl rand -hex 32
DATABASE_URL=...
JARVIS_MODEL_LARGE=...     # es. anthropic/claude-sonnet-4-6
ANTHROPIC_API_KEY=...      # oppure OPENAI_API_KEY, GROQ_API_KEY, ecc.
```

## 3. Avvio dei servizi

```bash
docker compose up -d
```

Servizi avviati:

- **server** — API principale (porta `8080`)
- **postgres** — storage relazionale (porta `5432`)
- **qdrant** — vector store (porta `6333`)
- **redis** — cache e pub/sub (porta `6379`)
- **frontend** — UI web (porta `3000`)

## 4. Verifica installazione

```bash
curl http://localhost:8080/health
```

Risposta attesa:

```json
{"status": "ok", "version": "0.1.0"}
```

Apri il browser su [http://localhost:3000](http://localhost:3000).

## 5. Registrazione del primo dispositivo

Dal terminale:

```bash
docker compose exec server jarvis enroll --type=desktop
```

Verrà mostrato un QR code per il pairing tramite app mobile.

## Prossimi passi

- 🏗️ Studia l'[architettura](../architecture/index.md)
- 📱 Configura un [dispositivo](../devices/index.md)
- 🤝 Scopri come [contribuire](../contributing/index.md)
