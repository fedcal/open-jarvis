---
title: "Deep-dive · Maker (Blender + 3D printing)"
description: "Pipeline tecnica end-to-end: AI 3D generation (TRELLIS-2, SPAR3D, TripoSR), Blender bpy automation, Klipper/Moonraker/OctoPrint/Bambu, slicer CLI."
keywords: "TRELLIS-2, SPAR3D, Blender bpy, Moonraker, OctoPrint, Bambu Lab MQTT, PrusaSlicer, mcp-3D-printer-server"
---

# Deep-dive · Maker stack (Blender + 3D printing)

**Phase:** 8 ([tracker](https://github.com/fedcal/open-jarvis/issues/17))
**Versione:** maggio 2026

## 1. AI 3D generation 2026

### TRELLIS-2 (Microsoft, MIT) — self-hosted

CVPR 2025 Spotlight, 4B params, struttura sparsa voxel "O-Voxel" field-free.

| GPU | VRAM | Risoluzione max | Tempo |
|---|---|---|---|
| RTX 3090/4080 | 16 GB | 512³ | ~6 s |
| RTX 4090/A6000 | 24 GB | 1024³ | ~17 s |
| A100/H100 | 40-80 GB | 1536³ | ~60 s |

```bash
git clone https://github.com/microsoft/TRELLIS.2.git
cd TRELLIS.2
bash setup.sh --new-env
conda activate trellis2
# GPU senza flash-attn (es. V100):
pip install xformers
export ATTN_BACKEND=xformers
```

Output: GLB (default OPAQUE), OBJ, PLY, Radiance Fields, 3D Gaussians. Pesi: `microsoft/TRELLIS.2-4B` su HuggingFace.

### SPAR3D (Stability AI) — self-hosted

Two-stage: point cloud diffusion + mesh generation conditioned. **0.7s** per oggetto, edit point cloud in **0.3s**. Licenza Stability AI Community.

### TripoSR (VAST AI / Stability) — self-hosted

Singola immagine → mesh in **<10 s** GPU consumer. Approccio feed-forward senza diffusion. Adatto a batch dove velocità > qualità assoluta.

### Meshy / CSM — cloud commerciale

| Tool | Latenza | Costo | Output |
|---|---|---|---|
| Meshy | ~60s text-to-3D | ~0.10 USD/gen | GLB, OBJ, FBX, STL, USDZ |
| CSM | 30-120s | Su richiesta | GLB, OBJ |

```python
import asyncio
import httpx


async def meshy_text_to_3d(prompt: str, api_key: str) -> str:
    headers = {"Authorization": f"Bearer {api_key}"}
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://api.meshy.ai/openapi/v2/text-to-3d",
            json={"mode": "preview", "prompt": prompt, "art_style": "realistic"},
            headers=headers,
        )
        r.raise_for_status()
        task_id = r.json()["result"]
        for _ in range(120):
            await asyncio.sleep(5)
            status = await client.get(
                f"https://api.meshy.ai/openapi/v2/text-to-3d/{task_id}", headers=headers
            )
            data = status.json()
            if data["status"] == "SUCCEEDED":
                return data["model_urls"]["glb"]
            if data["status"] == "FAILED":
                raise RuntimeError(f"Meshy failed: {data.get('task_error')}")
    raise TimeoutError("Meshy task timeout")
```

### GLB → STL conversion

```python
import trimesh


def glb_to_stl(glb_path: str, stl_path: str) -> None:
    scene = trimesh.load(glb_path)
    if isinstance(scene, trimesh.Scene):
        mesh = trimesh.util.concatenate(
            [g for g in scene.geometry.values() if isinstance(g, trimesh.Trimesh)]
        )
    else:
        mesh = scene
    mesh.export(stl_path)
```

## 2. Blender bpy automation

### Installazione headless

```bash
pip install bpy==4.3.0          # richiede Python 3.11
pip install fake-bpy-module-4.3  # type stubs IDE
```

!!! warning "Limite architetturale"
    `bpy` può essere importato **una sola volta per processo**. In server long-running, esegui ogni operazione mesh in subprocess dedicato.

### Pipeline GLB → repair → STL

```python
"""
agents/maker-agent/blender_pipeline.py
Eseguire come subprocess isolato.
"""
import logging
import math
from pathlib import Path

log = logging.getLogger(__name__)


def process_glb_to_stl(
    glb_path: str,
    stl_path: str,
    scale: float = 1.0,
    rotation_z_deg: float = 0.0,
) -> None:
    import bpy

    log.info("Pipeline: %s → %s", glb_path, stl_path)

    # 1. Pulizia scena
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # 2. Import GLB
    bpy.ops.import_scene.gltf(filepath=glb_path)

    # 3. Seleziona mesh + join
    mesh_objects = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not mesh_objects:
        raise ValueError(f"Nessuna mesh in {glb_path}")
    bpy.ops.object.select_all(action="DESELECT")
    for obj in mesh_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = mesh_objects[0]
    bpy.ops.object.join()
    merged = bpy.context.active_object

    # 4. Scale + rotate + apply
    merged.scale = (scale, scale, scale)
    merged.rotation_euler[2] = math.radians(rotation_z_deg)
    bpy.ops.object.transform_apply(scale=True, rotation=True, location=False)

    # 5. Repair: dedup vertices, normali coerenti, fill holes
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=0.0001)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.mesh.fill_holes(sides=4)
    bpy.ops.object.mode_set(mode="OBJECT")

    # 6. Export STL
    Path(stl_path).parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.stl_export(filepath=stl_path, export_selected_objects=True, ascii_format=False)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--glb", required=True)
    p.add_argument("--stl", required=True)
    p.add_argument("--scale", type=float, default=1.0)
    p.add_argument("--rotation-z", type=float, default=0.0)
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO)
    process_glb_to_stl(args.glb, args.stl, args.scale, args.rotation_z)
```

```python
# Invocazione safe da Jarvis
import subprocess, sys


def run_blender_pipeline(glb_path: str, stl_path: str, scale: float = 1.0) -> None:
    result = subprocess.run(
        [sys.executable, "/opt/jarvis/maker/blender_pipeline.py",
         "--glb", glb_path, "--stl", stl_path, "--scale", str(scale)],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Blender error:\n{result.stderr}")
```

### Blender 4.2+ extension system

```toml
# blender_manifest.toml
schema_version = "1.0.0"
id = "jarvis_maker"
version = "0.1.0"
name = "Jarvis Maker Integration"
maintainer = "open-jarvis"
type = "add-on"
blender_version_min = "4.2.0"
license = ["SPDX:Apache-2.0"]
```

## 3. 3D printer control

### Klipper + Moonraker (stack primario)

Moonraker porta default 7125. REST + WebSocket JSON-RPC 2.0.

| Endpoint | Funzione |
|---|---|
| `GET /printer/info` | Info firmware Klipper |
| `GET /printer/objects/query` | Stato (temp, posizione) |
| `POST /printer/objects/subscribe` | Subscribe real-time |
| `POST /printer/print/start` | Avvia stampa |
| `POST /printer/print/pause` | Pausa |
| `POST /printer/print/resume` | Resume |
| `POST /printer/print/cancel` | Cancella |
| `POST /server/files/upload` | Upload G-code |
| `POST /printer/gcode/script` | G-code raw |

```python
"""
agents/maker-agent/moonraker_client.py
Async REST + WebSocket client.
"""
import asyncio
import json
import httpx
import websockets


class MoonrakerClient:
    def __init__(self, host: str = "localhost", port: int = 7125):
        self._base = f"http://{host}:{port}"
        self._ws_url = f"ws://{host}:{port}/websocket"
        self._http = httpx.AsyncClient(timeout=30.0)
        self._rpc_id = 0

    async def get(self, path: str, **params):
        r = await self._http.get(f"{self._base}{path}", params=params)
        r.raise_for_status()
        return r.json()["result"]

    async def post(self, path: str, body: dict | None = None):
        r = await self._http.post(f"{self._base}{path}", json=body or {})
        r.raise_for_status()
        return r.json().get("result", {})

    async def start_print(self, filename: str):
        await self.post("/printer/print/start", {"filename": filename})

    async def cancel_print(self):
        await self.post("/printer/print/cancel")

    async def get_printer_status(self) -> dict:
        result = await self.get(
            "/printer/objects/query",
            objects="print_stats,extruder,heater_bed,toolhead,virtual_sdcard",
        )
        return result["status"]

    async def upload_file(self, local_path: str, remote_name: str) -> str:
        with open(local_path, "rb") as f:
            r = await self._http.post(
                f"{self._base}/server/files/upload",
                files={"file": (remote_name, f, "application/octet-stream")},
            )
        r.raise_for_status()
        return r.json()["result"]["item"]["path"]

    async def subscribe_and_watch(self, objects: dict, on_update):
        async with websockets.connect(self._ws_url) as ws:
            self._rpc_id += 1
            await ws.send(json.dumps({
                "jsonrpc": "2.0",
                "method": "printer.objects.subscribe",
                "params": {"objects": objects},
                "id": self._rpc_id,
            }))
            async for raw in ws:
                msg = json.loads(raw)
                if msg.get("id") == self._rpc_id and "result" in msg:
                    for obj_name, data in msg["result"].get("status", {}).items():
                        await on_update(obj_name, data)
                elif msg.get("method") == "notify_status_update":
                    for obj_name, data in msg["params"][0].items():
                        await on_update(obj_name, data)

    async def close(self):
        await self._http.aclose()
```

### OctoPrint + OctoEverywhere

OctoPrint REST porta 5000. Auth via `X-Api-Key`. **OctoEverywhere Gadget** AI failure detection (>320K maker), include MCP server [github.com/OctoEverywhere/mcp](https://github.com/OctoEverywhere/mcp).

### Bambu Lab MQTT (porta 8883 TLS)

```python
"""
agents/maker-agent/bambu_client.py
MQTT TLS Bambu Lab LAN mode.
"""
import json
import ssl
from dataclasses import dataclass, field
import paho.mqtt.client as mqtt


@dataclass
class BambuClient:
    serial: str
    ip: str
    access_code: str
    _state: dict = field(default_factory=dict)
    _client: mqtt.Client | None = None

    def connect(self):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE  # Bambu self-signed cert

        self._client = mqtt.Client(client_id="jarvis", protocol=mqtt.MQTTv311)
        self._client.username_pw_set("bblp", self.access_code)
        self._client.tls_set_context(ctx)
        self._client.on_message = self._on_message
        self._client.connect(self.ip, 8883, keepalive=60)
        self._client.subscribe(f"device/{self.serial}/report")
        self._client.loop_start()

    def _on_message(self, _c, _u, msg):
        payload = json.loads(msg.payload)
        if "print" in payload:
            self._state.update(payload["print"])

    def stop_print(self):
        cmd = {"print": {"command": "stop", "sequence_id": "1"}}
        self._client.publish(f"device/{self.serial}/request", json.dumps(cmd))

    def get_state(self) -> dict:
        return dict(self._state)
```

**bambu-moonraker-shim**: bridge che emula Moonraker API verso Bambu (P1P, P1S, X1C, A1) per uniformità client.

### PrusaLink / Prusa Connect

OpenAPI spec: [prusa3d/Prusa-Link-Web/spec/openapi.yaml](https://github.com/prusa3d/Prusa-Link-Web/blob/master/spec/openapi.yaml).

```python
class PrusaLinkClient:
    def __init__(self, host: str, api_key: str, port: int = 80):
        self._base = f"http://{host}:{port}/api/v1"
        self._headers = {"X-Api-Key": api_key}

    async def start_print(self, path: str):
        async with httpx.AsyncClient() as c:
            r = await c.post(
                f"{self._base}/job",
                headers=self._headers,
                json={"command": "start", "path": path},
            )
            r.raise_for_status()
```

## 4. mcp-3D-printer-server (unificazione)

[DMontgomery40/mcp-3D-printer-server](https://github.com/DMontgomery40/mcp-3D-printer-server) unifica Bambu, OctoPrint, Klipper, Duet, Prusa, Creality + operazioni STL (scala, rotazione) + slicing.

```python
"""
agents/maker-agent/mcp_printer_server.py
"""
from mcp.server import FastMCP
from agents.maker.moonraker_client import MoonrakerClient

mcp = FastMCP("jarvis-printer")
_moonraker = MoonrakerClient(host="192.168.1.100", port=7125)


@mcp.tool()
async def printer_start(filename: str) -> str:
    """Avvia stampa file presente sulla stampante."""
    await _moonraker.start_print(filename)
    return f"Stampa avviata: {filename}"


@mcp.tool()
async def printer_status() -> dict:
    """Stato corrente: temp, progresso, velocità."""
    return await _moonraker.get_printer_status()


@mcp.tool()
async def printer_cancel() -> str:
    await _moonraker.cancel_print()
    return "Stampa cancellata."
```

**Vantaggio:** ogni agente LangGraph chiama `printer.start`, `printer.status` senza conoscere se dietro c'è Moonraker, OctoPrint, Bambu o Prusa.

## 5. Slicer automation CLI

```python
"""
agents/maker-agent/slicer.py
"""
import subprocess
from dataclasses import dataclass
from pathlib import Path

PRUSA_SLICER_BIN = "/usr/bin/prusa-slicer"

MATERIAL_PROFILES = {
    "PLA":  "0.20mm QUALITY @MK4",
    "PETG": "0.20mm QUALITY PETG @MK4",
    "ABS":  "0.20mm QUALITY ABS @MK4",
    "TPU":  "0.30mm DRAFT TPU @MK4",
}


@dataclass(frozen=True)
class SliceResult:
    gcode_path: str
    estimated_time_s: int
    filament_used_g: float


def slice_stl(stl_path: str, output_dir: str, material: str = "PLA",
              printer: str = "Original Prusa MK4") -> SliceResult:
    if material not in MATERIAL_PROFILES:
        raise ValueError(material)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    gcode = str(out / f"{Path(stl_path).stem}.gcode")
    cmd = [
        PRUSA_SLICER_BIN, "--export-gcode", "--output", gcode,
        "--printer", printer,
        "--print-settings", MATERIAL_PROFILES[material],
        "--filament-settings", material,
        stl_path,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise RuntimeError(f"Slicer error:\n{r.stderr}")
    return SliceResult(gcode_path=gcode, estimated_time_s=_parse_time(r.stdout),
                       filament_used_g=_parse_filament(r.stdout))


def _parse_time(out: str) -> int:
    for line in out.splitlines():
        if "estimated printing time" in line.lower():
            parts = line.split("=")[-1].strip()
            seconds = 0
            for part in parts.split():
                if part.endswith("h"):
                    seconds += int(part[:-1]) * 3600
                elif part.endswith("m"):
                    seconds += int(part[:-1]) * 60
                elif part.endswith("s"):
                    seconds += int(part[:-1])
            return seconds
    return 0


def _parse_filament(out: str) -> float:
    for line in out.splitlines():
        if "filament used [g]" in line.lower():
            return float(line.split("=")[-1].strip())
    return 0.0
```

## 6. End-to-end LangGraph workflow

**Scenario:** "stampa un porta-penne esagonale"

```python
"""
agents/maker-agent/print_workflow.py
"""
import asyncio
import sys
import subprocess
from dataclasses import dataclass
from langgraph.graph import END, START, StateGraph
from agents.maker.moonraker_client import MoonrakerClient
from agents.maker.slicer import slice_stl

MOONRAKER_HOST = "192.168.1.100"
WORK_DIR = "/tmp/jarvis_maker"


@dataclass
class PrintState:
    user_request: str = ""
    glb_path: str = ""
    stl_path: str = ""
    gcode_path: str = ""
    filament_g: float = 0.0
    estimated_time_s: int = 0
    remote_filename: str = ""
    step: str = ""


async def generate_3d_model(state: PrintState) -> PrintState:
    try:
        glb = await _trellis_generate(state.user_request)
    except Exception:
        glb = await _meshy_generate(state.user_request)
    return PrintState(**{**state.__dict__, "glb_path": glb, "step": "generated"})


async def repair_mesh(state: PrintState) -> PrintState:
    stl = f"{WORK_DIR}/output.stl"
    r = subprocess.run(
        [sys.executable, "/opt/jarvis/maker/blender_pipeline.py",
         "--glb", state.glb_path, "--stl", stl, "--scale", "1.0"],
        capture_output=True, text=True, timeout=120,
    )
    if r.returncode != 0:
        raise RuntimeError(f"Blender: {r.stderr}")
    return PrintState(**{**state.__dict__, "stl_path": stl, "step": "repaired"})


async def slice_model(state: PrintState) -> PrintState:
    result = slice_stl(state.stl_path, f"{WORK_DIR}/gcode", material="PLA")
    return PrintState(**{
        **state.__dict__,
        "gcode_path": result.gcode_path,
        "filament_g": result.filament_used_g,
        "estimated_time_s": result.estimated_time_s,
        "step": "sliced",
    })


async def send_to_printer(state: PrintState) -> PrintState:
    client = MoonrakerClient(host=MOONRAKER_HOST)
    remote = "jarvis_print.gcode"
    await client.upload_file(state.gcode_path, remote)
    await client.start_print(remote)
    await client.close()
    return PrintState(**{**state.__dict__, "remote_filename": remote, "step": "printing"})


async def monitor_and_notify(state: PrintState) -> PrintState:
    client = MoonrakerClient(host=MOONRAKER_HOST)
    done = asyncio.Event()

    async def on_update(obj_name, data):
        if obj_name == "print_stats" and data.get("state") in ("complete", "error", "cancelled"):
            done.set()

    sub_task = asyncio.create_task(
        client.subscribe_and_watch(
            objects={"print_stats": ["state", "print_duration", "filament_used"]},
            on_update=on_update,
        )
    )
    await done.wait()
    sub_task.cancel()
    await client.close()
    return PrintState(**{**state.__dict__, "step": "complete"})


def build_print_graph():
    graph = StateGraph(PrintState)
    graph.add_node("generate_3d", generate_3d_model)
    graph.add_node("repair_mesh", repair_mesh)
    graph.add_node("slice", slice_model)
    graph.add_node("send_to_printer", send_to_printer)
    graph.add_node("monitor", monitor_and_notify)
    graph.add_edge(START, "generate_3d")
    graph.add_edge("generate_3d", "repair_mesh")
    graph.add_edge("repair_mesh", "slice")
    graph.add_edge("slice", "send_to_printer")
    graph.add_edge("send_to_printer", "monitor")
    graph.add_edge("monitor", END)
    return graph.compile()


async def run_print_job(user_request: str) -> PrintState:
    return await build_print_graph().ainvoke(PrintState(user_request=user_request))
```

## 7. Dependency summary

```toml
[project.optional-dependencies]
maker = [
    "bpy==4.3.0",
    "fake-bpy-module-4.3",
    "trimesh>=4.4.0",
    "websockets>=13.0",
    "httpx>=0.27.0",
    "paho-mqtt>=2.1.0",
    "langgraph>=0.2.0",
    "moonraker-api>=2.1.5",
]
```

## Riferimenti

- [TRELLIS-2 · Microsoft](https://github.com/microsoft/TRELLIS.2)
- [SPAR3D · Stability AI](https://github.com/Stability-AI/stable-point-aware-3d)
- [TripoSR · VAST AI](https://github.com/VAST-AI-Research/TripoSR)
- [Moonraker docs](https://moonraker.readthedocs.io/en/latest/external_api/printer/)
- [OctoEverywhere MCP](https://github.com/OctoEverywhere/mcp)
- [mcp-3D-printer-server](https://github.com/DMontgomery40/mcp-3D-printer-server)
- [bambu-moonraker-shim](https://github.com/justinh-rahb/bambu-moonraker-shim)
- [PrusaSlicer CLI](https://github.com/prusa3d/PrusaSlicer/wiki/Command-Line-Interface)
- [bpy 4.3.0 PyPI](https://pypi.org/project/bpy/4.3.0/)
