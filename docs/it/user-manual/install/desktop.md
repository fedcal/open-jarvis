---
title: "Installazione desktop · macOS · Windows · Linux"
description: "Installa l'agente desktop Open-Jarvis su Mac, Windows (WSL2) e Linux."
---

# Installazione desktop

L'agente desktop Jarvis è un'app Tauri (~10 MB) che fornisce: integrazione system tray, hotkey globali, accesso filesystem locale, IDE integration, voice input.

## macOS

### Requisiti

- macOS 13 Ventura o superiore (ARM o Intel)
- 100 MB spazio disco

### Installazione

**Opzione A — Homebrew (raccomandato):**

```bash
brew tap fedcal/jarvis
brew install --cask jarvis-desktop
```

**Opzione B — DMG:**

1. Scarica `Jarvis-Desktop-macOS.dmg` da [Releases](https://github.com/fedcal/open-jarvis/releases)
2. Apri il DMG e trascina **Jarvis** in Applicazioni
3. Avvia da Launchpad. Al primo avvio macOS chiederà conferma per "app non identificata": vai in **Sistema → Privacy e sicurezza → Apri comunque**

### Permessi richiesti

Al primo avvio l'app richiede:

- 🎙️ **Microfono** (per wake-word "Hey Jarvis")
- 🔔 **Notifiche**
- 🩺 **HealthKit** (se vuoi sincronizzare dati salute Mac → Jarvis)
- 🏠 **HomeKit** (opzionale, controllo smart home)
- 📁 **Documenti** (per RAG sui tuoi file)

### Pairing al server

1. Apri Jarvis Desktop → **Preferenze → Connessione**
2. Inserisci URL server: `https://jarvis.tuodominio.com`
3. Accedi con email + password + 2FA (vedi [Web auth](../../security/web-auth.md))
4. Il device viene registrato automaticamente

### Hotkey globali (default)

- `⌥⌘ Space` — apri pannello chat
- `⌥⌘ J` — voice input on-demand
- `⌥⌘ B` — daily briefing

Personalizzabili da **Preferenze → Hotkey**.

## Windows

### Requisiti

- Windows 11 (10 21H2+ supportato ma sconsigliato)
- WSL2 disponibile (per agente locale e voice pipeline)
- 200 MB spazio disco

### Installazione

**Opzione A — Winget (raccomandato):**

```powershell
winget install fedcal.jarvis-desktop
```

**Opzione B — Installer MSI:**

1. Scarica `Jarvis-Desktop-Setup-x64.msi` da [Releases](https://github.com/fedcal/open-jarvis/releases)
2. Esegui come amministratore
3. L'installer richiederà di abilitare WSL2 se non presente

### Permessi

Windows Security mostrerà un avviso "App non riconosciuta": clicca **Ulteriori info → Esegui comunque** (l'app è firmata MS Store dalla v1.0).

### Pairing al server

Identico a macOS ma da **Impostazioni → Connessione**.

### Voice input

Il voice agent gira in WSL2 per latenza ottimale. La prima volta:

```powershell
wsl --install -d Ubuntu-22.04
# Una volta in Ubuntu:
sudo apt install python3.12 python3.12-venv portaudio19-dev
```

Successivamente Jarvis Desktop gestirà tutto automaticamente.

## Linux

### Requisiti

- Distribuzione recente (Ubuntu 22.04+, Fedora 40+, Arch, Debian 12+)
- `glibc >= 2.35`
- PulseAudio o PipeWire
- 100 MB spazio disco

### Installazione

**Ubuntu/Debian (deb):**

```bash
curl -fsSL https://github.com/fedcal/open-jarvis/releases/latest/download/jarvis-desktop.deb -o jarvis.deb
sudo apt install ./jarvis.deb
```

**Fedora/RHEL (rpm):**

```bash
sudo dnf install https://github.com/fedcal/open-jarvis/releases/latest/download/jarvis-desktop.rpm
```

**Arch (AUR):**

```bash
yay -S jarvis-desktop
```

**AppImage (universale):**

```bash
wget https://github.com/fedcal/open-jarvis/releases/latest/download/Jarvis-Desktop.AppImage
chmod +x Jarvis-Desktop.AppImage
./Jarvis-Desktop.AppImage
```

**Flatpak:**

```bash
flatpak install flathub dev.federicocalo.Jarvis
```

### Pairing

Lancia Jarvis dal menu app o:

```bash
jarvis-desktop
```

Procedura di pairing identica alle altre piattaforme.

### KDE Connect bridge (opzionale)

Se hai KDE Connect installato, Jarvis lo rileva e lo usa per:

- 🔔 Notifiche bidirezionali con il telefono
- 📋 Clipboard sync
- 📁 Trasferimento file rapido

```bash
sudo apt install kdeconnect  # Ubuntu/Debian
# Abilita in Preferenze Jarvis → Integrazioni → KDE Connect
```

## Aggiornamenti

L'app si aggiorna automaticamente. Per verificare manualmente:

- macOS/Windows: **Aiuto → Cerca aggiornamenti**
- Linux: dipende dal package manager (`apt upgrade`, `dnf upgrade`, `flatpak update`)

## Disinstallazione

| Piattaforma | Comando |
|---|---|
| macOS | `brew uninstall --cask jarvis-desktop` o trascina in Cestino |
| Windows | `winget uninstall fedcal.jarvis-desktop` o Pannello di controllo |
| Linux deb | `sudo apt remove jarvis-desktop` |
| Linux rpm | `sudo dnf remove jarvis-desktop` |
| AppImage | Elimina il file |
| Flatpak | `flatpak uninstall dev.federicocalo.Jarvis` |
