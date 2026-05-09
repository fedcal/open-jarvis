---
title: "Quality standards"
description: "Standard di qualità del codice, dei test, della documentazione e del processo per garantire che Open-Jarvis sia software open source affidabile."
---

# Quality standards

Standard non negoziabili che garantiscono che Open-Jarvis sia **affidabile, manutenibile, sicuro**.

## ✅ Code quality

### Linguaggi e formattazione

| Linguaggio | Linter | Formatter | Type checker |
|---|---|---|---|
| Python | **ruff** (sostituisce flake8/pylint/black) | ruff format | mypy strict |
| TypeScript | **biome** o eslint | biome / prettier | tsc strict |
| Go | golangci-lint | gofmt | go vet |
| Rust | clippy | rustfmt | – (built-in) |
| Markdown | markdownlint | – | – |

Tutti enforced in CI. PR che fallisce lint = no merge.

### Pattern obbligatori

- ✅ **Immutabilità di default**: `frozen=True`, `tuple` invece di `list` quando possibile
- ✅ **Type hints completi**: 100% coverage type annotations
- ✅ **Async/await consistente**: no `time.sleep()` in handler async
- ✅ **Errori espliciti**: no `except: pass`, sempre logging
- ✅ **Dependency injection**: no global mutable state
- ✅ **Single responsibility**: ogni file/funzione fa una cosa
- ✅ **Pure function** dove possibile, side effect espliciti

### Anti-pattern banditi

- ❌ Magic number senza commento di contesto
- ❌ Funzioni > 50 righe (refactor in unità più piccole)
- ❌ Classi > 300 righe
- ❌ Cyclomatic complexity > 10 per funzione
- ❌ Nesting > 4 livelli
- ❌ Mutazione di parametri funzione
- ❌ Catch generico `Exception` (eccetto al boundary)

### Naming

```python
# Good
def fetch_oura_sleep_records(user_id: UUID, since: date) -> list[SleepRecord]:
    ...

class JarvisIdentityProvider:
    ...

OURA_RATE_LIMIT_RPS = 5

# Bad
def get_data(uid, d):  # ❌ unclear types, abbreviazioni
def OuraSleepFetcher():  # ❌ camelCase per funzione
def __process():  # ❌ dunder per privato non standard
class data_class:  # ❌ snake_case per classe
```

## 🧪 Test standards

### Coverage minima

- **Server core**: ≥ 85% line coverage, ≥ 75% branch coverage
- **Agents**: ≥ 80% line coverage
- **Frontend critical paths**: ≥ 70% line coverage
- **Migrations / scripts**: copertura tramite test E2E

PR che fa **abbassare** la coverage richiede giustificazione esplicita.

### Test types richiesti per ogni feature

```text
✅ Unit tests        — funzioni pure, isolate
✅ Integration tests — DB reale (Postgres in container), API esterne via mock
✅ Contract tests    — per ogni client API esterno (Oura, Whoop, Plaid)
✅ E2E tests         — flussi critici end-to-end (Playwright)
✅ Security tests    — endpoint con auth/sensitive data
✅ Performance tests — per cambi che toccano hot path
```

### Stack testing

| Tipo | Python | Frontend |
|---|---|---|
| Unit | `pytest` + `pytest-asyncio` | `vitest` |
| Mock HTTP | `respx` (HTTPX) | `msw` |
| Property-based | `hypothesis` | `fast-check` |
| E2E | `playwright` | `playwright` |
| Load | `locust` | `k6` |
| Coverage | `coverage.py` | `c8` / `istanbul` |

### Test isolation

- ✅ Ogni test pulisce dopo sé (transazioni rollback, fixture cleanup)
- ✅ Test indipendenti dall'ordine di esecuzione
- ✅ Container ephemeral per test integration
- ❌ Shared mutable state tra test
- ❌ Sleep arbitrari (usare fixture/await espliciti)

## 📚 Documentation standards

### Cosa va documentato

| Tipo | Dove | Quando |
|---|---|---|
| API pubblica | OpenAPI auto-generato + esempi | Sempre |
| User-facing feature | `docs/it/` + `docs/en/` | Sempre |
| Architectural decision | RFC + `docs/rfcs/` | Cambi architetturali |
| Setup / install | `docs/it/user-manual/install/` | Nuove piattaforme |
| Internal logic | Docstring + `docs/it/architecture/deep-dives/` | Componenti complessi |
| Breaking change | Migration guide + CHANGELOG | Sempre |

### Docstring style

Python (Google style):

```python
def fetch_oura_sleep(user_id: UUID, days: int = 7) -> list[SleepRecord]:
    """Recupera record di sonno Oura degli ultimi N giorni.

    Args:
        user_id: UUID dell'utente Jarvis (non Oura).
        days: Quanti giorni indietro andare (default 7, max 30).

    Returns:
        Lista di SleepRecord ordinati per data decrescente.

    Raises:
        OuraTokenExpired: Se il token OAuth è scaduto e il refresh fallisce.
        RateLimitExceeded: Se superato il rate limit Oura (5K req/5min).

    Example:
        >>> records = await fetch_oura_sleep(user.id, days=14)
        >>> records[0].efficiency_pct
        87.3
    """
    ...
```

### README per ogni componente

Ogni cartella significativa (`server/jarvis_server/auth/`, `agents/medical-agent/`, ecc.) ha un `README.md` con:

1. Cosa fa
2. Stack tecnico
3. Come testarlo localmente
4. Punti di estensione
5. Troubleshooting

## 🛡️ Security standards

### Mandatory checks

