---
title: "Modalità di interazione · Voce + Testo"
description: "Open-Jarvis supporta nativamente due modalità di interazione complete: chat testuale (REST/WebSocket) e chat vocale (wake-word + STT + TTS). Sempre interscambiabili."
keywords: "chat testuale, chat vocale, voice chat, text chat, multimodale, REST, WebSocket, wake-word, STT, TTS"
---

# Modalità di interazione

Open-Jarvis supporta nativamente **due modalità di interazione complete e perfettamente interscambiabili**:

<div class="grid cards" markdown>

- :material-keyboard:{ .lg .middle } **💬 Chat testuale**

    ---

    Scrivi a Jarvis da web, mobile, desktop o terminale.
    Risposte streaming via Server-Sent Events o WebSocket.
    Markdown, code block, citazioni, allegati.

- :material-microphone:{ .lg .middle } **🎙️ Chat vocale**

    ---

    Parli a Jarvis con "Hey Jarvis".
    Wake-word on-device → STT streaming → LLM → TTS naturale.
    Latency end-to-end < 1.5s. Funziona offline con Ollama.

</div>

## 🔄 Interscambiabili

Le due modalità **non sono ambienti separati**: condividono la **stessa conversazione**, la **stessa memoria**, lo **stesso routing** verso gli agenti.

Esempi reali:

```text
🌅 Mattina (a casa, in cucina)
   🎙️ Tu (voce): "Hey Jarvis, briefing"
   🎙️ Jarvis (voce): "Buongiorno, hai due meeting oggi…"

🚇 Metro (in treno, con cuffie)
   💬 Tu (testo da mobile): "Riassumi il briefing in 3 punti"
   💬 Jarvis (testo): "1. Meeting con Marco alle 11:00…"

💼 Ufficio (al PC)
   💬 Tu (testo da web): "Apri il documento del progetto X"
   💬 Jarvis (testo): "Ho aperto X.pdf nel tab successivo. Vuoi un riassunto?"

🚗 Sera (in auto)
   🎙️ Tu (voce): "Sì, riassumilo per favore"
   🎙️ Jarvis (voce, attraverso TTS): "Ecco il riassunto…"
```

In una giornata interagisci con Jarvis usando entrambe le modalità senza dover spiegare il contesto: la conversazione è una sola.

## 💬 Chat testuale

### Endpoint REST

Per integrazioni custom o automazioni:

```bash
curl -X POST https://jarvis.tuodominio.com/api/v1/chat \
  -H "Authorization: Bearer $JARVIS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Riassumi i miei impegni di oggi",
    "session_id": "uuid-...",
    "device_id": "uuid-..."
  }'
```

Risposta in streaming Server-Sent Events:

```text
data: {"type":"start","turn_id":"..."}

data: {"type":"chunk","content":"Ecco i tuoi"}
data: {"type":"chunk","content":" impegni di oggi: …"}
data: {"type":"sources","items":[…]}
data: {"type":"end","tokens":{"input":123,"output":456}}
```

### WebSocket per UI interattive

Connessione persistente per chat real-time, typing indicator, interruzione:

```text
ws://jarvis.tuodominio.com/api/v1/chat/ws
```

