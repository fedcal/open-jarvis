# Dispositivi

Jarvis è progettato per vivere su una **mesh di dispositivi**. Ogni device ha un agente locale e capacità specifiche.

## Desktop / Laptop

**Sistemi:** Linux, macOS, Windows.

**Capacità:**

- accesso al filesystem
- esecuzione di comandi shell
- integrazione IDE (VS Code, JetBrains, Vim/Neovim)
- coding assistant
- automazioni con LLM grandi

**Stack di riferimento:** Python 3.12, Tauri o Electron per UI.

## Smartphone

**Sistemi:** iOS, Android.

**Capacità:**

- notifiche push
- GPS / geofencing
- fotocamera (analisi visiva)
- microfono (input vocale)
- voice assistant naturale

**Stack di riferimento:** React Native o Flutter, Android Health Connect, Apple HealthKit.

## Smartwatch

**Sistemi supportati:**

- **Apple Watch** — solo dati passivi via HealthKit (Siri lock-in)
- **Wear OS** — Pixel Watch, Galaxy Watch — Health Connect
- **Garmin** — Connect IQ SDK
- **PineTime + InfiniTime** — open hardware, completamente hackerabile via BLE
- **Bangle.js 2** — programmabile in JavaScript da browser

**Capacità:**

- dati biometrici (HR, HRV, sleep)
- notifiche rapide
- wake-word (Porcupine on-device)
- gesture interaction

## Occhiali smart / AR

| Device | SDK | Licenza | Note |
|---|---|---|---|
| **Brilliant Labs Frame** | Python / Flutter | MIT | Massima apertura, BLE-native, Lua on-device |
| **MentraOS** (Mach1, Vuzix Z100, G1) | TypeScript | Open source | OS cross-hardware, app store integrato |
| **XREAL Air** | Unity / Android | Proprietary | Hand tracking, spatial anchors |
| **Meta Ray-Ban** | Wearables Toolkit | Proprietary | GA 2026, accesso controllato |

**Capacità tipiche:** overlay visivi, navigazione, riconoscimento ambientale, real-time information.

## Visori VR

**Standard:** OpenXR (Khronos Group) — cross-vendor, royalty-free.

**Runtime open source:** **Monado** (Linux-native).

**Headset supportati via OpenXR:**

- **Meta Quest** (Meta OpenXR SDK)
- **Valve Index** (via Monado o SteamVR)
- **Pico** (OpenXR 1.1 compliant)
- **Varjo** (quad-view OpenXR)

## Display olografici

| Device | SDK | Note |
|---|---|---|
| **Looking Glass Factory** | Core SDK pubblico (Unity/Unreal) | SID 2026 Display of the Year |
| **Voxon Photonics** | C++ / Python SDK | Vero output volumetrico |
| **HYPERVSN** | Proprietary | Presenza ambientale |

## Wearable medicali

API consumer health & medical:

- **Oura Ring v2** — sleep, HRV, readiness, SpO2 (OAuth 2.0)
- **Whoop v2** — strain, recovery, sleep (OAuth 2.0 + webhook)
- **Polar AccessLink** — training, HR, sleep
- **Garmin Health API** — HRV, VO2max, stress (OAuth 1.0a)
- **Withings** — peso, HR, ECG (OAuth 2.0)
- **Fitbit / Google Health API** — migrazione completa entro settembre 2026
- **Dexcom CGM** — glucosio in tempo reale, FDA-cleared

**Aggregatori open source:**

- **Open Wearables** — middleware unificato per Apple/Garmin/Polar/Suunto/Whoop/Oura
- **Wearipedia** — wrapper di ricerca Stanford

**Standard di interoperabilità:** HL7 FHIR R4/R5, SMART on FHIR, HAPI FHIR server.
