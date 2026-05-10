# Open-Jarvis · Desktop (Tauri 2)

Wrapper desktop nativo (macOS · Windows · Linux) attorno alla PWA
Angular di `frontend/web`. Pesa ~6 MB compresso (vs ~150 MB per Electron).

## Caratteristiche

- **System tray** con Mostra / Esci
- **Deep linking** per `jarvispair://v1?token=…&code=…` (apre l'app dal
  QR scannerizzato sul telefono)
- **Configurazione runtime** dell'API server URL via Login page
  (oppure compile-time via `OJ_API_BASE_URL`)
- **Single binary** firmabile e auto-aggiornabile (TODO: signing key)

## Prerequisiti

```bash
# Rust toolchain
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup default stable

# Linux deps (Debian/Ubuntu)
sudo apt install -y libwebkit2gtk-4.1-dev build-essential libssl-dev \
                    libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev

# macOS deps
xcode-select --install

# Windows deps: Microsoft Edge WebView2 (incluso in Windows 11)

# Node + pnpm
node --version    # v20+
pnpm --version    # v9+
```

## Sviluppo

Da repo root:

```bash
pnpm install                          # installa frontend + desktop
pnpm --filter @open-jarvis/desktop dev
```

Il primo run scarica Cargo crates (~5 min). I run successivi sono
incrementali. La finestra dev si aggiorna in tempo reale al modificare
i file Angular (HMR).

In alternativa dai due terminali:

```bash
# Terminale 1
pnpm --filter @open-jarvis/web start  # ng serve :4200

# Terminale 2
cd agents/desktop && pnpm tauri dev
```

## Build production

```bash
pnpm --filter @open-jarvis/desktop build
```

Output:

| Piattaforma | Path |
|-------------|------|
| Linux       | `src-tauri/target/release/bundle/{deb,appimage,rpm}/` |
| macOS       | `src-tauri/target/release/bundle/macos/`              |
| Windows     | `src-tauri/target/release/bundle/{msi,nsis}/`         |

## Compile-time API URL

Per distribuire bundle "puntati" a un server specifico:

```bash
OJ_API_BASE_URL=https://jarvis.example.com pnpm --filter @open-jarvis/desktop build
```

L'app emetterà come `window.__OJ_API_BASE_URL__` quel valore, e la
Login page nasconde il campo "Server URL".

## Comandi Tauri esposti al frontend

```ts
import { invoke } from '@tauri-apps/api/core';

await invoke('ping');                  // → "pong"
await invoke('default_api_base_url');  // → "" (o quello iniettato)
```

## Distribuzione

- **macOS**: `.dmg` o `.app.zip` (richiede Apple Developer ID per la
  notarizzazione, in roadmap M1.7)
- **Windows**: `.msi` con WiX Toolset
- **Linux**: `.AppImage` portable + `.deb`/`.rpm` per pacchettizzati

Roadmap firma + auto-update: vedi [Aggiornare Open-Jarvis](../../docs/it/user-manual/updates.md).
