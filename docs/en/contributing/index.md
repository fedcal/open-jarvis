# Contributing

Jarvis is an **open-source community-driven** project. Every contribution matters.

## Ways to contribute

<div class="grid cards" markdown>

- :material-bug:{ .lg .middle } **Report bugs**

    ---

    Open a [GitHub issue](https://github.com/fedcal/open-jarvis/issues) with a minimal reproduction.

- :material-lightbulb:{ .lg .middle } **Propose features**

    ---

    Start a [discussion](https://github.com/fedcal/open-jarvis/discussions) before coding, especially for big ideas.

- :material-book-edit:{ .lg .middle } **Improve docs**

    ---

    Typos, missing examples, IT ↔ EN translations.

- :material-translate:{ .lg .middle } **Add a language**

    ---

    We support IT + EN today. New languages are very welcome.

- :material-puzzle:{ .lg .middle } **Build a plugin**

    ---

    See `plugins/_template/` for the starter scaffold.

- :material-watch-vibrate:{ .lg .middle } **Integrate a device**

    ---

    Wearables, glasses, holographic displays. See `agents/`.

- :material-test-tube:{ .lg .middle } **Write tests**

    ---

    Unit, integration, E2E. Target: 80%+ coverage.

- :material-shield-check:{ .lg .middle } **Security audits**

    ---

    Security reports go via email, not in public issues.

</div>

## Workflow

1. **Fork** the repository
2. **Descriptive branch** (`feat/...`, `fix/...`, `docs/...`)
3. **Commits** using [Conventional Commits](https://www.conventionalcommits.org/)
4. **Push** + **Pull Request** against `main`
5. **Code review** + merge

Full details in [CONTRIBUTING.md](https://github.com/fedcal/open-jarvis/blob/main/CONTRIBUTING.md).

## Golden rules

- **Small files** > big files (200–400 lines typical)
- **Immutable structures** by default
- **Explicit error handling**
- **Validate input** at system boundaries
- **Never hardcode secrets** — `.env` is always gitignored
- **Comments only when the *why* is non-obvious**

## Code of Conduct

The project adopts the [Contributor Covenant](https://github.com/fedcal/open-jarvis/blob/main/CODE_OF_CONDUCT.md). Respectful and inclusive behaviour is expected from everyone.

## Recognition

Every contributor is listed in the README and the documentation. Your work matters.

---

> "Don't wait for permission. Open a PR."
> — A truth of open-source software