Vedi [API reference](../architecture/index.md#api) per il dettaglio completo.

### Client supportati

| Client | Tipo | Stato |
|---|---|---|
| Web UI | Browser-native | 🟡 In sviluppo (`feat/frontend-web-text-voice`) |
| App mobile iOS | Native + App Intents | ⚪ Phase 1.x |
| App mobile Android | Native + Tasker MCP | ⚪ Phase 1.x |
| Desktop Tauri | Mac/Win/Linux native | ⚪ Phase 1.x |
| `jarvis` CLI | Terminal | 🟢 v0.1 (basic) |
| Slack / Discord bot | Webhook bridge | ⚪ Phase 5+ |
| Browser extension | Chrome/Firefox | ⚪ Phase 3+ |

## 🎙️ Chat vocale

### Pipeline end-to-end

```text
┌──────────────┐    ┌──────────┐    ┌─────┐    ┌──────────┐    ┌──────┐
│ wake-word    │ →  │ VAD +    │ →  │ STT │ →  │ LLM +    │ →  │ TTS  │
│ on-device    │    │ capture  │    │     │    │ memory   │    │ naturale│
└──────────────┘    └──────────┘    └─────┘    └──────────┘    └──────┘
   < 50 ms          < 100 ms        < 400ms      < 700ms       < 150ms
```

**Target latency end-to-end: < 1.5 secondi.**

### Stack open source

| Layer | Tool | Note |
|---|---|---|
| Wake-word | **Picovoice Porcupine** o **openWakeWord** | On-device, anche su MCU |
| VAD | **Silero VAD** | Voice activity detection |
| STT | **faster-whisper** | Server-side (GPU o CPU int8) |
| TTS | **Piper** o **Kokoro 82M** | Naturale, streaming chunk-by-chunk |

### Wake-word custom

Frase di attivazione predefinita: **"Hey Jarvis"**.

Personalizzabile dalla CLI o UI:

```bash
jarvis voice wake-word train --phrase "Hello assistant"
```

### Interruzione naturale (barge-in)

Mentre Jarvis parla puoi **interromperlo** parlandogli sopra: il TTS si ferma immediatamente, la nuova frase viene catturata. Echo cancellation automatica con AEC hardware o WebRTC AEC3.

### Funziona offline

Con Ollama locale + faster-whisper CPU + Piper, l'intera pipeline gira **senza connessione internet**. Latenza maggiore (~3-5s end-to-end) ma operatività garantita.

## 🔀 Switch tra modalità durante la conversazione

| Da | A | Come |
|---|---|---|
| Voce → Testo | Continua a digitare nella stessa app | Trasparente, conversazione unica |
| Testo → Voce | "Hey Jarvis" o tap mic button | La cronologia testo è visibile a Jarvis |
| Voce su un device → Testo su altro device | Apri Jarvis sul nuovo device | Conversazione sincronizzata via memory layer |

## 🔇 Modalità mute / privacy

Puoi sempre disattivare l'una o l'altra modalità:

- **Solo testo**: `Impostazioni → Voice → Disabilita`. Wake-word non ascolta più.
- **Solo voce**: `Impostazioni → Voice only mode`. Risposte solo audio, niente UI testuale.
- **Mute totale**: triple-tap sul logo nell'app. Jarvis non risponde finché non riattivi.

## 🌐 Multilingue

Entrambe le modalità supportano le stesse lingue:

| Lingua | Testo | Voce (STT) | Voce (TTS) |
|---|---|---|---|
| 🇮🇹 Italiano | ✅ | ✅ | ✅ Piper `it_IT-paola-medium` |
| 🇬🇧 English | ✅ | ✅ | ✅ Piper `en_US-amy-medium` |
| 🇪🇸 Español | ⚪ | ⚪ | ⚪ Phase 9 (i18n) |
| 🇫🇷 Français | ⚪ | ⚪ | ⚪ Phase 9 |
| 🇩🇪 Deutsch | ⚪ | ⚪ | ⚪ Phase 9 |

Vedi [Voice pipeline deep-dive](../architecture/deep-dives/voice-pipeline.md) per il dettaglio tecnico.

## ♿ Accessibilità

Entrambe le modalità sono progettate **WCAG 2.2 AA**:

- 💬 La chat testuale ha live region ARIA, focus trap, font ridimensionabile
- 🎙️ La chat vocale ha trascrizione visibile in tempo reale (anche per chi non sente bene)
- ⌨️ Keyboard navigation completa
- 👁️ Screen reader-friendly (NVDA, VoiceOver, TalkBack, Orca)

Vedi [Mobile-first + WCAG 2.2](../design/mobile-accessibility.md).

## 🛡️ Privacy

| Modalità | Cosa lascia il device |
|---|---|
| Testo (LLM locale Ollama) | Niente |
| Testo (LLM cloud) | Solo il messaggio testuale |
| Voce (server locale + Ollama) | Niente |
| Voce (cloud) | Audio raw + trascrizione (con consenso) |

Wake-word è **sempre on-device**, mai inviato in rete: nessun "ascolto continuo" del cloud.

## 🚀 Quando usare quale modalità?

| Situazione | Consigliata |
|---|---|
| Coding, ricerca approfondita, scrittura | 💬 Testo |
| Mentre cucini, in auto, in palestra | 🎙️ Voce |
| Risposte lunghe da rileggere | 💬 Testo |
| Domande veloci hands-free | 🎙️ Voce |
| In riunione | 💬 Testo (silenzioso) |
| Bambini/anziani | 🎙️ Voce (più accessibile) |
| Privacy massima | 💬 Testo + LLM locale |

## 🔗 Vedi anche

- [Voice pipeline deep-dive](../architecture/deep-dives/voice-pipeline.md)
- [Chat API REST + WebSocket](../architecture/deep-dives/identity-memory-llm.md#chat-api)
- [Devices](../devices/index.md) — quali device supportano quali modalità
- [Mobile-first + WCAG](../design/mobile-accessibility.md)
