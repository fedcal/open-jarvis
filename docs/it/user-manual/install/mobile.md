---
title: "Installazione mobile · iOS · Android"
description: "Installa l'app Open-Jarvis su iPhone (iOS 17+), iPad e Android (10+)."
---

# Installazione mobile

L'app mobile Jarvis è il principale punto di interazione cross-device: voice input, push notifications, biometric data, GPS-aware routing.

## iOS / iPadOS

### Requisiti

- iOS 17 o superiore (iPhone XS+, iPad 6+)
- 80 MB spazio disco

### Installazione

**Opzione A — App Store** (quando disponibile):

1. Cerca **"Open Jarvis"** sull'App Store
2. Tap **"Ottieni"**

**Opzione B — TestFlight beta:**

1. Apri il link beta: <https://testflight.apple.com/join/JARVIS-BETA>
2. Installa TestFlight se non presente
3. Accetta l'invito beta e installa

**Opzione C — AltStore PAL** (Europa, sideloading):

1. Installa AltStore PAL
2. Aggiungi la sorgente `https://altstore.federicocalo.dev`
3. Installa Jarvis dalla sorgente

### Pairing

1. Apri **Jarvis** → **Connetti il tuo server**
2. Scegli:
   - **QR code** dal server desktop
   - **Inserisci URL** manualmente: `https://jarvis.tuodominio.com`
3. Login con email + password + 2FA
4. Conferma la creazione del device sul server (notifica push al desktop)

### Permessi richiesti

| Permesso | Funzione |
|---|---|
| Notifiche | Push da Jarvis (briefing, alert, risposte) |
| Microfono | Wake-word "Hey Jarvis", input vocale |
| Fotocamera | Analisi visiva, scan QR |
| Posizione | Routing context-aware (auto, casa, palestra) |
| HealthKit | Lettura dati biometrici Apple Watch / iPhone |
| Bluetooth | Pairing wearable e occhiali smart |
| HomeKit | Controllo smart home (opzionale) |
| Apple Music / Spotify | Controllo playback (opzionale) |

### App Intents per Siri

L'app espone App Intents alle Shortcuts di iOS. Esempi:

- "Hey Siri, **briefing di Jarvis**" → apre la chat con il briefing
- "Hey Siri, **chiedi a Jarvis** quando ho la prossima riunione"
- Scorciatoie personalizzate dalla **app Comandi**

### Live Activities + Widget

- Widget home screen: stato Jarvis, quick actions
- Live Activity: briefing in corso, conversazione attiva, alert biometrici
- Lock Screen widget per device pairing rapido

### Apple Watch companion

Installando Jarvis su iPhone, l'app Watch viene installata automaticamente:

- Tile principale per quick chat
- Complication per stato Jarvis (online/offline/listening)
- Wake-word "Hey Jarvis" via "double tap" o "raise to speak"

## Android

### Requisiti

- Android 10 (API 29) o superiore
- 100 MB spazio disco
- Google Play Services (per FCM push)

### Installazione

**Opzione A — Google Play Store:**

1. Cerca **"Open Jarvis"** sul Play Store
2. Tap **Installa**

**Opzione B — F-Droid (build privacy-focused):**

1. Installa F-Droid se non presente
2. Aggiungi repo: `https://fdroid.federicocalo.dev/repo`
3. Installa **Jarvis (Open Source)**

**Opzione C — APK diretto (sideload):**

```bash
# Da computer:
adb install jarvis-android.apk
```

Oppure scarica `jarvis-android.apk` da [Releases](https://github.com/fedcal/open-jarvis/releases) e abilita "Origini sconosciute" su Android.

### Pairing

Identico a iOS.

### Permessi Android

Android consente automazioni più profonde:

| Permesso | Funzione |
|---|---|
| RECORD_AUDIO | Wake-word + voice input |
| FOREGROUND_SERVICE | Wake-word always-on |
| ACCESS_FINE_LOCATION | Geofencing |
| HEALTH_CONNECT | Lettura dati Health Connect |
| BLUETOOTH_CONNECT | Pairing wearable |
| ACCESSIBILITY_SERVICE | Wake-word avanzato (opzionale) |
| SYSTEM_ALERT_WINDOW | Floating chat overlay |

### Wake-word always-on

Per "Hey Jarvis" sempre attivo:

1. **Impostazioni Android → App → Jarvis → Batteria → Senza restrizioni**
2. **Impostazioni Jarvis → Wake-word → Always on**

Consumo ~3-5 mA in standby.

### Tasker integration

Jarvis espone un **MCP Server** invocabile da Tasker:

```yaml
# Esempio task Tasker
trigger: "context: in_car"
action:
  - jarvis_mcp:
      command: announce
      params: { text: "Modalità auto attiva" }
  - mute_notifications: true
  - launch: "Google Maps"
```

### Wear OS

Su Wear OS la Jarvis Tile mostra:

- Stato connessione
- Pulsante "Ascolta" (bypassa wake-word)
- Quick view biometrica

Installa la Tile da:

- **App Jarvis Wear OS** dal Play Store sull'orologio
- Oppure dal companion phone: **Jarvis → Wear OS → Sync**

### KDE Connect bridge

L'app si integra con KDE Connect (se installato) per sync con desktop Linux:

- 📋 Clipboard automatico
- 📁 Send file via condividi
- 🔔 Notifiche desktop dal telefono

## Aggiornamenti

- iOS / Android: aggiornamento automatico tramite store
- F-Droid: notifica manuale, esegui aggiornamento dal repo
- APK sideload: scarica nuova release manualmente

## Disinstallazione

Standard rimozione app del sistema operativo. Prima di disinstallare:

1. Apri Jarvis → **Impostazioni → Account → Revoca questo dispositivo**
2. Solo dopo rimuovi l'app

In questo modo il server invalida i token e il device pairing.
