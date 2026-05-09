# Altri sistemi · Smart home, identity, computer vision, automazioni

Jarvis si integra con un ecosistema più ampio di software open source maturo. Questa pagina elenca le integrazioni "di sistema" non strettamente legate a un singolo device.

## Home Assistant

[Home Assistant](https://www.home-assistant.io/) è la piattaforma di riferimento per la **smart home**. Jarvis non rimpiazza HA: lo usa come **bridge** verso Matter/Thread/Zigbee/Wi-Fi e oltre 3.000 integrazioni.

### Capability che Jarvis sfrutta

- 🏠 controllo luci, termostati, prese, telecamere, allarmi
- 🚪 stato sensori (porte, finestre, presenza)
- ⚡ energy management (consumi solari, batterie)
- 🚨 automazioni complesse via YAML / NodeRED
- 📊 storia dati con Long-Term Statistics

### Integrazione

```env
HOME_ASSISTANT_URL=http://hassio.local:8123
HOME_ASSISTANT_TOKEN=eyJhbGciOi...
```

Jarvis legge lo stato HA via REST/WebSocket e invoca servizi:

```python
await ha.call_service("light", "turn_on",
                      entity_id="light.living_room",
                      brightness=128)
```

### Voice + HA

L'iniziativa **"Year of the Voice"** di HA ha portato a:

- pipeline STT/TTS/NLU completamente locale
- `microWakeWord` su ESP32-S3 per wake word on-device
- **Home Assistant Voice Preview Edition** (hardware ufficiale ESPHome-based)

Jarvis può funzionare come **conversation agent** di HA (compatibile API).

## ESPHome

[ESPHome](https://esphome.io/) è il framework YAML-driven per firmware ESP32/ESP8266.

- Aggiunge **OpenThread** dalla v2025.6
- Voice assistant nativo
- Deep integration con HA via API cifrata
- Abbatte la barriera per **device custom** (sensori, attuatori, gateway)

Use case Jarvis: pulsanti dedicati, sensori biometrici DIY, gateway BLE-to-Wi-Fi.

## Frigate

[Frigate](https://frigate.video/) è un NVR open source con **rilevamento oggetti locale** via OpenCV/TensorFlow/Coral TPU.

- ⚡ Latenza < 10ms con Coral
- 👤 Facial recognition + license plate recognition
- 🤖 Integrazione MQTT con HA per automazioni
- 📹 Gestione registrazioni 24/7

Jarvis può:

- ricevere eventi di detection in tempo reale
- contestualizzare ("c'è qualcuno sulla porta?")
- generare riassunti AI delle registrazioni

## Mosquitto / EMQX (MQTT broker)

- **Eclipse Mosquitto** — leggero, EPL/EDL, ideale per home lab
- **EMQX** — scalabile per produzione

Jarvis pubblica/sottoscrive eventi su MQTT come **event bus** per:

- detection di Frigate
- stato stampanti 3D Bambu (MQTT 8883)
- eventi Home Assistant

## Authentik

[Authentik](https://goauthentik.io/) è l'**Identity Provider** raccomandato per Jarvis. Versione 2025.12 aggiunge:

- 🔑 Device fleet management nativo per Win/Mac/Linux via Authentik Agent
- 🪪 WebAuthn Conditional UI (passkey)
- 👥 RBAC multi-parent
- 🌐 SSO, LDAP, OAuth 2.0/OIDC, SAML, SCIM

Jarvis usa Authentik per propagare un'**identity unica** a tutti gli agenti.

```env
OIDC_ISSUER=https://auth.tuodominio.com/application/o/jarvis/
OIDC_CLIENT_ID=jarvis
OIDC_CLIENT_SECRET=...
```

Alternative: **Keycloak** (più enterprise, passkey ufficiale in v26.4), **Authelia** (leggero), **Zitadel** (developer-first).

## n8n / Node-RED

Per **automazioni multi-step** complesse Jarvis può integrarsi con:

- [n8n](https://n8n.io/) — workflow orchestration moderna, fair-code
- [Node-RED](https://nodered.org/) — flow-based programming, classico per IoT

Use case: pipeline di ingestion personalizzate, multi-step decision chains, integrazione con SaaS senza scrivere codice.

## SearxNG

[SearxNG](https://github.com/searxng/searxng) è un **meta-search engine** privacy-first che aggrega risultati da Google, Bing, DuckDuckGo, ecc. **senza tracking**.

Jarvis lo usa come search provider quando l'utente vuole privacy massima (alternativa a Bing/Google API).

```env
SEARCH_PROVIDER=searxng
SEARXNG_URL=http://searxng:8080
```

## Vaultwarden

[Vaultwarden](https://github.com/dani-garcia/vaultwarden) — server Bitwarden compatibile, self-hosted.

Use case: Jarvis può **leggere credenziali con consenso esplicito** per riempire form, automatizzare login, gestire password senza copiarle in chat.

## HashiCorp Vault / SOPS / age

Per la gestione dei segreti operativi (token API, certificati):

- **HashiCorp Vault** — soluzione enterprise-grade
- **SOPS + age** — segreti cifrati committati nel repo (per home setup)
- **agenix** / **sops-nix** — integrazione con NixOS

## Stack di osservabilità

- **Prometheus** + **Grafana** — metriche e dashboard
- **Loki** — log aggregation
- **OpenTelemetry** — tracing distribuito
- **Sentry** — error tracking

Tutti i container Jarvis emettono metriche Prometheus su `/metrics`.

## Sistemi maker non-3D

- 🤖 **ROS 2** — robotica
- 🌱 **OpenSprinkler** — irrigazione
- 🐝 **Beekeeping monitors** — sensori arnie
- 🔬 **Octolapse** + **OctoEverywhere** — failure detection per stampe 3D

Tutti integrabili via Home Assistant o MQTT.

## Roadmap integrazioni

| Fase | Sistema |
|---|---|
| 5.1 | Home Assistant bridge bidirezionale |
| 5.2 | Frigate event ingestion |
| 5.3 | ESPHome custom devices |
| 5.4 | Authentik OIDC SSO |
| 5.5 | n8n trigger gateway |
| 5.6 | Vaultwarden credential filler |
| 5.7 | Prometheus + Grafana metrics dashboard |
