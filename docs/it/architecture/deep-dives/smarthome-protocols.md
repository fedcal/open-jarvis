---
title: "Deep-dive · Smart home + Communication protocols"
description: "Home Assistant bridge, Matter 1.5, Thread/OpenThread, MQTT, MCP/A2A/AG-UI, KDE Connect, Authentik OIDC."
keywords: "Home Assistant, Matter 1.5, Thread, MQTT, MCP, A2A, AG-UI, Authentik OIDC, KDE Connect"
---

# Deep-dive · Smart Home + Agent Protocols

**Phase:** 5 (smart home) e cross-phase per i protocolli
**Versione:** maggio 2026

## 1. Home Assistant bridge

### Setup Docker

```yaml
services:
  homeassistant:
    image: ghcr.io/home-assistant/home-assistant:stable
    network_mode: host
    volumes:
      - /opt/jarvis/ha-config:/config
      - /etc/localtime:/etc/localtime:ro
    restart: unless-stopped
    privileged: true
```

HA ascolta su `:8123`. Per Zigbee/Thread dongle USB: `devices: ["/dev/ttyUSB0:/dev/ttyUSB0"]`.

### REST + WebSocket client

```python
import json
import aiohttp

HA_URL = "http://homeassistant.local:8123"
HA_TOKEN = "YOUR_LONG_LIVED_TOKEN"
HEADERS = {"Authorization": f"Bearer {HA_TOKEN}", "Content-Type": "application/json"}


async def turn_on_light(entity_id: str, brightness: int = 255) -> dict:
    async with aiohttp.ClientSession() as s:
        async with s.post(
            f"{HA_URL}/api/services/light/turn_on",
            headers=HEADERS,
            json={"entity_id": entity_id, "brightness": brightness},
        ) as r:
            return await r.json()


async def stream_states():
    """WebSocket subscribe state_changed."""
    async with aiohttp.ClientSession() as s:
        async with s.ws_connect(f"ws://homeassistant.local:8123/api/websocket") as ws:
            assert (await ws.receive_json())["type"] == "auth_required"
            await ws.send_json({"type": "auth", "access_token": HA_TOKEN})
            assert (await ws.receive_json())["type"] == "auth_ok"
            await ws.send_json({
                "id": 1, "type": "subscribe_events", "event_type": "state_changed"
            })
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    if data.get("type") == "event":
                        evt = data["event"]["data"]
                        print(f"[HA] {evt.get('entity_id')} → {evt.get('new_state', {}).get('state')}")
```

### Conversation Agent

Espone Jarvis come backend voce HA tramite custom HACS component:

```text
POST /api/conversation/process
{
  "text": "Accendi la luce del soggiorno",
  "conversation_id": "jarvis-abc",
  "language": "it"
}
```

### HACS + Frigate NVR

**Frigate** publishes detection events su `frigate/<camera>/events` con `label`, `score`, snapshot URL. Jarvis sottoscrive per automazioni context-aware.

## 2. Matter 1.5 (novembre 2025)

Standard CSA, supportato da Apple/Google/Amazon/Samsung. v1.5 introduce:

- **Cameras** WebRTC + audio bidirezionale + zone privacy
- **Enhanced Closures** (tende, cancelli, garage)
- **Energy Management** esteso (EV charger, battery storage, solar)

### Cluster model

| Cluster | ID | Funzione |
|---|---|---|
| OnOff | 0x0006 | On/off |
| LevelControl | 0x0008 | Dimmer |
| ColorControl | 0x0300 | Hue/saturation/temp |
| Thermostat | 0x0201 | Setpoint |
| DoorLock | 0x0101 | Serratura |
| EnergyEvse | 0x0099 | EV charger |

### Commissioning flow

1. Accessory non-commissioned in BLE advertising
2. Controller legge QR Matter (o NFC)
3. PASE via BLE
4. Trasferimento credenziali Wi-Fi/Thread dataset
5. CASE completion

### python-matter-server

