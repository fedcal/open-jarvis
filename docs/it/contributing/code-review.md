---
title: "Code review guidelines"
description: "Come fare e ricevere code review costruttive in Open-Jarvis. Mindset, checklist tecnica, tono, tempistiche."
---

# Code review

Code review è il **principale strumento di qualità** del progetto. Tutti i merge in `develop`/`staging`/`main` richiedono almeno 1 review approvante (PR su `main` richiedono review CODEOWNERS).

## 🧠 Mindset

### Per chi rivede

- **Sii curioso**, non giudicante. "Perché hai scelto questo?" > "Questo è sbagliato"
- **Concentrati sul codice**, non sulla persona
- **Cerca di capire prima di criticare**: read the diff + read the linked issue
- **Cerca opportunità di insegnamento**, non per dimostrare di sapere
- **Approva quello che è pronto**: il "perfect" è nemico del "good"

### Per chi riceve

- **Non prendere personalmente** i feedback: il codice non sei tu
- **Spiega le scelte** quando rispondi a un commento
- **Sii grato** per il tempo che il revisore ha investito
- **Se sei in disaccordo**, argomenta tecnicamente. Non insistere senza motivi
- **Aggiorna la PR** in commit incrementali, non force-push (eccetto per rebase finale)

## ✅ Checklist tecnica

### Funzionalità

- [ ] La PR fa quello che la descrizione dichiara, niente di più
- [ ] Edge case considerati (null, empty, very large, concurrent)
- [ ] Errori gestiti esplicitamente, no `try/except: pass`
- [ ] Logging strutturato con contesto utile
- [ ] Backward compatibility se modifica un'API pubblica

### Test

- [ ] Coverage ≥ 80% per il codice nuovo
- [ ] Test unitari per la logica pura
- [ ] Test di integrazione per i confini (DB, API esterne via mock)
- [ ] Test di regressione per i bug fix
- [ ] Test E2E per i flussi critici toccati
- [ ] CI verde su tutti i job

### Sicurezza

- [ ] No secret hardcoded
- [ ] Input validation ai confini (Pydantic strict)
- [ ] Output encoding per prevent injection
- [ ] Dipendenze nuove auditate (Grype, OSV)
- [ ] Endpoint nuovi: rate-limit + auth + RBAC verificati
- [ ] Dati sensibili (PII, FHIR, finance): vault separato + audit log

### Performance

- [ ] No N+1 query
- [ ] Indici DB per query frequenti
- [ ] Caching dove appropriato (Redis, prompt caching)
- [ ] Async/await consistente, no blocking IO in handler async
- [ ] Memory profile ok per cambi grossi (es. RAG ingestion)

### Documentazione

- [ ] Docstring per funzioni pubbliche (formato Google o NumPy)
- [ ] Type hints completi (mypy strict)
- [ ] README della cartella aggiornato se serve
- [ ] Cambiamenti user-facing documentati in `docs/` (IT e EN se rilevante)
- [ ] CHANGELOG entry suggerito (auto-generato da Conventional Commits)

### Architettura

- [ ] Coerente con i pattern del progetto (vedi [Architettura](../architecture/index.md))
- [ ] Single responsibility: ogni modulo fa una cosa
- [ ] Immutabilità di default
- [ ] Dependency injection invece di global state
- [ ] No tight coupling con sistemi esterni (use abstraction)

### Comunicazione

- [ ] Titolo PR Conventional Commits
- [ ] Descrizione chiara del **why**, non solo del **what**
- [ ] Screenshot/GIF per cambi UI
- [ ] Migration plan se introduce breaking change
- [ ] Linked issue/RFC

## 💬 Tono dei commenti

Buoni esempi:

> 💡 Suggerimento: forse useremmo `frozenset` qui per immutabilità?
> 🤔 Capisco la scelta, ma il pattern del progetto è X. Cosa ne pensi di allinearci?
> ✅ Bel approccio! Ho anche aggiunto un commento per spiegarlo ai prossimi che leggeranno.
> ❓ Mi sfugge perché è async. È un'operazione bloccante?

Brutti esempi (da evitare):

> ❌ "Sbagliato"
> ❌ "Non ha senso"
> ❌ "Non ho mai fatto così"
> ❌ "Cambialo"
> ❌ "Riscrivilo"

### Etichette per chiarezza

Usa prefissi nei commenti per indicare la severità:

- `[blocking]` — il merge non può procedere finché non risolvi
- `[suggestion]` — opzionale, valuta tu
- `[nit]` — pignoleria, ignora se non sei d'accordo
- `[question]` — voglio capire, non chiedo cambiamenti
- `[praise]` — questo mi piace, segnalalo

## ⏱️ Tempistiche

| Tipo PR | Target review | Target merge |
|---|---|---|
| Bug fix piccolo | < 24h | < 48h |
| Feature media | 2-4 giorni | 1-2 settimane |
| Feature grande | 1 settimana | 2-4 settimane |
| RFC | 14-30 giorni | dopo accettazione |
| Hotfix sicurezza | < 4h | < 24h |

I maintainer si impegnano a **almeno acknowledge** entro 7 giorni anche se la review piena richiede più tempo.

## 🔁 Iterazioni

- **Primo round**: review completa, tutti i commenti in una passata
- **Round successivi**: solo i punti aperti, no nuovi che potevano essere visti prima
- **Stale PR**: dopo 30 giorni di inattività → label `stale`. Dopo altri 30 → close (riapribile)

## 🎯 Approvazione

```text
✅ "LGTM" / "Approve"     — pronto al merge, niente da cambiare
🟡 "Approve with comments" — ok ma valuta i suggestion, no blocking
🔴 "Request changes"        — ci sono blocking, non mergeo
💬 "Comment"                — ho contribuito ma non prendo posizione
```

## 🛡️ Edge cases

### Auto-merge

Quando attivare auto-merge:

- ✅ Dependabot patch updates con CI verde
- ✅ Documentation-only changes piccoli (≤ 50 righe)
- ❌ Mai per cambi che toccano `auth/`, `security/`, `health/`, `finance/`

### Self-merge

Auto-merge della propria PR:

- ✅ Permesso per fix typo/docs/refactor minore (con CI verde)
- ✅ Hotfix urgenti dal lead maintainer
- ❌ Mai per nuove feature o cambi architetturali

### Resolved conversations

Solo l'autore della conversazione può marcarla come resolved (eccetto per i [nit] dove può anche l'autore della PR).

## 📊 Metrics che monitoriamo

- ⏱️ Time-to-first-review (target: < 48h)
- ⏱️ Time-to-merge (target: < 7 giorni feature media)
- 🔁 Round di review (target: ≤ 3)
- 📈 Approvazione rate per nuovo contributor (target: > 80% prima approvata o con minor changes)
- 💬 Comment-to-line ratio (target: ≤ 0.05, oltre indica review pesante)

## Riferimenti

- [Google Engineering Practices · Code Review](https://google.github.io/eng-practices/review/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [How to Make Your Code Reviewer Fall in Love with You](https://mtlynch.io/code-review-love/)
