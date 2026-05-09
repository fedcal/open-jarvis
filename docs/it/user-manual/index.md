# Manuale utente

Benvenuto nel **manuale utente di Jarvis**: una guida progressiva per **installare**, **configurare** e **utilizzare** il tuo assistente AI personale.

!!! info "Documento vivo"
    Questo manuale è un *living document*: viene aggiornato a ogni release man mano che nuove funzionalità entrano nel sistema. La pagina [Fasi di sviluppo](../roadmap/phases.md) elenca cosa è già disponibile e cosa è in arrivo.

## Struttura del manuale

<div class="grid cards" markdown>

- :material-download:{ .lg .middle } **[Installazione](installation.md)**

    ---

    Tutto quello che serve per portare in piedi il primo nodo Jarvis: requisiti hardware/software, Docker, primo avvio.

- :material-cog:{ .lg .middle } **[Configurazione](configuration.md)**

    ---

    Variabili d'ambiente, OAuth, pairing dei dispositivi, scelta dei modelli LLM, vault dei segreti.

- :material-rocket-launch:{ .lg .middle } **[Utilizzo quotidiano](usage.md)**

    ---

    Come parlare con Jarvis, come spostarsi tra device, come usare le funzionalità di salute, finanza, news, RAG.

- :material-tools:{ .lg .middle } **[Risoluzione problemi](troubleshooting.md)**

    ---

    Errori più comuni, log da consultare, comandi diagnostici, come ripristinare l'istanza.

- :material-help-circle:{ .lg .middle } **[FAQ](faq.md)**

    ---

    Risposte rapide alle domande più frequenti su privacy, costi, dispositivi supportati.

</div>

## Cosa serve sapere prima di iniziare

- 🐳 **Docker** è il modo più semplice di avviare Jarvis. Per tutta la durata di questo manuale assumiamo Docker installato.
- 🔐 Jarvis è **self-hosted**: i tuoi dati restano sul tuo hardware. Tu sei l'amministratore.
- 🌍 Funziona su Linux, macOS e Windows (via WSL2 per Windows).
- 🧪 È in **fase MVP**: alcune funzionalità descritte sono in roadmap. Vedi [Fasi](../roadmap/phases.md).

## Esperienze d'uso tipiche

- **Sviluppatore solitario** che vuole un coding assistant cross-IDE → vedi [Sviluppatore](../features/developer.md)
- **Utente health-tech** con Oura/Whoop e voglia di insight longitudinali → vedi [Salute](../features/health.md)
- **Investitore self-managed** che vuole un dashboard e briefing finanziari → vedi [Finanza](../features/finance.md)
- **Maker / appassionato 3D printing** con stampante connessa → vedi [Maker](../features/maker.md)
- **Knowledge worker** con tante note Obsidian/Notion → vedi [RAG](../features/rag.md)

> Pronto? Comincia da [Installazione →](installation.md)