```python
import aiohttp


async def commission_device(code: str) -> dict:
    async with aiohttp.ClientSession() as s:
        async with s.ws_connect("ws://localhost:5580/ws") as ws:
            await ws.send_json({
                "message_id": "1",
                "command": "commission_with_code",
                "args": {"code": code, "network_only": False},
            })
            return await ws.receive_json()


async def discover_nodes() -> list:
    async with aiohttp.ClientSession() as s:
        async with s.ws_connect("ws://localhost:5580/ws") as ws:
            await ws.send_json({"message_id": "2", "command": "get_nodes", "args": {}})
            return (await ws.receive_json()).get("result", [])
```

### Thread Border Router 2026

- **Apple HomePod mini / HomePod 2**: Thread 1.4, credential sharing
- **Google Nest Hub 2nd gen**: Thread 1.3 (upgrade in arrivo)
- **HA Yellow / SkyConnect**: BR open source via OTBR

Da maggio 2026 Thread 1.4 obbligatorio per nuove certificazioni: BR 1.4 condividono automaticamente le credenziali.

## 3. Thread + OpenThread

ESPHome ≥ 2025.6.0 con ESP32-C6/H2:

```yaml
# esphome-thread-sensor.yml
esp32:
  board: esp32-c6-devkitc-1
  framework:
    type: esp-idf

openthread:
  network_name: "JarvisHome"
  channel: 15
  output_power: 10  # dBm

sensor:
  - platform: bme280
    temperature:
      name: "Temperatura Soggiorno"
```

OTBR Docker:

```bash
docker run --detach --name otbr \
  --sysctl "net.ipv6.conf.all.disable_ipv6=0 net.ipv4.conf.all.forwarding=1 net.ipv6.conf.all.forwarding=1" \
  --privileged \
  -p 8080:80 -p 8081:8081 \
  --device /dev/ttyUSB0:/dev/ttyACM0 \
  nrfconnect/otbr:latest \
  --radio-url spinel+hdlc+uart:///dev/ttyACM0?uart-baudrate=460800
```

## 4. Zigbee 3.0

Ampia copertura legacy (3.000+ device su zigbee2mqtt).

| Tool | Ruolo |
|---|---|
| zigpy | Stack Zigbee Python low-level |
| Zigbee2MQTT | Bridge Zigbee → MQTT |
| ZHA | Integrazione nativa HA |

| Coordinator | Chip | Note |
|---|---|---|
| Sonoff ZBDongle-P | CC2652P | Standard de facto |
| Sonoff ZBDongle-MG24 | MGM240P | Zigbee + Thread |
| HA Connect ZBT-2 | EFR32MG24 | Ufficiale HA (nov 2025) |

## 5. MQTT come event bus

**Mosquitto 2.x** raccomandato per home (footprint 5MB RAM). EMQX per multi-node.

Topic structure Jarvis:

```text
jarvis/{device_id}/{capability}/{action}

# Esempi
jarvis/lamp-living/light/turn_on
jarvis/thermostat-main/temperature/current
jarvis/camera-entrance/motion/detected
jarvis/frigate/camera-front/person/detected
```

QoS levels: 0 telemetria alta freq · 1 comandi standard · 2 transazioni critiche (lock).

mTLS auth:

```ini
listener 8883
cafile /etc/mosquitto/certs/ca.crt
certfile /etc/mosquitto/certs/server.crt
keyfile /etc/mosquitto/certs/server.key
require_certificate true
use_identity_as_username true
```

```python
import json
import aiomqtt


async def publish_command(device_id: str, capability: str, payload: dict):
    async with aiomqtt.Client(
        hostname="mosquitto", port=8883,
        tls_params=aiomqtt.TLSParameters(
            ca_certs="/certs/ca.crt",
            certfile="/certs/jarvis-agent.crt",
            keyfile="/certs/jarvis-agent.key",
        ),
    ) as c:
        await c.publish(f"jarvis/{device_id}/{capability}/set",
                        payload=json.dumps(payload), qos=1)
```

## 6. Model Context Protocol (MCP)

Anthropic, dic 2024. Spec attuale `2025-11-25`. JSON-RPC 2.0 su stdio o HTTP/SSE.

