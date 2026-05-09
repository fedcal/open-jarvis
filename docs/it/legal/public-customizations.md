---
title: "Public customizations clause"
description: "Come pubblicare le tue customizzazioni di Open-Jarvis per essere conforme ad AGPL-3.0 e contribuire alla community."
---

# Public customizations · come restituire alla community

Open-Jarvis è sotto **AGPL-3.0**. Significa che **se modifichi il software e lo offri come servizio in rete o lo distribuisci, devi pubblicare le modifiche**.

Questa pagina spiega **come fare** in pratica.

## 🎯 Quando devi pubblicare

| Scenario | Devi pubblicare? |
|---|---|
| Uso solo per me, niente modifiche | ❌ No |
| Uso in azienda internamente (no users esterni) | ❌ No (ma raccomandato) |
| Modifico per uso interno, niente distribuzione | ❌ No |
| **Offro Jarvis (anche modificato) come servizio cloud a terzi** | ✅ Sì |
| Distribuisco binari/container modificati | ✅ Sì |
| Pubblico un fork su GitHub | ✅ Sì |
| Includo Jarvis (modificato) in un mio prodotto distribuito | ✅ Sì |

## 📝 Cosa devi pubblicare esattamente

L'AGPL richiede di pubblicare la **"Corresponding Source"**:

