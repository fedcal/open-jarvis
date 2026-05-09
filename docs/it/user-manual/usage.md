# Utilizzo quotidiano

Una volta installato e configurato, ecco come **vivere quotidianamente** con Jarvis.

## Le tre modalità di interazione

| Modalità | Quando | Come |
|---|---|---|
| 🗨️ **Chat** | Compiti articolati, ragionamento, ricerca | Web UI o app mobile |
| 🎙️ **Voce** | In movimento, hands-free, smartwatch | Wake-word "Hey Jarvis" |
| 👆 **Quick action** | Comandi singoli, automazioni | Notifica push, gesture watch, shortcut OS |

## Conversazioni cross-device

La conversazione **non è legata al dispositivo**: è legata a te.

Esempio:

1. Ore 9:00 — al PC chiedi "trovami articoli sul nuovo modello Claude di novembre"
2. Ore 13:00 — al ristorante, chiedi al telefono: "rimandami quei due articoli per stasera"
3. Ore 22:00 — sul divano, sul tablet: "leggimi il primo, fai un riassunto"

Jarvis sa che è la **stessa conversazione** e mantiene il contesto.

## Routing automatico

Jarvis sceglie il device più adatto al contesto:

| Situazione | Device scelto | Motivo |
|---|---|---|
| Stai correndo | Smartwatch | hands-free, vibrazione |
| Sei alla guida | Auto / mobile + glasses | TTS + overlay AR |
| Sei al PC | Desktop | task complessi, IDE |
| Stai dormendo | Nessuno | Do Not Disturb |
| Sei in riunione | Notifiche soppresse | Focus mode |

Puoi forzare il routing con `@desktop`, `@mobile`, `@watch`.

## Funzionalità giornaliere

### Briefing quotidiano

Chiedi al mattino: *"dammi il briefing"*. Riceverai:

- 📰 Top 3 notizie del giorno (vedi [News](../features/news.md))
- 📅 Agenda con eventi e priorità
- 💼 Statistica finanziaria (saldo, variazioni significative)
- 🏃 Stato salute (recovery, sleep score)
- ⏰ Reminder e deadlines imminenti

### Memoria personale

Tutto quello che dici a Jarvis viene memorizzato (con il tuo consenso).

```
Tu: "Ricordati che il mio compleanno è il 15 marzo"
Jarvis: "Memorizzato in long-term."

[mesi dopo]
Tu: "Quando è il mio compleanno?"
Jarvis: "Il 15 marzo. Vuoi che ti suggerisca delle attività?"
```

Per dimenticare:

```
Tu: "Dimentica le mie preferenze su ristoranti vegetariani"
```

### Domande sui tuoi documenti (RAG)

Se hai connesso Obsidian / Notion / Drive (vedi [RAG](../features/rag.md)):

```
Tu: "Quando ho preso quegli appunti sulle architetture serverless?"
Jarvis: "Hai una nota del 12 marzo nel vault Obsidian, cartella 'work/architettura'."
```

### Comandi vocali utili

- "Hey Jarvis, **ricordami** di chiamare il dottore alle 16:00"
- "Hey Jarvis, **timer** di 25 minuti"
- "Hey Jarvis, **luci** del salotto al 30%"
- "Hey Jarvis, **traduci** 'have a nice day' in francese"
- "Hey Jarvis, **come ho dormito** questa notte?"
- "Hey Jarvis, **qual è il mio net worth** crypto?"

## Privacy e controllo

- 🔇 **Mute totale**: triplo tap sul logo nell'app — Jarvis non ascolta più finché non riattivi
- 🌙 **Modalità notte**: niente notifiche dalle 22:00 alle 7:00
- 🚫 **Modalità ospiti**: i nuovi device non possono essere registrati
- 🗑️ **Diritto all'oblio**: pulsante "Cancella tutto" dalle impostazioni

## Configurazioni avanzate

- [Plugin marketplace](../features/developer.md) — installa skill specifiche
- [Smart home](../integrations/other-systems.md) — abilita Home Assistant
- [Maker](../features/maker.md) — collega Blender e stampanti 3D

> Hai problemi? Vai a → [Risoluzione problemi](troubleshooting.md)
