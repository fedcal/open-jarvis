---
title: "Deep-dive · Health Layer + Medical Wearables"
description: "Approfondimento tecnico su federazione wearable medicali, OAuth flows, HAPI FHIR vault, coaching engine, alerting e compliance GDPR."
keywords: "Oura, Whoop, Polar, Garmin, Dexcom CGM, HAPI FHIR, Open Wearables, biometric alerting, GDPR health"
---

# Deep-dive · Health Layer + Medical Wearables

**Phase:** 4 ([tracker](https://github.com/fedcal/open-jarvis/issues/13))
**Versione:** maggio 2026
**Stack Python:** httpx 0.28, pydantic 2.11, authlib 1.4, hvac 2.3, fhir-resources 8.0

## 1. Architettura del Medical Agent

### Provider abstraction

```python
# agents/medical-agent/providers/base.py
from abc import ABC, abstractmethod
from datetime import date
from pydantic import BaseModel


class SleepRecord(BaseModel):
    date: date
    total_sleep_minutes: int
    deep_sleep_minutes: int
    rem_sleep_minutes: int
    efficiency_pct: float
    latency_minutes: int
    source: str


class HRVRecord(BaseModel):
    timestamp: str
    rmssd_ms: float
    sdnn_ms: float | None = None
    source: str


class ActivityRecord(BaseModel):
    date: date
    steps: int
    active_calories: int
    distance_meters: float
    source: str


class BaseWearableProvider(ABC):
    provider_id: str
    display_name: str

    @abstractmethod
    async def fetch_sleep(self, days: int = 7) -> list[SleepRecord]: ...

    @abstractmethod
    async def fetch_hrv(self, days: int = 7) -> list[HRVRecord]: ...

    @abstractmethod
    async def fetch_activity(self, days: int = 7) -> list[ActivityRecord]: ...

    @abstractmethod
    async def refresh_token(self) -> None: ...
```

### Token vault

**Opzione A — HashiCorp Vault** (produzione):

```bash
vault secrets enable -path=jarvis/medical kv-v2
vault kv put jarvis/medical/oura/user_alice \
  access_token="<tok>" \
  refresh_token="<ref>" \
  expires_at="2026-05-09T18:00:00Z"
```

**Opzione B — age + sops** (self-hosted):

```bash
age-keygen -o ~/.config/jarvis/age.key
sops --age $(cat ~/.config/jarvis/age.key.pub) \
     --encrypt secrets/medical_tokens.yaml > secrets/medical_tokens.enc.yaml
```

### Polling vs webhook strategy

| Provider | Strategia | Latenza |
|---|---|---|
| Oura v2 | Polling 30 min | ~15 min lag |
| Whoop v2 | Webhook + polling fallback | Near real-time |
| Polar AccessLink | Polling on-demand | Dopo sync watch |
| Garmin Health | Push (partner program) | Near real-time |
| Withings | Webhook | Near real-time |
| Dexcom CGM | Polling 5 min | 1-3h delay |
| Apple HealthKit | Companion app push | iOS background |
| Google Health Connect | On-device SDK | Locale |

### Conflict resolution

```python
PROVIDER_PRIORITY = {
    "dexcom": 100,    # FDA-cleared
    "oura": 80,
    "whoop": 75,
    "polar": 70,
    "garmin": 65,
    "apple_healthkit": 60,
    "withings": 55,
}


def resolve_hr(readings: list[tuple[str, float]], strategy: str) -> float:
    if strategy == "highest_priority":
        return max(readings, key=lambda r: PROVIDER_PRIORITY.get(r[0], 0))[1]
    if strategy == "average":
        return sum(v for _, v in readings) / len(readings)
    if strategy == "most_recent":
        return readings[-1][1]
    raise ValueError(strategy)
```

## 2. Provider OAuth flows (esempi codice)

### Oura Ring v2 (OAuth 2.0)

```python
# Scope: email, personal, daily, heartrate, workout, spo2Daily
# Rate limit: 5000 req / 5 min · Token expiry: 1h

class OuraProvider(BaseWearableProvider):
    provider_id = "oura"

    def __init__(self, access_token, refresh_token, client_id, client_secret):
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._client_id = client_id
        self._client_secret = client_secret

    async def refresh_token(self):
        async with httpx.AsyncClient() as c:
            r = await c.post(
                "https://api.ouraring.com/oauth/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self._refresh_token,
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                },
            )
            r.raise_for_status()
            p = r.json()
            self._access_token = p["access_token"]
            self._refresh_token = p["refresh_token"]

    async def fetch_sleep(self, days=7):
        start = (date.today() - timedelta(days=days)).isoformat()
        async with httpx.AsyncClient() as c:
            r = await c.get(
                "https://api.ouraring.com/v2/usercollection/daily_sleep",
                headers={"Authorization": f"Bearer {self._access_token}"},
                params={"start_date": start},
            )
            r.raise_for_status()
            return [
                SleepRecord(
                    date=item["day"],
                    total_sleep_minutes=item["contributors"]["total_sleep"] // 60,
                    deep_sleep_minutes=item["contributors"]["deep_sleep"] // 60,
                    rem_sleep_minutes=item["contributors"]["rem_sleep"] // 60,
                    efficiency_pct=item["contributors"]["efficiency"],
                    latency_minutes=item["contributors"]["latency"] // 60,
                    source="oura",
                )
                for item in r.json().get("data", [])
            ]
```

### Whoop v2 (OAuth + Webhook HMAC)

```python
class WhoopProvider(BaseWearableProvider):
    provider_id = "whoop"

    def validate_webhook_signature(self, raw_body: bytes, signature: str) -> bool:
        expected = hmac.new(
            self._webhook_secret.encode(), raw_body, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    async def fetch_sleep(self, days=7):
        start = (date.today() - timedelta(days=days)).isoformat()
        async with httpx.AsyncClient() as c:
            r = await c.get(
                "https://api.prod.whoop.com/developer/v1/activity/sleep",
                headers={"Authorization": f"Bearer {self._access_token}"},
                params={"start": f"{start}T00:00:00.000Z", "limit": 25},
            )
            r.raise_for_status()
            return [_to_sleep_record(item) for item in r.json().get("records", [])]


# Subscribe webhook (one-time)
async def subscribe_whoop_webhook(token: str, callback_url: str):
    async with httpx.AsyncClient() as c:
        await c.post(
            "https://api.prod.whoop.com/developer/v1/webhook",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "url": callback_url,
                "event_types": ["recovery.updated", "sleep.updated", "workout.updated"],
            },
        )
```

### Garmin Health API (OAuth 1.0a — attenzione sicurezza)

OAuth 1.0a usa HMAC-SHA1, niente refresh token, token a lunga scadenza. Richiede approvazione partner program. La libreria `requests_oauthlib` gestisce la firma.

### Withings, Fitbit/Google Health, Dexcom

- **Withings**: OAuth 2.0 web flow, sandbox available
- **Fitbit/Google Health**: migrazione completa entro settembre 2026, re-consent obbligatorio
- **Dexcom CGM**: OAuth 2.0, FDA-cleared. Limited Access (max 5 utenti) — Full Access via partnership

## 3. HAPI FHIR vault

### Deploy con Docker

```yaml
services:
  hapi-fhir:
    image: hapiproject/hapi:v7.4.0
    container_name: jarvis-fhir
    ports:
      - "8080:8080"
    environment:
      hapi.fhir.fhir_version: R4
      hapi.fhir.server_address: "https://fhir.jarvis.local/fhir"
      spring.datasource.url: "jdbc:postgresql://fhir-db:5432/hapi"
      spring.datasource.username: "${FHIR_DB_USER}"
      spring.datasource.password: "${FHIR_DB_PASS}"
    depends_on:
      - fhir-db
    networks:
      - jarvis-health-net   # rete isolata, non esposta

  fhir-db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: hapi
      POSTGRES_USER: "${FHIR_DB_USER}"
      POSTGRES_PASSWORD: "${FHIR_DB_PASS}"
    volumes:
      - fhir_pgdata:/var/lib/postgresql/data
    networks:
      - jarvis-health-net

volumes:
  fhir_pgdata:

networks:
  jarvis-health-net:
    driver: bridge
    internal: true   # nessuna connettività esterna
```

### FHIR Observation mapping (HR · HRV · Glucose · Sleep)

**Heart rate (LOINC 8867-4):**

```json
{
  "resourceType": "Observation",
  "status": "final",
  "category": [{ "coding": [{ "code": "vital-signs" }] }],
  "code": { "coding": [{ "system": "http://loinc.org", "code": "8867-4", "display": "Heart rate" }] },
  "subject": { "reference": "Patient/jarvis-user-alice" },
  "effectiveDateTime": "2026-05-09T07:32:00+02:00",
  "valueQuantity": { "value": 52, "unit": "/min", "system": "http://unitsofmeasure.org" },
  "device": { "display": "Oura Ring v3" }
}
```

**Glucose (LOINC 41653-7):**

```json
{
  "resourceType": "Observation",
  "code": { "coding": [{ "system": "http://loinc.org", "code": "41653-7" }] },
  "valueQuantity": { "value": 98, "unit": "mg/dL" },
  "interpretation": [{ "coding": [{ "code": "N", "display": "Normal" }] }],
  "device": { "display": "Dexcom G7 (FDA-cleared)" }
}
```

### SMART on FHIR (condivisione con medico)

```text
Scopes tipici:
patient/Observation.read
patient/Observation.write
patient/Patient.read
launch/patient
openid fhirUser
```

### Backup cifrato

```bash
pg_dump -h localhost -U $FHIR_DB_USER hapi \
  | age --recipient $(cat ~/.config/jarvis/age.key.pub) \
  > /backups/fhir/$(date +%Y%m%d).sql.age
```

## 4. Open Wearables middleware

[Open Wearables](https://openwearables.io/) (MIT) unifica 10 provider in un'API self-hosted: Garmin, Whoop, Oura, Strava, Apple Health, Samsung Health, Google Health Connect, Polar, Suunto, Ultrahuman.

```python
# Accesso unificato
async with httpx.AsyncClient(base_url="http://openwearables:3000") as c:
    sleep = await c.get("/api/sleep", params={"days": 7})
    hrv = await c.get("/api/hrv", params={"days": 7})
```

**Raccomandazione Jarvis:** Open Wearables come strato di acquisizione grezzo + layer FHIR + conflict resolution + coaching custom.

## 5. Apple HealthKit / Google Health Connect

- **HealthKit**: on-device only, no cloud API. Pattern: companion app iOS con `HKAnchoredObjectQuery` → upload mTLS al server Jarvis.
- **Health Connect**: SDK locale Android 14+. Letto on-device, sincronizzato via REST con server.

## 6. Coaching engine

```python
class CoachingContext(BaseModel):
    user_id: str
    avg_hrv_7d: float
    hrv_trend: str
    avg_sleep_efficiency: float
    resting_hr_trend: str
    training_load_7d: str
    glucose_avg_mgdl: float | None = None


COACHING_PROMPT = """
Sei un coach della salute personale. Analizza i dati biometrici degli ultimi
7 giorni e fornisci raccomandazioni concrete. NON fare diagnosi mediche.
Output: 1 insight principale + 1 raccomandazione immediata + 1 settimanale.
DISCLAIMER: Non sostituisce il parere del medico.
"""
```

PH-LLM (Nature Medicine 2025): LLM fine-tuned su 15 giorni di dati supera esperti umani in sleep medicine (79% vs 76%).

## 7. Biometric alerting engine (YAML)

```yaml
rules:
  - id: hrv_declining
    condition:
      metric: hrv_rmssd_7d_avg
      operator: lt
      threshold_factor: 0.80
      baseline_window_days: 30
    severity: warning
    cooldown_hours: 24
    dispatch:
      - channel: chat
      - channel: mobile_push
        message: "HRV in calo: considera un giorno di recupero."

  - id: glucose_high
    condition:
      metric: glucose_mgdl
      operator: gt
      value: 180
    severity: critical
    cooldown_hours: 1
    dispatch:
      - channel: watch_haptic
        pattern: "sos"
      - channel: mobile_push
        message: "Glicemia a {value} mg/dL. Controlla e agisci."
```

## 8. Privacy & compliance

### GDPR Art. 9 — Categorie speciali

- **Base giuridica**: consenso esplicito (Art. 9.2.a) o tutela salute (Art. 9.2.h)
- **DPIA obbligatoria** prima del deploy
- **Data minimization**: solo dati necessari
- **Retention policy** definita

### Audit log

```python
class AuditEvent(BaseModel):
    timestamp: str
    user_id: str
    action: str  # read|write|delete|export
    resource_type: str
    resource_id: str
    provider: str
    outcome: str  # success|denied|error


def log_health_access(event: AuditEvent) -> None:
    log.info("health_data_access", **event.model_dump())
    # Scrivere anche FHIR AuditEvent resource
```

### Right to be forgotten (Art. 17)

```python
async def delete_user_health_data(user_id: str, fhir_base: str, token: str):
    async with httpx.AsyncClient() as c:
        # Cancella Observation
        search = await c.get(
            f"{fhir_base}/Observation",
            headers={"Authorization": f"Bearer {token}"},
            params={"subject": f"Patient/{user_id}"},
        )
        for entry in search.json().get("entry", []):
            await c.delete(
                f"{fhir_base}/Observation/{entry['resource']['id']}",
                headers={"Authorization": f"Bearer {token}"},
            )
        # Cancella Patient
        await c.delete(
            f"{fhir_base}/Patient/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        # Revoca tutti i token OAuth dal vault (operazione separata)
```

### Disclaimer medico (obbligatorio)

> Le informazioni hanno finalità informative e di supporto al benessere. Non costituiscono diagnosi medica e non sostituiscono il consulto di un professionista sanitario abilitato. In caso di sintomi consultare sempre un medico.

## Riferimenti

- [Oura API Authentication](https://cloud.ouraring.com/docs/authentication)
- [Whoop OAuth + webhooks](https://developer.whoop.com/docs/developing/oauth/)
- [Polar AccessLink Python](https://github.com/polarofficial/accesslink-example-python)
- [Garmin Health API](https://developer.garmin.com/gc-developer-program/health-api/)
- [Dexcom Developer](https://developer.dexcom.com/)
- [HAPI FHIR Docker](https://hub.docker.com/r/hapiproject/hapi)
- [SMART on FHIR](https://docs.smarthealthit.org/)
- [Open Wearables](https://github.com/the-momentum/open-wearables)
- [PH-LLM · Nature Medicine 2025](https://www.nature.com/articles/s41591-025-03888-0)
