---
title: "Public Users Registry"
description: "Il registro pubblico degli utilizzatori di Open-Jarvis. Chiunque usi il software è invitato a registrarsi."
---

# Public Users Registry

Open-Jarvis adotta una pratica trasparente, ispirata da progetti come Kubernetes, Vue.js e Linkerd: **chiunque utilizza il software è invitato a registrarsi pubblicamente**.

> Per uso aziendale, accademico, governativo o di servizio (B2B/SaaS) la registrazione è **richiesta** dallo spirito del progetto e in coerenza con AGPL-3.0.

## 🗂️ Dove vive il registro

Il registro è il file **[`USERS.md`](https://github.com/fedcal/open-jarvis/blob/main/USERS.md)** alla root del repository, **versionato in git**, modificabile da chiunque tramite Pull Request.

Schema:

```markdown
- **Nome / Name** — *contesto d'uso* — [link opzionale] — *città, paese*
```

## ✍️ Come registrarsi (3 passi)

### 1. Forka il repo

```bash
gh repo fork fedcal/open-jarvis --clone
cd open-jarvis
```

### 2. Aggiungi la tua riga

Apri `USERS.md` e aggiungi una riga nella sezione corretta:

```diff
 ### 🏠 Personal users · Utenti privati

 - **Federico Calò** — *Personal · maintainer del progetto* — [federicocalo.dev](https://federicocalo.dev) — *Italia*
+- **Mario Rossi** — *Personal* — *Roma, Italia*
```

### 3. Apri la Pull Request

```bash
git checkout -b add/me-to-users-registry
git add USERS.md
git commit -m "docs(users): add Mario Rossi to personal users registry"
git push origin add/me-to-users-registry
gh pr create --title "Add Mario Rossi to USERS.md" --body "Personal user from Roma"
```

Il maintainer mergia entro **7 giorni**.

## 📊 Categorie

| Categoria | Esempio |
|---|---|
| 🏠 Personal | Singolo cittadino |
| 👨‍👩‍👧 Family / Household | Nucleo familiare |
| 🚀 Small team / Startup | < 20 persone |
| 🏢 Enterprise / Corporate | Aziende > 20 |
| 🎓 Education | Scuole, università |
| 🏥 Healthcare | Studi medici, RSA, ospedali |
| 🏛️ Government / Public sector | Comuni, ministeri |
| ❤️ NGO / Non-profit | Associazioni, ONG |
| 🔬 Research labs | Laboratori scientifici |
| 🛠️ Makerspace / Fab Lab | Spazi maker |
| 🎨 Content creators | Solopreneur, influencer, freelance |

Vedi anche [Catalog Use Cases](../use-cases/index.md) per dettaglio per categoria.

## 🎁 Cosa ottieni registrandoti

- 📛 **Visibilità** sul progetto (chi siamo, dove siamo)
- 🌐 **Networking** con altri utilizzatori del tuo settore
- 📈 **Metrica adoption** che aiuta a giustificare il progetto verso sponsor / partner
- 💬 **Priorità nelle discussion** (i registered user hanno feedback più peso)
- 🎤 **Eventuale invito a case study** o talk community

## 🔐 Privacy

### Per utenti personali

- Pseudonimo accettato (es. "Marco_dev")
- Solo paese (no città se preferisci)
- Niente email/telefono nel registro

### Per organizzazioni

Il nome legale dell'organizzazione **deve** essere reale (no aziende fittizie). URL pubblica richiesta. Questo per:

- Trasparenza verso la community
- Conformità con AGPL §13 (chi offre Jarvis come servizio deve essere identificabile)

## 🚫 Non registrarsi è un problema?

| Caso | Conseguenza |
|---|---|
| Personale, non distribuisci | ✅ Nessun problema, ma la registrazione è apprezzata |
| Aziendale interno (no SaaS, no fork) | ✅ Nessun problema legale, registrazione raccomandata |
| Aziendale che usa internamente Jarvis fork modificato | ⚠️ Sei comunque tenuto a fork pubblico (AGPL §5) |
| Servizio SaaS modificato a terzi | ❌ Devi pubblicare il fork + registrarti, è obbligo AGPL §13 |

In tutti i casi: **registrarsi è un atto di trasparenza che aiuta la community**.

## 🔄 Aggiornamenti del registro

Se cambi nome/contesto/URL, **apri una nuova PR** per aggiornare la tua riga.

Se vuoi essere rimosso (es. hai smesso di usare Jarvis), **apri una PR di rimozione**. La storia del registro resta in git history.

## 🤝 Maintainer responsabilità

Il maintainer si impegna a:

- 🕐 Mergiare PR di registrazione entro **7 giorni**
- 🛡️ Verificare che la riga rispetti il formato e le regole privacy
- 🚫 Rifiutare entry che violano CODE_OF_CONDUCT (es. nomi offensivi, spam)
- 📊 Pubblicare statistiche aggregate trimestrali (numero utenti per categoria)

## 📈 Statistiche

_Aggiornate manualmente quando il registro cresce. Per ora: **1 entry** (il maintainer)._

| Categoria | Utenti registrati |
|---|---|
| Personal | 1 |
| Family | 0 |
| Small team | 0 |
| Enterprise | 0 |
| Education | 0 |
| Healthcare | 0 |
| Government | 0 |
| NGO | 0 |
| Research | 0 |
| Makerspace | 0 |
| Content creators | 0 |

> 🚀 _Sii tu il primo della tua categoria!_

## 🌍 Esempi di registry analoghi

I seguenti progetti hanno aperto la strada a questa pratica:

- [Kubernetes USERS.md](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.0.md)
- [Vue.js Awesome Users](https://github.com/vuejs/awesome-vue#users)
- [Linkerd ADOPTERS](https://github.com/linkerd/linkerd2/blob/main/ADOPTERS.md)
- [Prometheus USERS](https://prometheus.io/community/)
- [Hugo Showcase](https://gohugo.io/showcase/)

Ognuno con le proprie sfumature, ma stesso principio: **trasparenza dell'adozione**.

## 🎤 Vuoi essere intervistato?

Se hai un caso d'uso interessante (azienda, scuola, NGO, ecc.) e vuoi raccontarlo, apri una [Discussion](https://github.com/fedcal/open-jarvis/discussions) con label `case-study`. Il tuo racconto può diventare:

- 📝 Blog post sul sito del progetto
- 🎙️ Podcast / video community
- 📊 Caso di studio nella documentazione

**Bonus**: chi offre case study riceve un badge "Case Study" sul nome nella USERS.md.
