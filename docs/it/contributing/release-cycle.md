---
title: "Release cycle"
description: "Cadenza delle release di Open-Jarvis: continuous deployment in develop, monthly stable in main, hotfix flow."
---

# Release cycle

Cadenza dei rilasci, criteri di promozione tra ambienti, gestione tag.

## 🗓️ Cadenza

| Cadenza | Branch | Cosa succede | Audience |
|---|---|---|---|
| **Continuous** | `develop` | Ogni merge → build + deploy `dev.*` | Sviluppatori, dogfooding |
| **Bi-weekly** | `develop` → `test` | Promote dopo settimana stabile | Community tester |
| **Monthly** | `staging` → `main` + tag `v*` | Release stabile production | Tutti gli utenti |
| **As needed** | `hotfix/*` → `main` | Fix urgenti production | Tutti |
| **Quarterly** | Major changelog + roadmap update | – | Comunicazione pubblica |

## 🚀 Workflow di promozione

### Da `develop` a `test`

```bash
# Lead maintainer settimanalmente
git checkout test
git merge --ff-only develop
git push origin test
# → CI test deploy → community test in https://test.jarvis.federicocalo.dev
```

Periodo di test: **5-7 giorni**. Bug emersi → fix in `develop` + cherry-pick in `test`.

### Da `test` a `staging`

```bash
git checkout staging
git merge --ff-only develop  # solo se test confermato
git push origin staging
```

Test finale **3-5 giorni** in staging, simulando produzione.

### Da `staging` a `main`

```bash
git checkout main
git merge --ff-only staging
git tag -a v0.2.0 -m "Release v0.2.0 — Voice & Watch"
git push origin main --tags
```

Tag → workflow automatico:

1. Build container con tag versione
2. Deploy production blue/green
3. Health check verificato
4. GitHub Release creata con changelog auto-generato
5. Notifica Discussions

## 🚨 Hotfix

```bash
git checkout -b hotfix/security-cve-2026-1234 main
# Fix minimale + test rigoroso
git commit -m "hotfix: patch CVE-2026-1234 in JWT validator"
git push -u origin hotfix/security-cve-2026-1234

# PR verso main con label "hotfix" → review urgente
# Dopo merge in main:
git checkout main && git pull
git tag v0.2.1
git push origin --tags

# Cherry-pick verso staging + develop
git checkout staging && git cherry-pick <hotfix-sha> && git push
git checkout develop && git cherry-pick <hotfix-sha> && git push
```

## 📜 Versioning (SemVer 2.0)

```text
MAJOR.MINOR.PATCH[-prerelease][+build]

0.1.0       — primo MVP (Phase 1.0 foundation)
0.2.0       — voice + watch
0.3.0       — RAG + briefing
1.0.0       — primo stable production-ready
1.0.1       — patch fix
1.1.0       — health vault
2.0.0       — breaking change API auth
2.0.0-beta.1 — beta pubblica per v2
```

| Cambiamento | Bump |
|---|---|
| Bug fix retrocompatibile | PATCH |
| Feature retrocompatibile | MINOR |
| Breaking change | MAJOR |

### Pre-release labels

- `alpha` — funziona ma instabile, breaking change frequenti
- `beta` — feature complete, in test
- `rc` — release candidate, no nuove feature

## 📋 Release checklist (lead maintainer)

Prima del tag finale:

```markdown
## Release v0.2.0 — checklist

### Code quality
- [ ] Tutti i test verdi su `staging`
- [ ] Coverage ≥ 80% mantenuta
- [ ] Grype scan: no HIGH/CRITICAL
- [ ] Semgrep: no findings nuovi
- [ ] pip-audit: no vulnerabilità note

### Documentation
- [ ] [Stato implementazione](../status.md) aggiornato
- [ ] CHANGELOG.md generato e revisionato
- [ ] User manual aggiornato per le nuove feature
- [ ] API docs ricostruite (OpenAPI)
- [ ] Migration guide scritta se ci sono breaking change

### Security
- [ ] DPIA aggiornato se ci sono nuovi tipi di dati
- [ ] Audit log review ultimi 30 giorni
- [ ] Secret rotation se necessaria
- [ ] SLSA provenance attestation

### Communication
- [ ] Annuncio in Discussions
- [ ] Post sul blog (federicocalo.dev)
- [ ] Tweet/Mastodon/Bluesky
- [ ] Email a sponsor (se >5)

### Backup
- [ ] Snapshot DB pre-deploy
- [ ] Plan B di rollback documentato
```

## 🔄 Continuous deployment in `develop`

Ogni push in `develop` triggera:

1. Run completo CI (lint + type + test + scan + e2e)
2. Build container `develop-latest`
3. Deploy automatico su `dev.jarvis.federicocalo.dev`
4. Notifica Discussions su feature merged

Filosofia: **`develop` è sempre installabile**. Se non è installabile, è un blocker da fixare immediatamente.

## 📊 KPI release

| Metrica | Target |
|---|---|
| Lead time (commit → production) | < 30 giorni |
| Deploy frequency | Settimanale (develop), Mensile (main) |
| MTTR (mean time to recover) | < 1 ora |
| Change failure rate | < 5% |
| Test coverage trend | ≥ 80%, in crescita |

## 📅 Calendario rilasci

Calendario pubblico in [Discussions/Roadmap](https://github.com/fedcal/open-jarvis/discussions/categories/roadmap).

Annunci 2 settimane prima per ogni MINOR release con:

- Feature in inclusione
- Breaking change preview
- Data target tag
- Testing window per community

## ⚠️ Rollback

Procedura emergenza:

```bash
# 1. Identifica ultima versione stabile
git log --oneline --grep="^v" main | head

# 2. Re-tag main alla versione precedente
git checkout main
git reset --hard v0.1.0   # ATTENZIONE: solo lead maintainer
git push --force-with-lease   # solo se ruleset bypass attivo

# 3. Auto-deploy si attiva e ripristina
```

In alternativa, container rollback senza modifiche git:

```bash
ssh prod-server
docker compose pull server
docker tag jarvis-server:v0.1.0 jarvis-server:latest
docker compose up -d server
```

## 🎯 LTS branches

A partire da `v1.0`, ogni MAJOR avrà un branch LTS:

- `lts/v1.x` — patch e security backport per 12 mesi
- `lts/v2.x` — patch e security backport per 12 mesi

I bug fix vanno cherry-picked manualmente da `main` ai branch LTS attivi.
