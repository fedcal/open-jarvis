---
title: "Update Open-Jarvis"
description: "Upgrade procedures for server, desktop, mobile, browser PWA, smartwatch and every other agent. Versioning, rollback and database migrations."
keywords: "open-jarvis update, server upgrade, mobile, desktop, alembic migrations, rollback"
---

# Update Open-Jarvis

Open-Jarvis follows [SemVer](https://semver.org): `MAJOR.MINOR.PATCH`.
Server and agents are **decoupled**: an agent v0.7 talks to a server
v0.7+, and a newer server **never** breaks compatibility with an agent
of the same MAJOR.

## Versioning policy

| Bump | Meaning | Cadence |
|------|---------|---------|
| **PATCH** (0.7.X) | bugfix, security | weekly |
| **MINOR** (0.X.0) | backwards-compatible features | monthly |
| **MAJOR** (X.0.0) | breaking API, coordinated update | rare |

Releases are signed (cosign) and published on GitHub Releases. Each
release notes documents breaking changes, DB migrations and which
agents require a forced update.

## Check current version

```bash
# Server
curl https://jarvis.example.com/health | jq .version

# Desktop / Mobile (CLI)
jarvis --version
```

Or *Settings → About → Version*.

## 1 · Update the server

```bash
cd /opt/open-jarvis
git fetch --tags
git checkout v0.X.Y

# Pull Docker images
docker compose pull

# DB migrations (idempotent)
docker compose run --rm server alembic upgrade head

# Graceful restart (zero-downtime with replicas >= 2)
docker compose up -d --remove-orphans
```

For critical security updates:

```bash
./scripts/update-server.sh --channel stable
```

Runs: `git fetch + checkout`, `docker compose pull`,
`alembic upgrade`, `docker compose up -d`, smoke test on `/health`,
auto-rollback on failure.

### Server rollback

```bash
docker compose down
git checkout v0.X.Y-1
docker compose up -d
docker compose run --rm server alembic downgrade -1
```

!!! warning "Destructive migrations"
    Some MINOR releases drop columns. Such migrations are flagged with
    `**BREAKING DB:**` in the release notes. Rollback then requires
    backup restore. Always `pg_dump` or VPS snapshot before an upgrade.

### Auto-update (Watchtower)

For homelab / personal:

```yaml
# infra/docker-compose.yml
services:
  watchtower:
    image: containrrr/watchtower
    volumes: [/var/run/docker.sock:/var/run/docker.sock]
    command: --schedule "0 0 4 * * *" --cleanup
```

Updates every night at 04:00 with `--label-enable`.

## 2 · Update the desktop agent

```bash
pnpm install
pnpm --filter @open-jarvis/desktop build
```

Or run the auto-updater built into Tauri once we publish signed
releases (M1.7).

## 3 · Update the mobile agent

| Platform | Update path |
|----------|------------|
| **iOS** | App Store → automatic if "App Updates" is on. Beta on TestFlight |
| **Android (Play Store)** | Play Console → automatic, or tap "Update" |
| **Android (F-Droid)** | F-Droid → "Updates" tab |
| **Android (GitHub APK)** | grab the new `apk` from Releases, install over the top |

**Capacitor live-updates** (JS-only) happen at cold-start: no App
Store gate for non-native fixes.

## 4 · Update the web PWA

Nothing to do: the Angular service worker checks `/version.json` at
every boot. When a new bundle appears:

1. a "*New version available*" toast shows
2. user confirms → service worker downloads
3. on the next refresh the new version is active

## 5 · Update health/medical clients (M4)

Health integrations live **server-side**: updating the server
auto-updates Oura, Whoop, Polar, etc. When a provider rolls a new
OAuth version (rare) the release notes document the user re-consent
procedure.

## 6 · Update watch / glasses / VR / holo

| Device | Update path |
|--------|------------|
| Apple Watch | bound to iPhone — update the iPhone |
| Wear OS | Play Store → automatic |
| Garmin | Connect IQ Store → auto |
| PineTime | flash via Gadgetbridge / nRF Connect, manual |
| Meta Quest | Quest Store → automatic |
| Brilliant Frame | Frame app → "Update Frame OS" |
| Looking Glass | Looking Glass Bridge → auto |

## Coordinated update (best practice)

For MAJOR bumps or troubleshooting:

1. **Backup**: `pg_dump`, VPS snapshot, memory export.
2. **Server**: update first.
3. **Desktop**: the "primary" device — must be able to re-pair the
   others if needed.
4. **Mobile**: after the desktop confirms chat + memory work.
5. **Web PWA**: auto-updates without intervention.
6. **Watch / wearables**: last.

`scripts/upgrade-fleet.sh` orchestrates everything via SSH + ADB +
osascript for the power user.

## Database migrations (Alembic)

All migrations live in `server/migrations/versions/`. They are
**linear** (HEAD ← 0001 ← 0002 ← …). Each release documents:

- current version (`alembic current`)
- migration required to reach HEAD
- tested rollback command

Example v0.8 release notes:

> From v0.7: `alembic upgrade head` (migration 0004 — non-destructive).
> Estimated time: <30 s on 1M rows.

## Production update checklist

Before touching a live install:

- [ ] DB backup (`pg_dump | gzip > backup-$(date +%F).sql.gz`)
- [ ] Qdrant volume snapshot (`/data/qdrant`)
- [ ] VPS snapshot (Hetzner / OVH)
- [ ] Read full release notes + `BREAKING` markers
- [ ] Inspect SQL with `alembic upgrade --sql`
- [ ] Comm a maintenance window via banner
- [ ] Post-deploy smoke test: `/health`, login, chat, memory search
- [ ] Rollback plan ready: previous tag + DB restore procedure

## Update troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `alembic upgrade` fails | migration never applied in dev | Run `alembic stamp head` only if you know what you're doing, otherwise restore from backup |
| Container restart loop | new env vars not set | Diff `.env.example` with `.env`, add the missing ones |
| Mobile app crash after update | OTA download corrupted | Force-stop, restart: OTA is atomic, will reload the previous one |
| JWT suddenly invalid | ES256 keys rotated | Every user must re-login (documented in MAJOR) |

## Update notifications

- **GitHub Watch → Releases only** on the repo
- Telegram channel `t.me/openjarvis` (release announcements)
- RSS feed: `https://github.com/fedcal/open-jarvis/releases.atom`

## See also

- [Multi-device install](multi-device.md)
- [Project status](../status.md)
- [Branching strategy & release cycle](../contributing/release-cycle.md)
