# Other systems · Smart home, identity, computer vision, automation

Jarvis integrates with a broader ecosystem of mature open-source software. This page lists "system-level" integrations not tied to a single device.

## Home Assistant

[Home Assistant](https://www.home-assistant.io/) is the reference **smart-home** platform. Jarvis does not replace HA: it uses it as a **bridge** to Matter/Thread/Zigbee/Wi-Fi and 3,000+ integrations.

### Capabilities Jarvis uses

- 🏠 Lights, thermostats, plugs, cameras, alarms control
- 🚪 Sensor states (doors, windows, presence)
- ⚡ Energy management (solar, batteries)
- 🚨 Complex automations via YAML / NodeRED
- 📊 Long-Term Statistics history

### Integration

```env
HOME_ASSISTANT_URL=http://hassio.local:8123
HOME_ASSISTANT_TOKEN=eyJhbGciOi...
```

Jarvis reads HA state via REST/WebSocket and invokes services:

```python
await ha.call_service("light", "turn_on",
                      entity_id="light.living_room",
                      brightness=128)
```

### Voice + HA

HA's **"Year of the Voice"** initiative delivered:

- Fully local STT/TTS/NLU pipeline
- `microWakeWord` on ESP32-S3 for on-device wake word
- **Home Assistant Voice Preview Edition** (official ESPHome-based hardware)

Jarvis can act as HA **conversation agent** (API-compatible).

## ESPHome

[ESPHome](https://esphome.io/) is the YAML-driven firmware framework for ESP32/ESP8266.

- Adds **OpenThread** since v2025.6
- Native voice assistant
- Deep HA integration via encrypted API
- Lowers the barrier for **custom devices** (sensors, actuators, gateways)

Jarvis use case: dedicated buttons, DIY biometric sensors, BLE-to-Wi-Fi gateways.

## Frigate

[Frigate](https://frigate.video/) is an open-source NVR with **local object detection** via OpenCV/TensorFlow/Coral TPU.

- ⚡ < 10ms latency with Coral
- 👤 Facial recognition + license plate recognition
- 🤖 MQTT integration with HA for automations
- 📹 24/7 recording management

Jarvis can:

- receive detection events in real time
- contextualise ("is anyone at the door?")
- generate AI summaries of recordings

## Mosquitto / EMQX (MQTT brokers)

- **Eclipse Mosquitto** — lightweight, EPL/EDL, ideal for home labs
- **EMQX** — scalable for production

Jarvis publishes/subscribes events on MQTT as **event bus** for:

- Frigate detection events
- Bambu 3D printer state (MQTT 8883)
- Home Assistant events

## Authentik

[Authentik](https://goauthentik.io/) is the recommended **Identity Provider** for Jarvis. Version 2025.12 adds:

- 🔑 Native device fleet management for Win/Mac/Linux via Authentik Agent
- 🪪 WebAuthn Conditional UI (passkeys)
- 👥 Multi-parent RBAC
- 🌐 SSO, LDAP, OAuth 2.0/OIDC, SAML, SCIM

Jarvis uses Authentik to propagate a **single identity** to all agents.

```env
OIDC_ISSUER=https://auth.yourdomain.com/application/o/jarvis/
OIDC_CLIENT_ID=jarvis
OIDC_CLIENT_SECRET=...
```

Alternatives: **Keycloak** (more enterprise, official passkey in v26.4), **Authelia** (lightweight), **Zitadel** (developer-first).

## n8n / Node-RED

For complex **multi-step automations** Jarvis can integrate with:

- [n8n](https://n8n.io/) — modern workflow orchestration, fair-code
- [Node-RED](https://nodered.org/) — flow-based programming, classic for IoT

Use case: custom ingestion pipelines, multi-step decision chains, SaaS integration without code.

## SearxNG

[SearxNG](https://github.com/searxng/searxng) is a privacy-first **meta-search engine** that aggregates results from Google, Bing, DuckDuckGo, etc. **without tracking**.

Jarvis uses it as the search provider when the user wants maximum privacy (alternative to Bing/Google APIs).

```env
SEARCH_PROVIDER=searxng
SEARXNG_URL=http://searxng:8080
```

## Vaultwarden

[Vaultwarden](https://github.com/dani-garcia/vaultwarden) — Bitwarden-compatible, self-hosted server.

Use case: Jarvis can **read credentials with explicit consent** to fill forms, automate logins, manage passwords without copying them into chat.

## HashiCorp Vault / SOPS / age

For operational secrets management (API tokens, certificates):

- **HashiCorp Vault** — enterprise-grade solution
- **SOPS + age** — secrets encrypted in the repo (home setup)
- **agenix** / **sops-nix** — NixOS integration

## Observability stack

- **Prometheus** + **Grafana** — metrics and dashboards
- **Loki** — log aggregation
- **OpenTelemetry** — distributed tracing
- **Sentry** — error tracking

All Jarvis containers expose Prometheus metrics on `/metrics`.

## Non-3D maker systems

- 🤖 **ROS 2** — robotics
- 🌱 **OpenSprinkler** — irrigation
- 🐝 **Beekeeping monitors** — hive sensors
- 🔬 **Octolapse** + **OctoEverywhere** — 3D print failure detection

All integrable via Home Assistant or MQTT.

## Integration roadmap

| Phase | System |
|---|---|
| 5.1 | Bidirectional Home Assistant bridge |
| 5.2 | Frigate event ingestion |
| 5.3 | ESPHome custom devices |
| 5.4 | Authentik OIDC SSO |
| 5.5 | n8n trigger gateway |
| 5.6 | Vaultwarden credential filler |
| 5.7 | Prometheus + Grafana metrics dashboard |
