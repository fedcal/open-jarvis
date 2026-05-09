# Tests

🇮🇹 Suite di test cross-componente.
🇬🇧 Cross-component test suite.

## Layout

```text
tests/
├── integration/   # Test che attraversano più componenti (server + agente)
└── e2e/           # Test end-to-end (user flow completi)
```

🇮🇹 I test unit-level vivono accanto al codice (`server/tests/`, `agents/desktop-agent/tests/`, ecc.).
🇬🇧 Unit-level tests live next to the code (`server/tests/`, `agents/desktop-agent/tests/`, etc.).

## Obiettivo · Target

🇮🇹 Copertura ≥ 80% su tutti i componenti core.
🇬🇧 Coverage ≥ 80% on every core component.