- ✅ Tutto il codice sorgente delle tue modifiche
- ✅ Le configurazioni necessarie alla build
- ✅ Le istruzioni di installazione
- ✅ I patch sui file Open-Jarvis originali (o l'intero file modificato)
- ✅ Il `Dockerfile` e i `docker-compose.yml` se modificati
- ✅ Gli script di deploy

Cosa **non** sei obbligato a pubblicare:

- ❌ Le tue chiavi API o secret
- ❌ I dati dei tuoi utenti
- ❌ I tuoi file di configurazione personali (`.env`)
- ❌ Codice strettamente proprietario che **non** estende Open-Jarvis (es. il tuo CRM aziendale)
- ❌ Plugin completamente separati che usano l'API pubblica di Jarvis (vedi sotto)

## 🔌 Plugin: la regola del confine

I **plugin** che usano solo l'API pubblica di Jarvis (REST, MCP, A2A) non sono "modifiche di Jarvis": sono software a sé stante. Possono avere licenza diversa, anche proprietaria.

| Tipo | Linkato come | Licenza obbligata |
|---|---|---|
| Modifica al codice di `server/jarvis_server/` | Compilato dentro | AGPL-3.0 |
| Plugin caricato dinamicamente, usa solo API pubblica | Network call / IPC | A scelta del plugin author |
| Fork del repo con cambiamenti al core | Patch del codice | AGPL-3.0 |
| Estensione browser che parla a Jarvis via REST | API esterna | A scelta |

In dubbio? Apri una [Discussion](https://github.com/fedcal/open-jarvis/discussions) con label `legal`.

## 🚀 Come pubblicare il tuo fork

### Opzione 1 — Fork pubblico su GitHub (consigliato)

1. Forka [`fedcal/open-jarvis`](https://github.com/fedcal/open-jarvis)
2. Lavora nel tuo fork normalmente
3. Aggiungi una riga in [USERS.md → Public forks](https://github.com/fedcal/open-jarvis/blob/main/USERS.md) con PR
4. Mantieni la sincronizzazione `git fetch upstream` periodica

```bash
# Setup upstream
git remote add upstream https://github.com/fedcal/open-jarvis.git

# Allineamento periodico
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

### Opzione 2 — Repo separato con riferimento

Se non vuoi forkare ma vuoi solo mantenere patch:

1. Crea un repo `mio-jarvis-fork` su un git host pubblico (GitHub, GitLab, Codeberg, ecc.)
2. Includi i file modificati o i patch (`*.patch`)
3. Documenta nel `README.md` che è basato su Open-Jarvis vXYZ
4. Mantieni la licenza **AGPL-3.0**

### Opzione 3 — In-app source link

Se offri Jarvis modificato come SaaS:

1. Aggiungi nel footer della tua UI un link visibile: "Source code"
2. Il link punta al tuo repo pubblico
3. Aggiorna il link a ogni release pubblica

Esempio:

```html
<footer>
  <a href="https://github.com/myorg/our-jarvis-fork" rel="external">
    Powered by Open-Jarvis (modified) — source code
  </a>
</footer>
```

## 📋 Checklist di compliance AGPL

Prima di andare in produzione con un Jarvis modificato come servizio:

- [ ] Repo del fork è **pubblico** (no `private` su GitHub)
- [ ] LICENSE include il testo completo AGPL-3.0
- [ ] README dichiara: "Based on Open-Jarvis ([github.com/fedcal/open-jarvis](https://github.com/fedcal/open-jarvis)) — AGPL-3.0"
- [ ] Tutte le modifiche al codice originale sono **commit pubblici**
- [ ] Il link al sorgente è visibile nella UI degli utenti finali
- [ ] Nessun secret, API key, dato utente nel repo
- [ ] Hai aggiunto la tua entry in [USERS.md](https://github.com/fedcal/open-jarvis/blob/main/USERS.md)
- [ ] I tuoi contributor accettano AGPL (CLA semplificato o sufficiente)

## ✨ Best practice di un buon fork

Anche se l'AGPL non lo impone, un fork **rispettoso** della community fa anche:

- 📝 Chiarisce le **divergenze** dal progetto upstream nel README
- 🔁 Sottomette **PR upstream** per le modifiche di interesse generale
- 🏷️ Usa **versioning chiaro** che identifica il fork (es. `v0.5.0-acme1`)
- 💬 Linka i propri **issue/discussion** in modo che la community originale possa tracciare
- 🤝 Non **enclave**: contribuisce su entrambi i lati

## 🛠️ Tool consigliati

### Sync upstream automatico

GitHub Action `aormsby/Fork-Sync-With-Upstream-action` per allineare il main del fork ad upstream:

```yaml
# .github/workflows/sync-upstream.yml (nel tuo fork)
name: Sync upstream
on:
  schedule:
    - cron: "0 6 * * *"
  workflow_dispatch:
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: main
          fetch-depth: 0
      - uses: aormsby/Fork-Sync-With-Upstream-action@v3
        with:
          upstream_sync_branch: main
          upstream_sync_repo: fedcal/open-jarvis
          target_branch: main
```

### License compliance check

Pre-commit hook per verificare:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/fsfe/reuse-tool
    rev: v3.0.2
    hooks:
      - id: reuse
```

[REUSE.software](https://reuse.software/) automatizza la conformità SPDX e AGPL.

### SBOM con licenza

```bash
syft dir:. -o cyclonedx-json | jq '.components[] | {name, license: .licenses[0].license.id}'
```

## 🤝 Contributor License Agreement (CLA)

Open-Jarvis **non richiede CLA**. Le contribuzioni sono accettate sotto AGPL-3.0 implicitamente (DCO sign-off raccomandato).

Se forki e accetti contributor, considera di adottare uno di questi:

- **DCO** (Developer Certificate of Origin) — light, basta `git commit -s`
- **Linux Foundation CLA Manager** — automated, integrato GitHub
- **CLA semplice via PR** — modello per progetti piccoli

## 📚 Risorse legali (non consulenza)

- [SFC AGPL Compliance Guide](https://sfconservancy.org/copyleft-compliance/)
- [REUSE.software](https://reuse.software/)
- [SPDX License List](https://spdx.org/licenses/)
- [OSS Compliance Toolkit](https://github.com/oss-review-toolkit/ort)

> ⚠️ **Disclaimer**: questa pagina è un tentativo di chiarezza, non sostituisce consulenza legale. Per casi commerciali significativi, consulta un avvocato specializzato in software libero.

## 🆘 Hai modificato Jarvis e non sapevi della compliance?

Nessun problema, basta sistemare:

1. Pubblica subito il repo (qualunque host pubblico)
2. Notifica nel registro USERS.md
3. Apri una Discussion per segnalare e ottenere aiuto se serve

La community valuta la **buona fede**, non la perfezione.
