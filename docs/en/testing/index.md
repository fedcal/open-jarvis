# Testing & quality

Jarvis is a distributed system handling sensitive personal, biometric and financial data. Quality is non-negotiable.

## Goals

- **Coverage ≥ 80%** on core code (server, agents)
- **Zero regressions** in production: every bug fix ships with a regression test
- **Device-bridge tests**: every integration (Oura, Whoop, Frame, …) has mock contract tests
- **Green CI** before every merge to `main`

## Testing pyramid

```text
            ▲
           ╱E╲           E2E (Playwright · device emulators)
          ╱2 E╲          few, slow, high value
         ╱─────╲
        ╱  INT  ╲        Integration (server + DB + LLM mock)
       ╱─────────╲
      ╱   UNIT    ╲      Unit (pytest · vitest)
     ╱─────────────╲     many, fast, isolated
```

## Testing stack per language

| Language | Framework | Mock | Coverage |
|---|---|---|---|
| **Python** | `pytest` + `pytest-asyncio` | `pytest-mock`, `respx` (HTTPX), `freezegun` | `coverage.py` |
| **TypeScript / JS** | `vitest` or `jest` | `msw`, `nock` | `c8` / `istanbul` |
| **Go** (if used) | `testing` + `testify` | gomock, httptest | `go test -cover` |
| **Mobile** | `XCTest` (iOS), `Espresso` (Android) | Detox, Maestro | platform-specific |
| **E2E** | **Playwright** | – | – |

## TDD workflow

```text
1. RED      → write a failing test
2. GREEN    → write the minimum code to make it pass
3. IMPROVE  → refactor while keeping tests green
4. COVERAGE → verify we are ≥ 80%
```

## Test types required per feature

- ✅ **Unit tests** on pure functions
- ✅ **Integration tests** hitting the real database (Postgres in container) — no DB mocks
- ✅ **Contract tests** for every external API client (Oura, Whoop, Plaid…)
- ✅ **E2E tests** for every critical user flow (login, device pairing, cross-device conversation)
- ✅ **Security tests** for every endpoint handling auth or sensitive data

## Mandatory security tests

- 🔒 No hardcoded secrets — checked in CI with `gitleaks` or `trufflehog`
- 🔒 Input validation at boundaries (Pydantic schemas, Zod schemas)
- 🔒 SQL injection / XSS tests on forms
- 🔒 Rate-limiting tests on public endpoints
- 🔒 Dependency audit: `pip-audit`, `npm audit`, `osv-scanner`

## CI / CD

```yaml
# .github/workflows/ci.yml — simplified
on: [push, pull_request]
jobs:
  test:
    steps:
      - lint        # ruff, eslint, prettier
      - typecheck   # mypy, tsc
      - unit        # pytest, vitest
      - integration # with services in containers
      - e2e         # playwright (only on PRs to release branches)
      - security    # gitleaks, pip-audit
```

## Writing a good test

- 🎯 One test = one behaviour
- 📛 Naming: `test_<component>_<action>_<expected>`
- 🧱 Clear and visible **Arrange / Act / Assert**
- 🚫 No tests that depend on execution order
- 🚫 No arbitrary sleeps — use fixtures and explicit awaits
- 🪪 Every test cleans up after itself (rollback transactions, ephemeral containers)

## Mock strategy for device agents

Integrations with physical devices (Frame, OctoPrint, smartwatches) require **two levels**:

1. **Contract test** on the client → HTTP mock of the remote server
2. Optional **smoke test** on real hardware → run locally by whoever develops that device-agent, not in CI

## Example: server integration test

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

## References

- [Conventional Commits](https://www.conventionalcommits.org/)
- [pytest documentation](https://docs.pytest.org/)
- [Playwright](https://playwright.dev/)