- [ ] No secret hardcoded (gitleaks in pre-commit + CI)
- [ ] Input validation strict (Pydantic + Zod)
- [ ] Output encoding per HTML/SQL/shell
- [ ] CSRF protection per form
- [ ] Rate limiting su tutti gli endpoint pubblici
- [ ] Auth + RBAC verificati per ogni nuovo endpoint
- [ ] Audit log per accessi a dati sensibili
- [ ] SBOM aggiornato ad ogni release

### Security review obbligatoria per

- Modifiche a `server/jarvis_server/auth/`
- Endpoint nuovi che gestiscono PII / FHIR / finance
- Cambi a `Dockerfile`, `docker-compose.yml`, workflows GitHub
- Aggiornamento dipendenze critiche (anthropic, openai, fastapi)
- Cambi a politiche CORS, headers, TLS

Trigger automatico via CODEOWNERS sui path sopra.

## 📦 Dependency management

### Aggiunta nuova dipendenza

```markdown
## Pre-aggiunta checklist
- [ ] Esiste già una dipendenza che fa la stessa cosa?
- [ ] La libreria ha > 1000 stelle GitHub o è ufficiale?
- [ ] Licenza compatibile con MIT?
- [ ] Manutenzione attiva (ultimo commit < 6 mesi)?
- [ ] Audit di sicurezza pulito (Grype, OSV)?
- [ ] Dimensione ragionevole (no leftpad)?
- [ ] Maintainer nel team OK con la scelta?
```

### Update strategy

- **Patch**: auto-merge tramite Dependabot (se CI verde)
- **Minor**: review manuale, di solito accettato dopo CI
- **Major**: review approfondita, possibile RFC se introduce breaking

### License compliance

- ✅ Allowed: MIT, Apache 2.0, BSD-2/3, ISC, Unlicense, CC0
- ⚠️ Discusso: MPL 2.0, EPL 2.0, LGPL 3.0
- ❌ Vietato: AGPL, GPL 3.0, SSPL, Commons Clause, "ethical" licenses

Verifica automatica con [github.com/google/licensecheck](https://github.com/google/licensecheck) o [dependabot license filter](https://docs.github.com/en/code-security/dependabot).

## 🔬 Performance standards

### Latency budget per layer

| Layer | p95 target | p99 target |
|---|---|---|
| API REST handler | 200ms | 500ms |
| DB query | 50ms | 200ms |
| Vector search (Qdrant) | 100ms | 300ms |
| LLM inference (cloud) | 700ms | 2000ms |
| LLM inference (Ollama small) | 200ms | 500ms |
| Voice STT (5s clip) | 400ms | 800ms |
| Voice TTS first chunk | 150ms | 300ms |
| End-to-end voice round trip | 1500ms | 3000ms |

PR che peggiora un budget di > 10% richiede giustificazione tecnica.

### Profilation richiesta per

- Cambi che toccano hot path (`/chat`, `/health`, `memory.search`)
- Aggiunta di nuovi middleware
- Cambi nel layer di routing LLM
- Cambi in voice pipeline

Tool: `pyinstrument`, `py-spy`, `austin`, Chrome DevTools per frontend.

## 📊 Observability standards

### Logging

```python
import structlog

log = structlog.get_logger()


# Buono — logging strutturato con contesto
log.info("oura_sync_completed",
         user_id=str(user.id),
         records_count=len(records),
         duration_ms=elapsed_ms,
         provider="oura")

# Male
log.info(f"Done {user.id} {len(records)} records in {elapsed_ms}ms")
```

Tutti i log in formato JSON in produzione (parseable da Loki).

### Metrics

- ✅ Esporre metriche Prometheus su `/metrics` (porta interna)
- ✅ RED method: Rate, Errors, Duration per endpoint
- ✅ USE method per risorse: Utilization, Saturation, Errors
- ✅ Business metrics custom (es. `oura_sync_records_total`)

### Tracing

- ✅ OpenTelemetry SDK installato e configurato
- ✅ Span per ogni handler API + chiamate downstream
- ✅ Trace ID propagato in HTTP headers `traceparent`

### SLO

| Servizio | Disponibilità | Latency p95 |
|---|---|---|
| API gateway | 99.9% | 200ms |
| Auth service | 99.95% | 100ms |
| Memory service | 99.5% | 150ms |
| LLM router | 99.5% | (dipende provider) |

Error budget calcolato mensilmente.

## ✅ Definition of Done

Una feature è "Done" quando **tutto** è vero:

- [ ] Codice scritto seguendo i pattern del progetto
- [ ] Test unitari + integration + E2E (se applicabile)
- [ ] Coverage ≥ 80% sul codice nuovo
- [ ] Lint + format + type-check verde
- [ ] Security scan: no nuove vulnerabilità HIGH/CRITICAL
- [ ] Documentation aggiornata (IT + EN se user-facing)
- [ ] CHANGELOG entry suggerito (auto via Conventional Commits)
- [ ] Migration plan se introduce breaking change
- [ ] Code review approvata da CODEOWNERS
- [ ] CI completamente verde
- [ ] Funziona localmente con `docker compose up`
- [ ] Funziona su `develop` deploy automatico
- [ ] Nessun TODO/FIXME aggiunto senza issue collegato

## 📈 Continuous improvement

Standard rivisti **trimestralmente** in retrospettive pubbliche:

- Cosa ha rallentato?
- Cosa ha funzionato?
- Cosa è diventato bottleneck?
- Quali standard sono troppo stretti? Troppo larghi?

Modifiche via RFC.

## 📚 Riferimenti

- [Google Engineering Practices](https://google.github.io/eng-practices/)
- [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines)
- [12-Factor App](https://12factor.net/)
- [SRE Workbook](https://sre.google/workbook/)
- [Pragmatic Engineer · DORA metrics](https://newsletter.pragmaticengineer.com/p/dora-2024)
