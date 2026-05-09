# Test e qualità

Jarvis è un sistema distribuito che tocca dati personali, biometrici e finanziari sensibili. La qualità non è negoziabile.

## Obiettivi

- **Copertura ≥ 80%** sul codice core (server, agenti)
- **Zero regressioni** in produzione: ogni bug fix porta con sé un test di regressione
- **Test sui device-bridge**: ogni integrazione (Oura, Whoop, Frame, ecc.) ha mock contract test
- **CI verde** prima di ogni merge in `main`

## Piramide del testing

```text
            ▲
           ╱E╲           E2E (Playwright · device emulators)
          ╱2 E╲          poche, lente, alto valore
         ╱─────╲
        ╱  INT  ╲        Integration (server + DB + LLM mock)
       ╱─────────╲
      ╱   UNIT    ╲      Unit (pytest · vitest)
     ╱─────────────╲     molte, veloci, isolate
```

## Stack di testing per linguaggio

| Linguaggio | Framework | Mock | Coverage |
|---|---|---|---|
| **Python** | `pytest` + `pytest-asyncio` | `pytest-mock`, `respx` (HTTPX), `freezegun` | `coverage.py` |
| **TypeScript / JS** | `vitest` o `jest` | `msw`, `nock` | `c8` / `istanbul` |
| **Go** (se usato) | `testing` + `testify` | gomock, httptest | `go test -cover` |
| **Mobile** | `XCTest` (iOS), `Espresso` (Android) | Detox, Maestro | piattaforma-specifico |
| **E2E** | **Playwright** | – | – |

## TDD workflow

```text
1. RED      → scrivi un test che fallisce
2. GREEN    → scrivi il codice minimo per farlo passare
3. IMPROVE  → refactor mantenendo i test verdi
4. COVERAGE → verifica che siamo ≥ 80%
```

## Tipi di test richiesti per ogni feature

- ✅ **Unit test** sulle funzioni pure
- ✅ **Integration test** che colpiscono il database vero (Postgres in container) — niente mock del DB
- ✅ **Contract test** per ogni client API esterno (Oura, Whoop, Plaid…)
- ✅ **E2E test** per ogni user flow critico (login, pairing device, conversazione cross-device)
- ✅ **Security test** per ogni endpoint che gestisce auth o dati sensibili

## Test di sicurezza obbligatori

- 🔒 Nessun secret hardcoded — controllato in CI con `gitleaks` o `trufflehog`
- 🔒 Validazione input ai confini (Pydantic schemas, Zod schemas)
- 🔒 Test SQL injection / XSS sui form
- 🔒 Test rate-limiting sugli endpoint pubblici
- 🔒 Audit dipendenze: `pip-audit`, `npm audit`, `osv-scanner`

## CI / CD

```yaml
# .github/workflows/ci.yml — semplificato
on: [push, pull_request]
jobs:
  test:
    steps:
      - lint        # ruff, eslint, prettier
      - typecheck   # mypy, tsc
      - unit        # pytest, vitest
      - integration # con servizi in container
      - e2e         # playwright (solo su PR ai branch di release)
      - security    # gitleaks, pip-audit
```

## Come scrivere un buon test

- 🎯 Un test = un comportamento
- 📛 Naming: `test_<componente>_<azione>_<atteso>`
- 🧱 **Arrange / Act / Assert** chiaro e visibile
- 🚫 Niente test che dipendono dall'ordine di esecuzione
- 🚫 Niente sleep arbitrari — usa fixture e await espliciti
- 🪪 Ogni test pulisce dopo di sé (transazioni rollback, container ephemeral)

## Mock strategy per gli agenti device

Le integrazioni con dispositivi fisici (Frame, OctoPrint, smartwatch) richiedono **due livelli**:

1. **Contract test** sul client → mock HTTP del server remoto
2. **Smoke test** opzionale su hardware reale → eseguiti localmente da chi sviluppa quel device-agent, non in CI

## Esempio: test integration server

```python
# server/tests/integration/test_memory_search.py
import pytest

@pytest.mark.asyncio
async def test_memory_search_returns_relevant_results(client, db, qdrant):
    # Arrange
    await client.memory.add(user_id="u1", text="I love sushi")

    # Act
    results = await client.memory.search(user_id="u1", query="japanese food")

    # Assert
    assert len(results) >= 1
    assert "sushi" in results[0].text
```

## Riferimenti

- [Conventional Commits](https://www.conventionalcommits.org/)
- [pytest documentation](https://docs.pytest.org/)
- [Playwright](https://playwright.dev/)
