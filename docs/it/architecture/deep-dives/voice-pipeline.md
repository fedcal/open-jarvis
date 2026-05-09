---
title: "Deep-dive · Voice Pipeline cross-device"
description: "Approfondimento tecnico sulla pipeline vocale di Open-Jarvis: latency budget, wake-word, STT, TTS, orchestrazione, edge deployment su smartwatch e occhiali."
keywords: "voice pipeline, wake-word Porcupine, faster-whisper, Piper TTS, Kokoro, latency budget, barge-in, edge deployment"
---

# Deep-dive · Voice Pipeline cross-device

**Versione librerie:** maggio 2026
**Target latenza end-to-end:** < 1.5 secondi
**Phase:** 2 ([tracker](https://github.com/fedcal/open-jarvis/issues/11))

> Questa pagina è il deep-dive tecnico della voice pipeline di Open-Jarvis. Per la vista user-facing vedi [Funzionalità voce](../../features/developer.md#voice-agent).

## 1. Latency budget end-to-end

La conversazione naturale richiede una finestra di risposta di 300-500ms per non sembrare "lenta". Per Jarvis, con pipeline distribuita multi-device, il target è **< 1.5s di latenza totale percepita** dall'utente.

| Fase | Budget | Cumulativo |
|---|---|---|
| Wake-word detection | < 50 ms | 50 ms |
| VAD + audio capture (buffering) | < 100 ms | 150 ms |
| STT streaming (first token) | < 400 ms | 550 ms |
| LLM inference (TTFT) | < 700 ms | 1250 ms |
| TTS first audio chunk | < 150 ms | 1400 ms |
| Network overhead (BLE/WiFi) | < 100 ms | 1500 ms |

### Edge cases e degradazione graceful

**Rete lenta (RTT > 200ms):** wake-word rimane on-device, STT commuta su Vosk locale (`vosk-model-small-it-0.22`, ~50MB), LLM cade su Llama 3.2 3B Q4_K_M via llama.cpp, TTS resta su Piper locale.

**GPU offload assente:** faster-whisper `base.en` con `int8` (RTF ~0.04 su CPU 8-core). Per LLM: quantizzazione Q4_K_M con TTFT ~900ms.

**Smartwatch standalone:** pipeline completamente on-device con microWakeWord o Porcupine on-device, comandi predefiniti, risposte precompilate.

## 2. Wake-word detection

### 2.1 Picovoice Porcupine 3.x

Motore wake-word maturo per embedded. SDK v3 (mag 2026) supporta Python, Android, iOS, Web (WASM), C, .NET, Flutter, React Native.

**Caratteristiche:**

- Latenza < 50ms (tipicamente 20-30ms)
- Consumo ~2-5% CPU su ARM Cortex-M7 a 216 MHz
- Supporto MCU (STM32F7, nRF52840, ESP32-S3 via C SDK)
- Wear OS: gira in `ForegroundService` persistente
- Custom wake-word via Picovoice Console (25 registrazioni da 5 speaker, training ~5 min)

```python
# requirements: pvporcupine==3.0.2, pvrecorder==1.2.3
import pvporcupine
import pvrecorder
import struct
from collections import deque
from pathlib import Path

class WakeWordDetector:
    """Detector Porcupine con buffer circolare pre-roll (250ms)."""

    SENSITIVITY = 0.6
    PRE_ROLL_FRAMES = 8

    def __init__(self, access_key: str, keyword_path: Path | None = None):
        self._porcupine = pvporcupine.create(
            access_key=access_key,
            keywords=["jarvis"] if keyword_path is None else [],
            keyword_paths=None if keyword_path is None else [str(keyword_path)],
            sensitivities=[self.SENSITIVITY],
        )
        self._recorder = pvrecorder.PvRecorder(
            frame_length=self._porcupine.frame_length, device_index=-1
        )
        self._pre_roll: deque[bytes] = deque(maxlen=self.PRE_ROLL_FRAMES)

    def listen_once(self) -> list[bytes]:
        """Blocca fino al wake-word. Restituisce i frame pre-roll."""
        self._recorder.start()
        try:
            while True:
                pcm_frame = self._recorder.read()
                self._pre_roll.append(struct.pack("h" * len(pcm_frame), *pcm_frame))
                if self._porcupine.process(pcm_frame) >= 0:
                    return list(self._pre_roll)
        finally:
            self._recorder.stop()
```

**Power consumption:**

- Wear OS (Snapdragon W5+ Gen 1) Porcupine in ForegroundService: ~3-5 mA in ascolto continuo. Con batteria 300mAh, durata ~60-80h.
- Strategia "listen-on-wrist-raise": mic attivo solo dopo gesto rilevato dall'accelerometro (consumo medio < 0.5 mA).
- Brilliant Frame (nRF52840): interrupt hardware ADC sveglia processore solo sopra soglia acustica (< 1 mA standby).

### 2.2 openWakeWord 0.6.x

Alternativa open source (Apache 2.0). Backbone condiviso Google + classificatore leggero su sintesi TTS.

Training pipeline (`CoreWorxLab/openwakeword-training`) genera modelli ONNX ~200KB. Custom wake-word in ~30 min su CPU con 1000 esempi sintetici Piper.

Limite: tasso falsi positivi ~3x rispetto a Porcupine in ambiente rumoroso.

### 2.3 microWakeWord per ESP32-S3

Per dispositivi ESP32-S3 con ESPHome ≥ 2024.7. Modelli TFLite INT8, fino a 4 simultanei con PSRAM. Inferenza 10ms.

**Use case Jarvis:** satellite hardware low-cost (ESP32-S3 + MEMS I2S + speaker) per ogni stanza, trasmette audio raw via WebSocket WiFi al server principale.

## 3. Speech-to-Text

### 3.1 faster-whisper 1.1.x (CTranslate2 4.x)

Reimplementa Whisper via CTranslate2: speedup 4-8x e minore VRAM rispetto all'originale.

**Benchmark RTX 3090, mag 2026:**

| Modello | VRAM | WER en | RTF GPU | RTF CPU int8 |
|---|---|---|---|---|
| `tiny.en` | ~1GB | ~12% | 0.006 | 0.03 |
| `base.en` | ~1GB | ~8% | 0.009 | 0.04 |
| `medium.en` | ~5GB | ~4% | 0.02 | 0.15 |
| `large-v3-turbo` | ~6GB | ~2.5% | 0.03 | N/A |
| `distil-large-v3` | ~3GB | ~3% | 0.02 | 0.12 |

**Profilo Jarvis raccomandato:** `distil-large-v3` con `int8_float16` su GPU. Segmenti da 5s trascritti in ~100-150ms.

```python
# requirements: faster-whisper==1.1.0, silero-vad==5.1.2, websockets==12.0
import asyncio
import io
import websockets
import numpy as np
import soundfile as sf
import torch
from collections import deque
from faster_whisper import WhisperModel

_vad_model, _vad_utils = torch.hub.load(
    repo_or_dir="snakers4/silero-vad", model="silero_vad", onnx=False
)
(_get_speech_timestamps, *_) = _vad_utils

SAMPLE_RATE = 16_000
CHUNK_SAMPLES = int(SAMPLE_RATE * 0.5)
SILENCE_THRESHOLD_S = 1.2

_whisper_model = WhisperModel(
    "distil-large-v3", device="cuda", compute_type="int8_float16"
)


async def stream_transcribe(websocket) -> None:
    """Riceve chunk PCM float32 16kHz, ritorna trascrizioni parziali real-time."""
    audio_buffer: deque[np.ndarray] = deque()
    silence_frames = 0
    max_silence = int(SILENCE_THRESHOLD_S / 0.5)

    async for message in websocket:
        chunk = np.frombuffer(message, dtype=np.float32)
        audio_buffer.append(chunk)

        speech_ts = _get_speech_timestamps(
            chunk, _vad_model, sampling_rate=SAMPLE_RATE, threshold=0.5
        )
        silence_frames = 0 if speech_ts else silence_frames + 1

        accumulated = np.concatenate(list(audio_buffer))
        if len(accumulated) >= SAMPLE_RATE * 1.5 or silence_frames >= max_silence:
            buf = io.BytesIO()
            sf.write(buf, accumulated, SAMPLE_RATE, format="WAV")
            buf.seek(0)

            segments, _ = _whisper_model.transcribe(
                buf, beam_size=1, language="it", vad_filter=False
            )
            transcript = " ".join(seg.text.strip() for seg in segments)
            if transcript:
                await websocket.send(transcript)

            if silence_frames >= max_silence:
                audio_buffer.clear()
                silence_frames = 0
                await websocket.send("__END_OF_UTTERANCE__")


async def main() -> None:
    async with websockets.serve(stream_transcribe, "0.0.0.0", 8765):
        await asyncio.Future()
```

### 3.2 Vosk 0.3.45 — fallback offline

Modelli small italiano (`vosk-model-small-it-0.22`) ~50MB, RTF < 0.05 su Raspberry Pi 4. Attivato automaticamente se latency check (ping STT > 500ms) rileva rete degradata.

### 3.3 Coqui STT — deprecato

Coqui AI ha cessato gennaio 2024. Non usare per nuovi progetti. Alternative: Vosk (lightweight kaldi) o faster-whisper (qualità superiore).

## 4. Text-to-Speech

### 4.1 Piper (Open Home Foundation) 1.2.x

TTS locale raccomandato. Architettura VITS, modelli ONNX, 35+ lingue.

| Qualità | Sample rate | First-chunk latency | Modello |
|---|---|---|---|
| `x_low` | 16kHz | 20-30ms | ~5MB |
| `medium` | 22.05kHz | 60-80ms | ~60MB |
| `high` | 22.05kHz | 120-150ms | ~120MB |

**Profilo Jarvis IT:** `it_IT-paola-medium` o `it_IT-riccardo-x_low`.

```python
# requirements: piper-tts==1.2.0 (OHF fork), sounddevice==0.4.7
import numpy as np
import sounddevice as sd
from piper.voice import PiperVoice
from pathlib import Path


class PiperStreamer:
    """TTS streaming: emette chunk audio mentre il modello genera."""

    SAMPLE_RATE = 22_050
    CHUNK_FRAMES = 1_024  # ~46ms

    def __init__(self, model_path: Path, config_path: Path):
        self._voice = PiperVoice.load(
            str(model_path), config_path=str(config_path), use_cuda=False
        )
        self._stream = sd.OutputStream(
            samplerate=self.SAMPLE_RATE, channels=1, dtype="int16"
        )

    async def speak(self, text: str) -> None:
        self._stream.start()
        try:
            buf = np.array([], dtype=np.int16)
            for audio_bytes in self._voice.synthesize_stream_raw(text):
                chunk = np.frombuffer(audio_bytes, dtype=np.int16)
                buf = np.concatenate([buf, chunk])
                while len(buf) >= self.CHUNK_FRAMES:
                    self._stream.write(buf[: self.CHUNK_FRAMES])
                    buf = buf[self.CHUNK_FRAMES :]
            if len(buf):
                self._stream.write(buf)
        finally:
            self._stream.stop()
```

### 4.2 Kokoro 82M (2025)

Modello TTS open-weight (Apache 2.0) da 82M parametri. Sintetizza in 40-70ms su GPU (RTX 3090: ~210x real-time). Qualità superiore a Piper a paragonabile latenza. Preferibile per server con GPU.

### 4.3 XTTS-v2 (Coqui community fork)

Voice cloning con 3-6s di audio reference. Latency ~300-500ms su GPU. Inadatto al real-time primario, utile per personalizzare la voce di Jarvis.

### 4.4 Voice cloning ethics

Policy in Jarvis:

- Solo il proprietario dell'istanza può clonare la propria voce
- Modelli clonati cifrati con chiave derivata dall'identità utente
- Le voci clonate non vengono mai usate per impersonare terzi
- Vedi linee guida EU AI Act (in vigore dal 2025) sull'audio sintetico

## 5. Orchestrazione della pipeline

### 5.1 Architettura event-driven

```text
mic → [WakeWordDetector] --event:wake_detected-->
      [VAD + AudioCapture] --event:utterance_ready-->
      [STTWorker] --event:transcript_ready-->
      [LLMWorker] --event:response_chunk-->
      [TTSWorker] --event:audio_chunk-->
      speaker
```

```python
# Event bus asyncio in-process
import asyncio
from dataclasses import dataclass
from typing import Any, Callable, Awaitable


@dataclass
class Event:
    topic: str
    payload: Any
    source: str = ""


EventHandler = Callable[[Event], Awaitable[None]]


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventHandler]] = {}

    def subscribe(self, topic: str, handler: EventHandler) -> None:
        self._subscribers.setdefault(topic, []).append(handler)

    async def publish(self, event: Event) -> None:
        handlers = self._subscribers.get(event.topic, [])
        await asyncio.gather(*(h(event) for h in handlers))
```

### 5.2 Interruption handling (barge-in)

Il barge-in è la capacità di interrompere Jarvis mentre parla.

**Requisiti:**

1. **Echo cancellation (AEC)**: il microfono non deve "sentire" l'audio dello speaker. Linux: `pulseaudio` + `module-echo-cancel` (WebRTC AEC3). Embedded: chip MEMS con AEC HW (ES8388, INMP441+DSP).
2. **VAD durante riproduzione**: Silero continua a girare, dopo AEC se rileva parlato → emette `barge_in_detected`.
3. **Cancellazione immediata**: il TTSWorker stops, svuota buffer LLM, riavvia da VAD.

```python
class InterruptibleTTSWorker:
    def __init__(self, bus: EventBus, streamer: PiperStreamer) -> None:
        self._bus = bus
        self._streamer = streamer
        self._playing = asyncio.Event()
        self._interrupted = asyncio.Event()
        bus.subscribe("barge_in_detected", self._on_barge_in)

    async def _on_barge_in(self, event: Event) -> None:
        if self._playing.is_set():
            self._interrupted.set()

    async def speak(self, text: str) -> None:
        self._playing.set()
        self._interrupted.clear()
        speak_task = asyncio.create_task(self._streamer.speak(text))
        interrupt_task = asyncio.create_task(self._interrupted.wait())

        _, pending = await asyncio.wait(
            {speak_task, interrupt_task}, return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()
        self._playing.clear()
```

### 5.3 Multi-speaker detection

Per ambienti con più persone: pyannote.audio 4.0 (`pyannote/speaker-diarization-community-1`).

Pipeline real-time:

1. Segmenta flusso in finestre 2s overlap 50%
2. Estrae embedding ECAPA-TDNN
3. Compara con vettore voce proprietario (Qdrant)
4. Similarità coseno > 0.82 → processa; altrimenti ignora

Latenza diarizzazione real-time: 80-150ms per segmento.

## 6. Edge deployment

### 6.1 Architettura on-device + offload

```text
┌──────────────────── EDGE (watch/glasses) ────────────────────┐
│ [mic] → [microWakeWord/Porcupine on-device]                 │
│   wake → [AEC HW] → [Silero VAD ONNX] → [PCM buffer]        │
│   utterance ready → [BLE/WiFi WebSocket] ──────────────►   │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────── SERVER ─────────────────────────────┐
│ [WS recv] → [STT faster-whisper] → [LLM] → [TTS Kokoro]    │
│ → [WS send audio chunks] ─────────────────────────────►    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────── EDGE (watch/glasses) ────────────────────┐
│ [WS recv] → [speaker / haptic]                              │
└──────────────────────────────────────────────────────────────┘
```

### 6.2 BLE Frame audio offload protocol

Quando WiFi non disponibile (es. Brilliant Frame BLE-only):

```text
Frame BLE Audio (max 244 bytes per MTU BT 5.2):
┌────────┬──────────┬────────┬────────────────────────┐
│ 1 byte │ 2 bytes  │ 1 byte │ fino a 240 bytes       │
│ type   │ seq_num  │ flags  │ payload (PCM mu-law)   │
└────────┴──────────┴────────┴────────────────────────┘

type:  0x01 audio chunk · 0x02 end_of_utterance · 0x03 cancel
flags: bit0 is_last_frame · bit1 vad_active
```

Audio compresso mu-law (G.711) 8kHz mono → 64kbps, compatibile con BLE 2M PHY (~1.4 Mbps). Server decomprime e upsampling a 16kHz prima dello STT.

### 6.3 Power-aware mic management

```python
class PowerAwareMicController:
    INACTIVITY_TIMEOUT_S = 30.0
    WRIST_RAISE_THRESHOLD_G = 0.8

    async def run_power_loop(self) -> None:
        last_activity = time.monotonic()
        mic_active = False

        async for sensor_event in self._sensor_stream():
            if sensor_event.type == "wrist_raise" and not mic_active:
                await self._activate_mic()
                mic_active = True
            if sensor_event.type in ("wrist_raise", "wake_word_detected"):
                last_activity = time.monotonic()

            if mic_active and (time.monotonic() - last_activity) > self.INACTIVITY_TIMEOUT_S:
                await self._deactivate_mic()
                mic_active = False
```

### 6.4 Wear OS Tile per controllo vocale

Tile con tre pulsanti:

- "Ascolta" → attiva mic e bypassa wake-word
- "Muto" → silenzia Jarvis per N minuti
- "Stato" → latenza last-request + modalità (online/offline)

API Tiles 1.4 (Wear OS 4.0+). Update ogni 30 min via `TileService.getUpdater()`. Comunicazione con `WatchAgent` via `ChannelClient` (Wearable Data Layer API).

## 7. Stack finale (mag 2026)

| Componente | Libreria · Versione | Licenza |
|---|---|---|
| Wake-word server | pvporcupine 3.0.2 / openWakeWord 0.6.3 | Comm. / Apache 2.0 |
| Wake-word ESP32-S3 | microWakeWord (ESPHome 2025.6) | MIT |
| VAD | silero-vad 5.1.2 | MIT |
| STT primario | faster-whisper 1.1.0 + CTranslate2 4.4.0 | MIT |
| STT fallback | vosk 0.3.45 | Apache 2.0 |
| TTS primario | piper-tts 1.2.0 (OHF fork) | GPL 3.0 |
| TTS GPU | kokoro 82M | Apache 2.0 |
| TTS voice clone | coqui-ai-TTS 0.25.x (idiap fork XTTS-v2) | MPL 2.0 |
| Diarizzazione | pyannote-audio 4.0 + community-1 | MIT |
| Audio I/O | pvrecorder 1.2.3 / sounddevice 0.4.7 | Apache / BSD |
| WebSocket server | websockets 12.0 | BSD |
| Event bus | asyncio stdlib / redis-py 5.2.0 | MIT |

## 8. Note implementative per Jarvis

Il `voice-agent` è strutturato come worker asincroni indipendenti su EventBus. Separazione modulare (wake-word, VAD, STT, LLM, TTS) → sostituire un componente non tocca il resto. Esempio: passare da Piper a Kokoro è solo sostituzione `TTSWorker`.

Il `VoiceAgent` orchestratore leggero: registra worker, gestisce stati FSM (IDLE → LISTENING → PROCESSING → SPEAKING), coordina interruption.

Protocollo edge↔server: WebSocket cifrato TLS 1.3, autenticato con device token emesso da [Identity Layer](identity-memory-llm.md).

## Riferimenti

- [faster-whisper · SYSTRAN](https://github.com/SYSTRAN/faster-whisper)
- [Porcupine docs · Picovoice](https://picovoice.ai/docs/porcupine/)
- [openWakeWord · dscripka](https://github.com/dscripka/openWakeWord)
- [microWakeWord · ESPHome](https://esphome.io/components/micro_wake_word/)
- [Piper TTS](https://github.com/rhasspy/piper)
- [Kokoro-82M · HuggingFace](https://huggingface.co/hexgrad/Kokoro-82M)
- [Silero VAD](https://github.com/snakers4/silero-vad)
- [pyannote community-1](https://www.pyannote.ai/blog/community-1)
- [Whisper large-v3-turbo · OpenAI](https://huggingface.co/openai/whisper-large-v3-turbo)
