# Contribuire al progetto

Jarvis è un progetto **open source community-driven**. Ogni contributo conta.

## Modi per contribuire

<div class="grid cards" markdown>

- :material-bug:{ .lg .middle } **Segnalare bug**

    ---

    Apri una [GitHub issue](https://github.com/fedcal/open-jarvis/issues) con un caso di riproduzione minimale.

- :material-lightbulb:{ .lg .middle } **Proporre feature**

    ---

    Apri una [discussion](https://github.com/fedcal/open-jarvis/discussions) prima di scrivere codice, soprattutto per idee importanti.

- :material-book-edit:{ .lg .middle } **Migliorare la documentazione**

    ---

    Refusi, esempi mancanti, traduzioni IT ↔ EN.

- :material-translate:{ .lg .middle } **Aggiungere una lingua**

    ---

    Oggi supportiamo IT + EN. Ogni nuova lingua è benvenuta.

- :material-puzzle:{ .lg .middle } **Costruire un plugin**

    ---

    Vedi `plugins/_template/` per lo scaffold di partenza.

- :material-watch-vibrate:{ .lg .middle } **Integrare un device**

    ---

    Wearable, occhiali, display olografici. Vedi `agents/`.

- :material-test-tube:{ .lg .middle } **Scrivere test**

    ---

    Unit, integration, E2E. Obiettivo: 80%+ di copertura.

- :material-shield-check:{ .lg .middle } **Audit di sicurezza**

    ---

    Le segnalazioni di sicurezza vanno via email, non in issue pubbliche.

</div>

## Workflow

1. **Fork** del repository
2. **Branch** descrittivo (`feat/...`, `fix/...`, `docs/...`)
3. **Commit** con [Conventional Commits](https://www.conventionalcommits.org/)
4. **Push** + **Pull Request** verso `main`
5. **Code review** + merge

Il dettaglio completo è nel file [CONTRIBUTING.md](https://github.com/fedcal/open-jarvis/blob/main/CONTRIBUTING.md).

## Regole d'oro

- **File piccoli** > file grandi (200–400 righe tipico)
- **Strutture immutabili** per default
- **Gestione esplicita degli errori**
- **Validazione input** ai confini del sistema
- **Mai segreti hardcoded** — `.env` è sempre gitignored
- **Commenti solo quando il *perché* non è ovvio**

## Codice di condotta

Il progetto adotta il [Contributor Covenant](https://github.com/fedcal/open-jarvis/blob/main/CODE_OF_CONDUCT.md). Comportamenti rispettosi e inclusivi sono attesi da tutti.

## Riconoscimento

Ogni contributore viene elencato nel README e nella documentazione. Il tuo lavoro conta.

---

> "Non aspettare il permesso. Apri una PR."
> — Una verità del software open source
