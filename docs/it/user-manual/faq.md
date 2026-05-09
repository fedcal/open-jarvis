# FAQ

Risposte rapide alle domande più frequenti.

## Generale

### Jarvis è gratuito?

Sì. Il **codice è MIT** ed è completamente gratuito, anche per uso commerciale. Eventuali costi derivano solo dai provider esterni che scegli (API LLM cloud, hosting, hardware).

### Devo essere uno sviluppatore per usarlo?

In **Fase 0–1** (attuale): sì, devi essere comodo con la riga di comando e Docker.
Da **Fase 2** in avanti: arriverà un installer "one-click" per utenti finali.

### Posso usarlo senza connessione internet?

Parzialmente sì:

- ✅ Memoria, RAG sui tuoi documenti, chat con LLM locali (Ollama) → **offline**
- ❌ News, web search, finance API, sync wearable cloud → **richiedono internet**

### Quanto costa?

| Voce | Costo |
|---|---|
| Software Jarvis | 0 € |
| Hardware (PC casalingo) | da 300 € (NUC riciclato) a 2.000 € (workstation con GPU) |
| LLM cloud (opzionale) | da 5 €/mese (uso leggero) a 50 €/mese (uso pesante) |
| LLM locale (Ollama) | 0 € (già incluso) |
| API wearable (Oura, Whoop) | dipendono dal device, le API sono gratuite |

## Privacy

### I miei dati vanno su un cloud di terze parti?

**Solo se lo decidi tu.** Per default tutto resta sull'hardware che gestisci. Se attivi un provider LLM cloud (es. Anthropic, OpenAI), ogni messaggio inviato al provider segue le sue policy di privacy.

### Posso usare Jarvis al 100% in locale?

Sì:

```env
JARVIS_MODEL_LARGE=ollama/qwen2.5:14b
EMBEDDING_MODEL=ollama/bge-m3
SEARCH_PROVIDER=searxng     # invece di Bing/Google
```

### Jarvis registra audio in continuo?

No. Il **wake-word** è un piccolo modello on-device (Porcupine) che ascolta in locale senza inviare nulla. L'audio passa al server solo dopo l'attivazione di "Hey Jarvis".

### Come cancello tutti i miei dati?

Dall'UI: **Impostazioni → Avanzate → Cancella tutto**.
Da CLI:

```bash
docker compose exec server jarvis user delete --me --confirm
```

## Dispositivi

### Su quali sistemi gira il server?

Linux, macOS, Windows (via WSL2). Anche su **Raspberry Pi 5 / 4 GB**, ma con LLM locali piccoli.

### Quali dispositivi posso pairare?

Vedi la pagina [Dispositivi](../devices/index.md). In sintesi:

- Desktop / laptop (Linux, macOS, Windows)
- Smartphone (iOS 17+, Android 10+)
- Smartwatch (Apple Watch, Wear OS, Garmin, PineTime, Bangle.js)
- Occhiali smart (Brilliant Frame, MentraOS, XREAL)
- Visori VR (Meta Quest, Valve Index, Pico, Varjo)
- Display olografici (Looking Glass, Voxon)
- Wearable medicali (Oura, Whoop, Polar, Garmin, Withings, Fitbit, Dexcom)
- Stampanti 3D (Klipper/Moonraker, OctoPrint, Bambu, Prusa)

### Posso aggiungere un device non in lista?

Sì, scrivendo un agente custom. Vedi [Contribuire](../contributing/index.md) e l'esempio in `agents/_template/`.

## Sicurezza

### Cosa succede se il mio server viene compromesso?

- I segreti sono in `.env` cifrato a riposo (raccomandato LUKS/FileVault)
- Le sessioni utente hanno JWT short-lived (60 minuti)
- I dati biometrici e finanziari possono essere ulteriormente cifrati con chiave per-utente

In caso di compromissione: ruota tutti i token, riemetti i certificati device, audit del log.

### Come posso segnalare una vulnerabilità?

Vedi [SECURITY.md](https://github.com/fedcal/open-jarvis/blob/main/SECURITY.md). **Non aprire issue pubbliche.**

## Roadmap e contributi

### Quando sarà pronta la feature X?

Vedi [Fasi di sviluppo](../roadmap/phases.md). Le date sono indicative — la velocità dipende dai contributori.

### Come posso contribuire?

Vedi [Contribuire](../contributing/index.md). Ogni contributo è benvenuto, anche se non sei sviluppatore: traduzioni, segnalazione bug, idee, test su hardware reale.

### Posso usarlo nel mio prodotto commerciale?

Sì. La licenza MIT lo permette esplicitamente. Apprezziamo (ma non richiediamo) un menzione del progetto.

## Supporto

- 🐛 [GitHub issues](https://github.com/fedcal/open-jarvis/issues) — bug e feature request
- 💬 [GitHub discussions](https://github.com/fedcal/open-jarvis/discussions) — domande e idee
- 🌐 [federicocalo.dev](https://federicocalo.dev) — il sito del maintainer
