# Devices

Jarvis is designed to live on a **device mesh**. Every device runs a local agent and has specific capabilities.

## Desktop / Laptop

**Systems:** Linux, macOS, Windows.

**Capabilities:**

- filesystem access
- shell command execution
- IDE integration (VS Code, JetBrains, Vim/Neovim)
- coding assistant
- automations with large LLMs

**Reference stack:** Python 3.12, Tauri or Electron for UI.

## Smartphone

**Systems:** iOS, Android.

**Capabilities:**

- push notifications
- GPS / geofencing
- camera (visual analysis)
- microphone (voice input)
- natural voice assistant

**Reference stack:** React Native or Flutter, Android Health Connect, Apple HealthKit.

## Smartwatch

**Supported systems:**

- **Apple Watch** — passive data only via HealthKit (Siri lock-in)
- **Wear OS** — Pixel Watch, Galaxy Watch — Health Connect
- **Garmin** — Connect IQ SDK
- **PineTime + InfiniTime** — open hardware, fully hackable via BLE
- **Bangle.js 2** — programmable in JavaScript from the browser

**Capabilities:**

- biometric data (HR, HRV, sleep)
- quick notifications
- wake-word (Porcupine on-device)
- gesture interaction

## Smart glasses / AR

| Device | SDK | License | Notes |
|---|---|---|---|
| **Brilliant Labs Frame** | Python / Flutter | MIT | Maximum openness, BLE-native, on-device Lua |
| **MentraOS** (Mach1, Vuzix Z100, G1) | TypeScript | Open source | Cross-hardware OS, integrated app store |
| **XREAL Air** | Unity / Android | Proprietary | Hand tracking, spatial anchors |
| **Meta Ray-Ban** | Wearables Toolkit | Proprietary | GA 2026, controlled access |

**Typical capabilities:** visual overlays, navigation, environmental awareness, real-time information.

## VR headsets

**Standard:** OpenXR (Khronos Group) — cross-vendor, royalty-free.

**Open-source runtime:** **Monado** (Linux-native).

**OpenXR-compatible headsets:**

- **Meta Quest** (Meta OpenXR SDK)
- **Valve Index** (via Monado or SteamVR)
- **Pico** (OpenXR 1.1 compliant)
- **Varjo** (quad-view OpenXR)

## Holographic displays

| Device | SDK | Notes |
|---|---|---|
| **Looking Glass Factory** | Public Core SDK (Unity/Unreal) | SID 2026 Display of the Year |
| **Voxon Photonics** | C++ / Python SDK | True volumetric output |
| **HYPERVSN** | Proprietary | Ambient presence |

## Medical wearables

Consumer health & medical APIs:

- **Oura Ring v2** — sleep, HRV, readiness, SpO2 (OAuth 2.0)
- **Whoop v2** — strain, recovery, sleep (OAuth 2.0 + webhook)
- **Polar AccessLink** — training, HR, sleep
- **Garmin Health API** — HRV, VO2max, stress (OAuth 1.0a)
- **Withings** — weight, HR, ECG (OAuth 2.0)
- **Fitbit / Google Health API** — full migration by September 2026
- **Dexcom CGM** — real-time glucose, FDA-cleared

**Open-source aggregators:**

- **Open Wearables** — unified middleware for Apple/Garmin/Polar/Suunto/Whoop/Oura
- **Wearipedia** — Stanford research wrapper

**Interoperability standards:** HL7 FHIR R4/R5, SMART on FHIR, HAPI FHIR server.