3 primitive:

1. **Tools**: funzioni con schema JSON
2. **Resources**: dati con URI template
3. **Prompts**: template tipizzati

Apple iOS 26.1 (autunno 2026): Siri usa MCP via App Intents.

```python
"""
MCP server per Jarvis home control.
"""
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, Resource, CallToolResult
import aiohttp

app = Server("jarvis-home-mcp")
HA_URL = "http://homeassistant.local:8123"
HA_HEADERS = {"Authorization": f"Bearer YOUR_TOKEN"}


@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="home_turn_on_light",
            description="Accende una luce o gruppo di luci",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string"},
                    "brightness_pct": {"type": "integer", "minimum": 1, "maximum": 100},
                },
                "required": ["entity_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    async with aiohttp.ClientSession(headers=HA_HEADERS) as s:
        if name == "home_turn_on_light":
            payload = {"entity_id": arguments["entity_id"]}
            if "brightness_pct" in arguments:
                payload["brightness_pct"] = arguments["brightness_pct"]
            async with s.post(f"{HA_URL}/api/services/light/turn_on", json=payload) as r:
                result = await r.json()
                return CallToolResult(content=[TextContent(type="text", text=str(result))])
```

## 7. Agent2Agent (A2A)

Google, apr 2025 → Linux Foundation jun 2025. Risolve agent-to-agent.

- Agent Card JSON (capacità, endpoint, auth)
- Task lifecycle (submitted, working, completed, failed)
- LangGraph v1.0 supporto nativo

```python
import httpx
from a2a.client import A2AClient
from a2a.types import SendMessageRequest, MessageSendParams

HOME_AGENT_URL = "http://jarvis-home-agent:8001"


async def delegate_to_home_agent(task: str) -> str:
    async with httpx.AsyncClient() as http:
        client = A2AClient(http_client=http, url=HOME_AGENT_URL)
        request = SendMessageRequest(
            params=MessageSendParams(
                message={
                    "role": "user",
                    "parts": [{"kind": "text", "text": task}],
                    "messageId": "msg-001",
                }
            )
        )
        response = await client.send_message(request)
        return response.result.parts[0].text if response.result else ""
```

### MCP vs A2A (complementari)

| Dimensione | MCP | A2A |
|---|---|---|
| Relazione | Agent → Tool/Resource | Agent → Agent |
| Paradigma | Client-server sync | Task delegation async |
| Stato | Stateless | Lifecycle tracking |
| Uso Jarvis | Esporre tool HA, file, API | Delegare a sotto-agenti |

## 8. AG-UI Protocol

CopilotKit. Bidirezionale frontend ↔ backend agentico, complementa MCP+A2A su layer rendering UI. Adottato da Google ADK, LangChain, AWS, Microsoft, Mastra, PydanticAI.

```tsx
// React + AG-UI
import { useCoAgent, useCoAgentStateRender } from "@copilotkit/react-core";
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";

function SmartHomeDashboard() {
  const { state } = useCoAgent<HomeState>({ name: "jarvis_home_agent" });

  useCoAgentStateRender<HomeState>({
    name: "jarvis_home_agent",
    render: ({ state }) => (
      <div className="grid grid-cols-3 gap-4">
        {state.rooms.map(r => <RoomCard key={r.id} room={r} />)}
      </div>
    ),
  });

  return (
    <div className="flex">
      <CopilotChat instructions="Sei Jarvis..." />
    </div>
  );
}

export default function App() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit">
      <SmartHomeDashboard />
    </CopilotKit>
  );
}
```

## 9. KDE Connect (cross-device sync)

Open source dal 2013, TCP/UDP discovery + TLS data. Plugin sfruttabili da Jarvis:

| Plugin | Uso Jarvis |
|---|---|
| Notification Sync | Alert smart home → smartphone |
| Remote Input | Debug remoto da mobile |
| Clipboard Sync | Entity ID condivisi |
| Media Control | Player Jarvis remote |
| File Transfer | Log, snapshot Frigate |
| Run Command | Trigger automazioni |

