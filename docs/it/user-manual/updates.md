---
title: "Aggiornare Open-Jarvis"
description: "Procedure di aggiornamento per server, desktop, mobile, browser PWA, smartwatch e tutti gli altri agent. Versionamento, rollback e migrazioni database."
keywords: "open-jarvis update, aggiornamento server, mobile, desktop, migration alembic, rollback"
---

# Aggiornare Open-Jarvis

Open-Jarvis segue il versionamento [SemVer](https://semver.org):
`MAJOR.MINOR.PATCH`. Il server e gli agent sono **disaccoppiati**:
un agent v0.7 funziona con un server v0.7+, ma un server più recente
**non rompe mai** la compatibilità con un agent della stessa MAJOR.

## Politica di versionamento

| Tipo bump | Significato | Frequenza |
|-----------|-------------|-----------|
| **PATCH** (0.7.X) | bugfix, sicurezza | settimanale |
| **MINOR** (0.X.0) | nuove feature retrocompatibili | mensile |
| **MAJOR** (X.0.0) | break API, richiede update coordinato | rara |

Le release vengono firmate (cosign) e pubblicate su GitHub Releases.
Ogni release nota i breaking change, le migrazioni database e gli
agent che richiedono update obbligatorio.

## Verificare la versione corrente

```bash
# Server
curl https://jarvis.example.com/health | jq .version

# Desktop / Mobile (CLI)
jarvis --version
```

Oppure: *Settings → About → Version*.

## 1 · Aggiornare il server

```bash
cd /opt/open-jarvis    # o ovunque sia il clone
git fetch --tags
git checkout v0.X.Y    # tag della release desiderata

# Pull immagini Docker
docker compose pull

# Migrazioni DB (idempotenti)
docker compose run --rm server alembic upgrade head

# Restart graceful (zero-downtime con replica >= 2)
docker compose up -d --remove-orphans
```

Per gli aggiornamenti di sicurezza critici esiste lo script:

```bash
./scripts/update-server.sh --channel stable
```

che esegue: `git fetch + checkout`, `docker compose pull`,
`alembic upgrade`, `docker compose up -d`, smoke-test su `/health` e
rollback automatico in caso di failure.

### Rollback server

```bash
docker compose down
git checkout v0.X.Y-1
docker compose up -d
docker compose run --rm server alembic downgrade -1
```

!!! warning "Migrazioni distruttive"
    Alcuni `MINOR` introducono migrazioni che droppano colonne. Tali
    migrazioni sono sempre marcate nella release con il prefisso
    `**BREAKING DB:**`. In quel caso il rollback richiede ripristino
    dal backup. Esegui sempre `pg_dump` o lo snapshot Hetzner prima
    di un upgrade.

### Aggiornamento automatico (Watchtower)

Per ambienti home-lab / personal:

```yaml
# infra/docker-compose.yml
services:
  watchtower:
    image: containrrr/watchtower
    volumes: [/var/run/docker.sock:/var/run/docker.sock]
    command: --schedule "0 0 4 * * *" --cleanup
```

Aggiorna ogni notte alle 04:00 dopo un controllo `--label-enable`.

## 2 · Aggiornare il desktop agent

=== "macOS"

    ```bash
    brew upgrade open-jarvis
    ```

=== "Windows"

    ```powershell
    winget upgrade OpenJarvis.Desktop
    ```

=== "Linux (AppImage)"

    L'app si auto-aggiorna al prossimo avvio se hai abilitato
    `Settings → Updates → Auto-update`. Update manuale:

    ```bash
    curl -L https://github.com/fedcal/open-jarvis/releases/latest/download/open-jarvis.AppImage \
         -o ~/Applications/open-jarvis.AppImage
    ```

=== "Linux (Flatpak)"

    ```bash
    flatpak update dev.openjarvis.Desktop
    ```

Tauri verifica un manifest firmato (Ed25519) prima di applicare la
patch — niente attacchi MITM possibili anche su Wi-Fi pubblico.

## 3 · Aggiornare il mobile agent

| Piattaforma | Update path |
|-------------|------------|
| **iOS** | App Store → automatico se "App Updates" è attivo. Beta su TestFlight |
| **Android (Play Store)** | Play Console → automatico, oppure tap su "Update" |
| **Android (F-Droid)** | F-Droid → "Updates" tab |
| **Android (APK GitHub)** | scarica nuova `apk` da Releases, installa over-the-top |

Le **Expo OTA updates** (JavaScript-only) avvengono al cold-start:
nessun App Store gate per i fix non-nativi.

## 4 · Aggiornare la PWA web

Niente da fare: il service worker controlla `/version.json` ad ogni
avvio. Quando appare un nuovo bundle:

1. comparirà un toast "*Nuova versione disponibile*"
2. l'utente conferma → il service worker scarica il bundle
3. al prossimo refresh la nuova versione è attiva

## 5 · Aggiornare i client medical (M4)

Le integrazioni health vivono **server-side**: aggiornare il server
aggiorna automaticamente Oura, Whoop, Polar, ecc. Quando un provider
cambia versione OAuth (raro), trovi nelle release notes la procedura
di re-consent dell'utente.

## 6 · Aggiornare watch / glasses / VR / holo

| Dispositivo | Update path |
|-------------|------------|
| Apple Watch | bound al iPhone — aggiorna l'iPhone |
| Wear OS | Play Store → automatico |
| Garmin | Connect IQ Store → auto |
| PineTime | flash via Gadgetbridge / nRF Connect, manuale |
| Meta Quest | Quest Store → automatico |
| Brilliant Frame | Frame app → "Update Frame OS" |
| Looking Glass | Looking Glass Bridge → auto |

## Update coordinato (best practice)

Per cambi MAJOR o per troubleshooting:

1. **Backup**: `pg_dump`, snapshot VPS, export memoria.
2. **Server**: aggiorna prima di tutto.
3. **Desktop**: il dispositivo "primario", deve poter rifare il
   pairing degli altri se serve.
4. **Mobile**: dopo che il desktop conferma il flow di chat e memory.
5. **Web PWA**: si auto-aggiorna senza intervento.
6. **Watch / wearables**: per ultimi.

Lo script `scripts/upgrade-fleet.sh` orchestra il tutto via SSH +
ADB + osascript per l'utente power.

## Migrazioni database (Alembic)

Tutte le migrazioni vivono in `server/migrations/versions/`. Le
migrazioni sono **lineari** (HEAD ← 0001 ← 0002 ← …). Ogni release
documenta:

- numero versione corrente (`alembic current`)
- migrazione richiesta per arrivare a HEAD
- comando di rollback testato

Esempio nella release v0.8:

> Da v0.7: `alembic upgrade head` (migrazione 0004 — non distruttiva).
> Tempo stimato: <30 s su 1M righe.

## Aggiornamento sicuro in produzione

Checklist prima di toccare un'installazione live:

- [ ] Backup database (`pg_dump | gzip > backup-$(date +%F).sql.gz`)
- [ ] Backup volume Qdrant (snapshot della cartella `/data/qdrant`)
- [ ] Snapshot VPS (Hetzner / OVH)
- [ ] Lettura release notes complete + `BREAKING` marker
- [ ] Test del comando `alembic upgrade --sql` per ispezionare le SQL
- [ ] Maintenance window comunicata agli utenti via banner
- [ ] Smoke test post-deploy: `/health`, login, chat, memory search
- [ ] Rollback plan pronto: tag precedente + procedura ripristino DB

## Troubleshooting update

| Sintomo | Causa | Fix |
|---------|-------|-----|
| `alembic upgrade` fallisce | migrazione mai applicata in dev | Esegui `alembic stamp head` solo se sai cosa fai, altrimenti ripristina da backup |
| Container restart loop | env-var nuove non settate | Confronta `.env.example` con `.env`, aggiungi le mancanti |
| Mobile app crash dopo update | OTA scaricata male | Force-stop, riavvia: l'OTA è atomica, ricaricherà la precedente |
| Token JWT improvvisamente invalido | Chiavi ES256 ruotate | Tutti gli utenti devono ri-loggarsi (questo è documentato in MAJOR) |

## Notifiche di aggiornamento

- **GitHub Watch → Releases only** sul repository
- Channel Telegram `t.me/openjarvis` (annuncio rilasci)
- RSS feed: `https://github.com/fedcal/open-jarvis/releases.atom`

## Vedi anche

- [Multi-device install](multi-device.md)
- [Stato del progetto](../status.md)
- [Branching strategy & release cycle](../contributing/release-cycle.md)
