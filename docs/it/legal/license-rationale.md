---
title: "Licenza AGPL-3.0 · perché"
description: "Perché Open-Jarvis è rilasciato sotto AGPL-3.0: garantire che resti libero, gratuito e che tutte le customizzazioni siano pubbliche per sempre."
keywords: "AGPL-3.0, copyleft, licenza, open source, Mastodon, Nextcloud, MinIO, share-alike, software libero"
---

# Perché AGPL-3.0

Open-Jarvis è rilasciato sotto **GNU Affero General Public License v3.0** ([AGPL-3.0](https://www.gnu.org/licenses/agpl-3.0.html)).

Questa pagina spiega **perché** questa scelta e **cosa significa** per chi usa, modifica o ridistribuisce il software.

## 🎯 I tre pilastri

Open-Jarvis si fonda su tre regole che vogliamo restino vere **per sempre**:

1. 🆓 **Sempre gratis** — nessuno può fare soldi vendendo Jarvis senza condividere il valore con la community
2. 🌍 **Sempre open source** — nessuno può creare un fork chiuso o "enterprise edition" proprietaria
3. 📢 **Sempre dichiarato** — chi modifica e distribuisce (anche **come servizio cloud**) deve pubblicare le proprie modifiche sotto la stessa licenza

L'AGPL è l'**unica licenza** che garantisce contemporaneamente tutti e tre.

## 📜 Cosa puoi fare

✅ **Usare** Open-Jarvis per qualsiasi scopo (personale, aziendale, accademico, governativo, religioso, militare…)
✅ **Studiare** il codice, modificarlo, sperimentare
✅ **Ridistribuire** copie del software originale o modificato
✅ **Far pagare** un servizio costruito su Open-Jarvis (consulenza, hosting gestito, supporto)
✅ **Fork** del progetto per qualsiasi motivo
✅ **Combinare** con altro software AGPL-compatibile

## 🚫 Cosa NON puoi fare

❌ **Vendere** una "Enterprise Edition" closed-source di Open-Jarvis
❌ **Creare un fork proprietario** senza pubblicarne il sorgente
❌ **Offrire Jarvis come servizio cloud** modificato senza pubblicare le modifiche al codice
❌ **Re-licenziare** sotto licenza non-AGPL-compatibile (no MIT, BSD, proprietaria)
❌ **Rimuovere** i copyright notice o i file di licenza

## 🔑 La clausola chiave: §13 (uso in rete)

L'**Articolo 13 dell'AGPL-3.0** è ciò che distingue questa licenza da GPL-3.0:

> "If you modify the Program, your modified version must prominently offer all users
> interacting with it remotely through a computer network […] an opportunity to
> receive the Corresponding Source of your version by providing access to the
> Corresponding Source from a network server at no charge."

In pratica: **se offri Open-Jarvis modificato come servizio cloud, devi dare ai tuoi utenti accesso al codice sorgente delle tue modifiche**.

Questo è un principio fondamentale: **nessuna SaaS-loophole**. La community ha contribuito al progetto, e la community deve poter ricevere indietro ogni miglioramento.

## 🆚 Confronto con altre licenze

| Licenza | Free use | Modifica | SaaS loophole | Re-license closed |
|---|---|---|---|---|
| **AGPL-3.0** ⭐ | ✅ | ✅ con copyleft | ❌ chiuso (§13) | ❌ vietato |
| GPL-3.0 | ✅ | ✅ con copyleft | ✅ aperto | ❌ vietato |
| MPL 2.0 | ✅ | ⚠️ file-level copyleft | ✅ aperto | ⚠️ parziale |
| Apache 2.0 | ✅ | ✅ permissiva | ✅ aperto | ✅ permesso |
| MIT | ✅ | ✅ permissiva | ✅ aperto | ✅ permesso |
| BUSL | ⚠️ con limiti | ⚠️ | ❌ commerciale | ❌ |
| SSPL | ⚠️ con limiti | ⚠️ | ❌ molto stretto | ❌ |

L'AGPL è **strict copyleft** ma **non source-available**: rimane vera open source secondo OSI/FSF, mentre BUSL e SSPL sono ibridi controversi.

## 🏆 Esempi di progetti AGPL famosi

| Progetto | Settore | Risultato |
|---|---|---|
| **Mastodon** | Social network federato | 8M+ utenti, ecosystem fork sano |
| **Nextcloud** | Cloud storage self-hosted | Adozione enterprise + community |
| **Plausible** | Analytics privacy-first | Profitti senza tradire community |
| **MinIO** | Object storage | Standard de facto S3-compatible |
| **Bitwarden** | Password manager | 8M+ utenti, server self-host gratis |
| **GitLab CE** | DevOps platform | Migrazione MIT → AGPL nel 2024 |
| **Grafana** | Observability | Migrazione Apache → AGPL nel 2024 |
| **Sentry** | Error tracking | BSL → AGPL nel 2025 |
| **Element** | Matrix client | Comunicazione cifrata |

Lo schema comune: progetti che vogliono restare **community-first** scelgono AGPL per **proteggersi da Big Tech** che storicamente prendevano open source senza restituire.

## 🤔 "Ma come fate a sostenere il progetto?"

AGPL non vieta di guadagnare. Modelli sostenibili open source con AGPL:

1. **Hosting gestito** — gli utenti pagano per non gestire il VPS (à la Mastodon hosting, Plausible Cloud)
2. **Support paid tier** — onboarding aziendale, SLA, formazione
3. **Sponsorship** — GitHub Sponsors, Open Collective, donazioni
4. **Consulenza & integrazione** — implementazione personalizzata
5. **Workshops & corsi** — formazione e certificazioni
6. **Dual licensing opzionale** — solo per casi specifici dove un'azienda vuole linkare codice non-AGPL (raro, e con accordo esplicito col copyright holder)

**Apertura è il prodotto.** Il valore è la community, non l'esclusività.

## ⚠️ Implicazioni pratiche

### Per uso personale
**Nessuna implicazione**. Usi liberamente, modifichi liberamente, niente da pubblicare se non distribuisci.

### Per uso aziendale interno (no SaaS)
Se usi Jarvis **internamente nella tua azienda** (deployment privato), **non sei obbligato** a pubblicare le modifiche. L'AGPL §13 si attiva solo se distribuisci il software o lo offri come servizio in rete a terzi.

Però **incoraggiamo a registrarsi nel [Public Users Registry](users-registry.md)** per spirito di trasparenza.

### Per offerta come servizio cloud
Se offri Jarvis (modificato o meno) come SaaS / piattaforma in rete a utenti esterni, **devi pubblicare il sorgente delle tue modifiche** sotto AGPL-3.0.

In pratica:

- Fork del repo o repo separato con i tuoi commit
- Link al fork nella UI degli utenti
- Endpoint `/source` o link visibile nel footer

### Per fork pubblici
Devi:

- Mantenere AGPL-3.0
- Riconoscere il copyright dei contributor originali
- Pubblicare i commit
- Listare il fork in [USERS.md → Public forks](users-registry.md#public-forks)

## 🛡️ Protezione da abuso

Cosa succede se qualcuno **viola** l'AGPL?

1. **Notifica privata** al violatore con richiesta di compliance
2. **Notifica pubblica** se ignorata (issue su GitHub)
3. **Software Freedom Conservancy** può intervenire legalmente in giurisdizioni dove ha standing
4. **Causa civile** in ultima istanza (raramente necessaria, AGPL ha precedenti legali solidi)

Il progetto ha registrato il proprio copyright per facilitare l'enforcement futuro.

## 🌐 Compatibilità con altre licenze

L'AGPL-3.0 è **compatibile** con:

- ✅ GPL-3.0 (con interpretazione standard FSF)
- ✅ LGPL-3.0
- ✅ Apache 2.0 (in una direzione: Apache → AGPL ok, contrario no)
- ✅ MIT, BSD, ISC (Apache → AGPL ok)
- ✅ MPL 2.0 (con boundary chiari)

Non compatibile con: GPL-2.0 only, proprietarie senza dual-licensing, SSPL, BUSL.

## 📚 Risorse

- 📜 [Testo completo AGPL-3.0](https://www.gnu.org/licenses/agpl-3.0.html)
- ❓ [FSF AGPL FAQ](https://www.gnu.org/licenses/gpl-faq.html#AGPL)
- 📖 [AGPL Compliance Guide](https://www.softwarefreedom.org/resources/2008/compliance-guide.html)
- 🎬 [Why AGPL — Mastodon's Eugen Rochko](https://blog.joinmastodon.org/2018/09/the-license-that-defines-mastodon/)
- 💼 [Plausible: 5 anni con AGPL](https://plausible.io/blog/open-source-licenses)

## 🤝 Hai dubbi?

Se hai domande sulla compatibilità della tua use case con AGPL:

- Apri una [Discussion](https://github.com/fedcal/open-jarvis/discussions) con label `legal`
- Non sostituiamo un avvocato, ma proviamo a chiarire i casi più comuni
- Per aziende: consulenza specializzata raccomandata (Software Freedom Law Center, ecc.)

> Open-Jarvis appartiene a chi lo usa. AGPL è il modo legale di dirlo.