```python
# Notifiche via DBus
import dbus


def send_notification(device_id: str, title: str, body: str):
    bus = dbus.SessionBus()
    device = bus.get_object(
        "org.kde.kdeconnect.daemon",
        f"/modules/kdeconnect/devices/{device_id}/notifications"
    )
    iface = dbus.Interface(device, "org.kde.kdeconnect.device.notifications")
    iface.sendNotification(title, body, "jarvis", 0)
```

## 10. Authentik OIDC + WebAuthn

**Authentik 2025.12** (gen 2026): Endpoint Devices fleet, Fleet Connector, WebAuthn Conditional UI, Local Device Login Linux con FIDO2.

```yaml
services:
  authentik-server:
    image: ghcr.io/goauthentik/server:2025.12
    command: server
    environment:
      AUTHENTIK_REDIS__HOST: redis
      AUTHENTIK_POSTGRESQL__HOST: postgresql
      AUTHENTIK_POSTGRESQL__USER: authentik
      AUTHENTIK_POSTGRESQL__PASSWORD: ${PG_PASS}
      AUTHENTIK_SECRET_KEY: ${AUTHENTIK_SECRET_KEY}
    ports:
      - "9000:9000"
      - "9443:9443"
```

Verifica JWT su ogni device-agent:

```python
import jwt as pyjwt
from functools import lru_cache

AUTHENTIK_URL = "https://auth.jarvis.local"
JWKS_URL = f"{AUTHENTIK_URL}/application/o/jarvis/.well-known/jwks.json"


@lru_cache(maxsize=1)
def jwks_client() -> pyjwt.PyJWKClient:
    return pyjwt.PyJWKClient(JWKS_URL)


def verify_jwt(token: str) -> dict:
    signing_key = jwks_client().get_signing_key_from_jwt(token)
    return pyjwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256", "ES256"],
        audience="jarvis-agent",
        issuer=f"{AUTHENTIK_URL}/application/o/jarvis/",
        options={"require": ["exp", "iat", "sub", "aud"]},
    )
```

## Mappa dipendenze

```text
open-jarvis
├── MQTT Bus (Mosquitto)
│   ├── Frigate events → jarvis/camera/+/detected
│   ├── Zigbee2MQTT → jarvis/zigbee/+/+
│   └── ESPHome sensors → jarvis/thread/+/+
├── Home Assistant (REST + WebSocket :8123)
│   ├── Matter (python-matter-server)
│   ├── ZHA / Zigbee
│   └── Conversation Agent ← Jarvis LLM core
├── MCP Server (stdio / SSE)
│   ├── Tool: home.turn_on_light
│   └── Resource: home://states
├── A2A Network
│   ├── JarvisHomeAgent
│   ├── JarvisSecurityAgent
│   └── JarvisEnergyAgent
├── AG-UI (React dashboard)
└── Authentik OIDC + WebAuthn
```

## Versioni (mag 2026)

| Componente | Versione |
|---|---|
| Home Assistant | 2025.12+ |
| Matter SDK | 1.4.2 (python-matter-server) |
| Matter Spec | 1.5 (nov 2025) |
| Thread Spec | 1.4 |
| ESPHome | 2025.6.0+ |
| MCP Spec | 2025-11-25 |
| A2A Protocol | 1.0 (Linux Foundation) |
| Authentik | 2025.12 |

## Riferimenti

- [Home Assistant WebSocket API](https://developers.home-assistant.io/docs/api/websocket/)
- [Matter Integration HA](https://www.home-assistant.io/integrations/matter/)
- [python-matter-server](https://github.com/matter-js/python-matter-server)
- [ESPHome 2025.6.0](https://esphome.io/changelog/2025.6.0/)
- [MCP Specification](https://modelcontextprotocol.io/specification/2025-11-25)
- [A2A Protocol](https://a2a-protocol.org/latest/)
- [AG-UI Docs](https://docs.ag-ui.com/introduction)
- [Authentik 2025.12](https://docs.goauthentik.io/releases/2025.12/)
