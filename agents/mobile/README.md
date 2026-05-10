# Open-Jarvis · Mobile (Ionic 8 + Angular 18 + Capacitor 6)

Client mobile nativo per **iOS** e **Android**, con UI Ionic e core
Angular condiviso (servizi auth/chat/memory equivalenti al web).

> **Nota sulla scelta tecnologica.** Il branch si chiama storicamente
> `feat/agent-mobile-react-native`, ma il progetto si è standardizzato
> su Angular per il frontend; Ionic + Capacitor permette di riusare
> direttamente i servizi e i tipi del web. Una sostituzione del nome
> branch verrà fatta quando non ci saranno più branch aperti che vi
> dipendono.

## Pagine

| Tab | Descrizione |
|-----|-------------|
| 💬 Chat     | Conversazione con streaming SSE token-by-token |
| 📚 Memoria  | Aggiungi/elimina ricordi (swipe-to-delete) |
| ⚙️ Settings | Server URL, lista backend LLM, modelli Ollama, logout |

Login dedicato (`/login`) con segmenti *Accedi* / *Registrati* e campo
*Server URL* per puntare al PC host (`http://192.168.X.Y:8090`) o al
dominio della VPS (`https://jarvis.example.com`).

## Sviluppo (browser)

```bash
cd agents/mobile
pnpm install
pnpm start      # → http://localhost:4300
```

L'app gira nel browser come una PWA. Per autenticarti devi avere il
server Open-Jarvis raggiungibile (vedi
[Installazione locale](../../docs/it/user-manual/install/local-lan.md)).

## Build per iOS

```bash
pnpm sync                  # build Angular + cap sync
pnpm cap add ios           # solo la prima volta
pnpm ios                   # apre Xcode
```

Compila in Xcode (richiede Apple Developer ID per device fisico,
simulatore funziona gratis). Per submission App Store:

1. Configura signing in *Signing & Capabilities*
2. Product → Archive
3. Distribute → App Store Connect

## Build per Android

```bash
pnpm sync
pnpm cap add android       # solo la prima volta
pnpm android               # apre Android Studio
```

In Android Studio: *Run* (su emulatore o dispositivo). Per Play Store:
*Build → Generate Signed Bundle*.

## Architettura

```
agents/mobile/
├── src/
│   ├── app/
│   │   ├── app.component.ts     # IonApp + RouterOutlet
│   │   ├── app.routes.ts        # /login + tabs (chat/memory/settings)
│   │   ├── core/
│   │   │   ├── api.types.ts     # mirror dei DTO Pydantic
│   │   │   ├── auth.service.ts  # signals + Capacitor Preferences
│   │   │   ├── auth.interceptor.ts
│   │   │   ├── auth.guard.ts
│   │   │   ├── chat.service.ts  # fetch + ReadableStream SSE
│   │   │   ├── memory.service.ts
│   │   │   ├── llm.service.ts
│   │   │   ├── config.ts        # API URL persistente in Preferences
│   │   │   └── storage.ts       # Capacitor Preferences (fallback localStorage)
│   │   ├── layout/tabs.page.ts  # IonTabs (chat/memory/settings)
│   │   └── pages/               # login, chat, memory, settings
│   ├── theme/variables.css      # palette jarvis-*
│   ├── styles.css
│   ├── index.html
│   └── main.ts
├── capacitor.config.json        # appId dev.openjarvis.mobile + LAN allowNavigation
├── angular.json
├── package.json
└── README.md
```

## Capacitor plugins inclusi

| Plugin | Uso |
|--------|-----|
| `@capacitor/preferences` | persistenza secure-ish del JWT |
| `@capacitor/keyboard`    | resize body + status bar dark |
| `@capacitor/status-bar`  | tema coerente con `jarvis-*` |
| `@capacitor/haptics`     | feedback (in roadmap) |
| `@capacitor/app`         | deep-link `jarvispair://` (in roadmap) |

## Pairing del device

L'app supporta il pairing via QR generato dal client web/desktop:

1. Sul PC apri Open-Jarvis web → *Devices* → *Genera codice pairing*
2. Apri lo scanner QR sull'app mobile (in roadmap M1.6 mobile-side; per
   ora incolla manualmente l'URI `jarvispair://...`)
3. L'app POSTa `/api/v1/pairing/redeem` e riceve un JWT device-bound

## Limitazioni note

- **iOS Safari nativo** richiede HTTPS per WebAuthn/passkey: vedi
  [Installazione locale → mkcert](../../docs/it/user-manual/install/local-lan.md#opzione-b--mkcert-ca-locale-raccomandato)
- **Push notifications**: arriveranno nella M2 (richiede Firebase/APNs)
- **Wake-word "Hey Jarvis"**: M2 con Picovoice Porcupine
