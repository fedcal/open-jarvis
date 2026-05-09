# Contributing to Jarvis · Contribuire a Jarvis

> 🇬🇧 [English](#-english) · 🇮🇹 [Italiano](#-italiano)

---

## 🇬🇧 English

First of all: **thank you!** 🙏 Jarvis is an open-source community project. Every contribution — code, documentation, bug reports, ideas — helps make a private, distributed, personal AI a reality.

### Code of Conduct

This project adheres to the [Contributor Covenant](./CODE_OF_CONDUCT.md). By participating you agree to uphold it.

### Ways to contribute

- 🐛 **Report bugs** — open a [GitHub issue](https://github.com/fedcal/open-jarvis/issues) with a reproduction case.
- 💡 **Propose features** — open a [discussion](https://github.com/fedcal/open-jarvis/discussions) before writing code, especially for big ideas.
- 📖 **Improve documentation** — typos, clearer explanations, missing examples, translations (IT ↔ EN).
- 🌍 **Add a new language** — Jarvis docs are bilingual today (IT + EN). Other languages are welcome.
- 🧩 **Build a plugin** — see `plugins/_template/` for the scaffold.
- 🔌 **Integrate a new device** — wearables, smart glasses, holographic displays. See `agents/`.
- 🧪 **Write tests** — unit, integration, E2E. We aim at 80%+ coverage.

### Development workflow

1. **Fork** the repository on GitHub.
2. **Clone** your fork:
   ```bash
   git clone git@github.com:YOUR_USERNAME/open-jarvis.git
   cd open-jarvis
   ```
3. **Create a branch** with a descriptive name:
   ```bash
   git checkout -b feat/oura-integration
   git checkout -b fix/voice-agent-crash
   git checkout -b docs/it-architecture
   ```
4. **Make your changes**, following the conventions below.
5. **Commit** using [Conventional Commits](https://www.conventionalcommits.org/):
   ```
   feat(medical): add Oura Ring API client
   fix(voice): handle empty audio buffer
   docs(it): translate architecture overview
   refactor(memory): extract vector store interface
   ```
6. **Push** and open a **Pull Request** against `main`.

### Pull Request checklist

- [ ] My branch is up to date with `main`
- [ ] My commits follow Conventional Commits
- [ ] I have added/updated tests where needed
- [ ] I have updated documentation (both IT and EN if user-facing)
- [ ] I have run linters and formatters locally
- [ ] My PR description explains **what** changed and **why**

### Code style

- **Many small files** over few large ones (200–400 lines typical, 800 max).
- **Immutable data structures** by default.
- **Explicit error handling** at every boundary.
- **Validate input** at system boundaries (user, external APIs).
- **No hardcoded secrets** — use `.env` files (see `.env.example`).
- Comments only when the *why* is non-obvious.

### Testing

- New features ship with tests.
- Bug fixes ship with a regression test.
- Aim at 80%+ coverage.
- Use the testing stack appropriate to the language (`pytest`, `vitest`, `jest`, `playwright`).

### Documentation

- The site lives under `docs/` and is built with **MkDocs Material**.
- IT and EN are kept in sync. If you change one, please update the other (or open a follow-up issue tagged `i18n`).
- Run `mkdocs serve` locally to preview.

### Reporting security issues

**Do not** open a public issue for security vulnerabilities. Email Federico at the address listed on [federicocalo.dev](https://federicocalo.dev) with the details.

### Recognition

Every contributor is listed in the README and in the docs **Contributors** page. Your work matters.

---

## 🇮🇹 Italiano

Prima di tutto: **grazie!** 🙏 Jarvis è un progetto open source community-driven. Ogni contributo — codice, documentazione, segnalazione di bug, idee — aiuta a rendere reale un'AI personale, privata e distribuita.

### Codice di condotta

Il progetto adotta il [Contributor Covenant](./CODE_OF_CONDUCT.md). Partecipando ti impegni a rispettarlo.

### Modi per contribuire

- 🐛 **Segnalare bug** — apri una [GitHub issue](https://github.com/fedcal/open-jarvis/issues) con un caso di riproduzione.
- 💡 **Proporre feature** — apri una [discussion](https://github.com/fedcal/open-jarvis/discussions) prima di scrivere codice, soprattutto per idee grosse.
- 📖 **Migliorare la documentazione** — refusi, spiegazioni più chiare, esempi mancanti, traduzioni (IT ↔ EN).
- 🌍 **Aggiungere una nuova lingua** — oggi la documentazione è bilingue (IT + EN). Altre lingue sono benvenute.
- 🧩 **Costruire un plugin** — vedi `plugins/_template/` per lo scaffold.
- 🔌 **Integrare un nuovo dispositivo** — wearable, occhiali smart, display olografici. Vedi `agents/`.
- 🧪 **Scrivere test** — unit, integration, E2E. L'obiettivo è 80%+ di copertura.

### Workflow di sviluppo

1. **Fork** del repository su GitHub.
2. **Clone** del tuo fork:
   ```bash
   git clone git@github.com:TUO_USERNAME/open-jarvis.git
   cd open-jarvis
   ```
3. **Crea un branch** con un nome descrittivo:
   ```bash
   git checkout -b feat/oura-integration
   git checkout -b fix/voice-agent-crash
   git checkout -b docs/it-architecture
   ```
4. **Apporta le modifiche** seguendo le convenzioni qui sotto.
5. **Commit** usando [Conventional Commits](https://www.conventionalcommits.org/):
   ```
   feat(medical): aggiunto client per Oura Ring API
   fix(voice): gestione del buffer audio vuoto
   docs(it): traduzione overview architettura
   refactor(memory): estratta l'interfaccia del vector store
   ```
6. **Push** e apri una **Pull Request** verso `main`.

### Checklist per la Pull Request

- [ ] Il branch è aggiornato con `main`
- [ ] I commit seguono Conventional Commits
- [ ] Ho aggiunto/aggiornato i test dove serve
- [ ] Ho aggiornato la documentazione (sia IT sia EN se user-facing)
- [ ] Ho eseguito linter e formatter in locale
- [ ] La descrizione della PR spiega **cosa** è cambiato e **perché**

### Stile del codice

- **Molti file piccoli** invece di pochi grandi (200–400 righe tipico, 800 massimo).
- **Strutture dati immutabili** per default.
- **Gestione esplicita degli errori** a ogni confine.
- **Validazione degli input** ai confini del sistema (utente, API esterne).
- **Nessun segreto hardcoded** — usa file `.env` (vedi `.env.example`).
- Commenti solo quando il *perché* non è ovvio.

### Test

- Le nuove feature vengono rilasciate con i test.
- I bug fix vengono rilasciati con un test di regressione.
- Obiettivo: 80%+ di copertura.
- Usa lo stack di testing più adatto al linguaggio (`pytest`, `vitest`, `jest`, `playwright`).

### Documentazione

- Il sito vive in `docs/` ed è generato con **MkDocs Material**.
- IT ed EN sono mantenute allineate. Se modifichi una lingua, aggiorna anche l'altra (o apri una issue di follow-up con tag `i18n`).
- Lancia `mkdocs serve` in locale per la preview.

### Segnalare problemi di sicurezza

**Non** aprire una issue pubblica per le vulnerabilità di sicurezza. Scrivi a Federico all'indirizzo presente su [federicocalo.dev](https://federicocalo.dev) con i dettagli.

### Riconoscimento

Ogni contributore è elencato nel README e nella pagina **Contributors** della documentazione. Il tuo lavoro conta.

---

<div align="center">

**Maintained by [Federico Calò](https://federicocalo.dev) · [federicocalo.dev](https://federicocalo.dev)**

</div>
