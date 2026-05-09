---
title: "Deep-dive · Identity + Memory + LLM Router"
description: "Approfondimento tecnico su Identity Layer (OAuth, JWT, WebAuthn), Memory Layer (mem0, Qdrant, FHIR vault) e LLM Router per Open-Jarvis."
keywords: "identity layer, OAuth, WebAuthn, passkey, JWT, mem0, Qdrant, LLM router, Authentik"
---

# Deep-dive · Identity + Memory + LLM Router

**Phase:** 1 ([tracker](https://github.com/fedcal/open-jarvis/issues/10))
**Stack:** FastAPI 0.115+, Pydantic v2.7+, SQLAlchemy 2.x, Alembic 1.13+, mem0ai 2.0+, qdrant-client 1.9+, anthropic 0.42+, langgraph 1.0+

## 1. Identity Layer

### 1.1 Modelli dati con Pydantic v2

I modelli separano lo schema di lettura (risposta API) da quello di scrittura (input utente), con `ConfigDict(from_attributes=True)` per integrazione ORM con SQLAlchemy 2.x.

```python
# server/jarvis_server/identity/schemas.py
from __future__ import annotations
from datetime import datetime
from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class Role(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"


class Permission(StrEnum):
    MEMORY_READ = "memory:read"
    MEMORY_WRITE = "memory:write"
    HEALTH_READ = "health:read"
    DEVICE_MANAGE = "device:manage"
    LLM_CLOUD = "llm:cloud"


ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.OWNER: frozenset(Permission),
    Role.ADMIN: frozenset({Permission.MEMORY_READ, Permission.MEMORY_WRITE, Permission.DEVICE_MANAGE}),
    Role.MEMBER: frozenset({Permission.MEMORY_READ, Permission.MEMORY_WRITE}),
    Role.GUEST: frozenset({Permission.MEMORY_READ}),
}


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: EmailStr
    display_name: str = Field(min_length=2, max_length=64)
    role: Role
    is_active: bool
    created_at: datetime
    permissions: frozenset[Permission]

    @model_validator(mode="after")
    def derive_permissions(self) -> "UserRead":
        object.__setattr__(self, "permissions", ROLE_PERMISSIONS[self.role])
        return self


class DeviceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    name: str
    platform: str  # ios | android | web | desktop
    public_key_id: str  # WebAuthn credential ID base64url
    last_seen: datetime
    is_trusted: bool
```

### 1.2 OAuth 2.0 / OIDC + FIDO2/passkey

**Architettura raccomandata 2026:**

- Provider OIDC esterno (**Authentik** o Keycloak) come authority centrale
- **WebAuthn/FIDO2** (libreria `py_webauthn >= 2.2`) come secondo fattore hardware-bound
- **Synced passkeys** (NIST 800-63-4, lug 2025): soddisfano AAL2 senza hardware fisico

```python
# server/jarvis_server/identity/webauthn_routes.py
from fastapi import APIRouter, Depends
from webauthn import generate_registration_options, verify_registration_response
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    ResidentKeyRequirement,
)

router = APIRouter(prefix="/auth/webauthn")


@router.post("/register/begin")
async def begin_registration(user: UserRead = Depends(get_current_user)):
    options = generate_registration_options(
        rp_id="jarvis.local",
        rp_name="Open-Jarvis",
        user_id=str(user.id).encode(),
        user_name=user.email,
        user_display_name=user.display_name,
        authenticator_selection=AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.REQUIRED,
            user_verification=UserVerificationRequirement.REQUIRED,
        ),
    )
    await cache.set(f"webauthn:challenge:{user.id}", options.challenge, ex=300)
    return options
```

**Authentik vs Keycloak per personal AI:**

| Criterio | Authentik 2024.12+ | Keycloak 26+ |
|---|---|---|
| Setup iniziale | Basso (Python, flow-based UI) | Alto (Java, XML-heavy) |
| FIDO2/Passkey | Nativo, zero-config | Nativo ma config avanzata |
| RAM footprint | ~200MB | ~512MB |
| Multi-tenant | Brands | Realms |
| Scelta Jarvis | **Raccomandato** | Solo se già in corporate |

### 1.3 Device pairing via QR code (FIDO Cross-Device caBLE)

Il QR usa lo standard **FIDO Hybrid Transport**: `FIDO:/[version]:[qr-secret-base64url]:[known-domain-list]`

- `qr-secret`: 16 byte random per derivare chiavi sessione Noise_KK, monouso, scade dopo 90s
- BLE come proximity check (non canale dati) anti-relay
- Tunnel dati Noise Protocol cifrato via relay HTTPS

!!! warning "Sicurezza"
    Senza BLE proximity, QR relay attack sono possibili. Open-Jarvis richiede BLE proximity obbligatorio o limita pairing a stessa subnet LAN per device domestici.

```python
# server/jarvis_server/identity/device_pairing.py
import secrets
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class PairingChallenge:
    secret: bytes
    relay_url: str
    expires_at: float


def create_pairing_challenge(relay_url: str) -> tuple[PairingChallenge, str]:
    secret = secrets.token_bytes(16)
    challenge = PairingChallenge(
        secret=secret,
        relay_url=relay_url,
        expires_at=time.time() + 90,
    )
    qr_data = f"FIDO:/{secret.hex()}/{relay_url}"
    return challenge, qr_data
```

### 1.4 JWT short-lived + refresh con rotation e family revocation

**Schema temporale:**

- Access token: TTL **15 minuti**, RS256
- Refresh token: TTL **30 giorni**, opaque (sha256-hashed in PostgreSQL)
- Revoke list: Redis sorted set con `jti` come member, `expires_at` come score

```python
# server/jarvis_server/identity/tokens.py
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from jose import jwt

ALGORITHM = "RS256"
ACCESS_TTL = timedelta(minutes=15)
REFRESH_TTL = timedelta(days=30)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(user_id: str, jti: str, family_id: str, private_key: str) -> str:
    now = _utcnow()
    return jwt.encode(
        {"sub": user_id, "jti": jti, "fid": family_id, "iat": now, "exp": now + ACCESS_TTL},
        private_key,
        algorithm=ALGORITHM,
    )


def create_refresh_token() -> tuple[str, str]:
    """Returns (raw_token, sha256_hash). Store only the hash."""
    raw = secrets.token_urlsafe(48)
    return raw, hashlib.sha256(raw.encode()).hexdigest()


async def rotate_tokens(old_hash: str, db, cache, private_key: str) -> dict:
    """Token rotation: invalida vecchio, emette nuova coppia."""
    session = await db.scalar(
        select(Session).where(Session.refresh_token_hash == old_hash, Session.expires_at > _utcnow())
    )
    if session is None:
        # Replay attack: revoca tutta la famiglia
        await revoke_family(session.family_id, db, cache)
        raise HTTPException(401, "Token reuse detected — all sessions revoked")

    new_jti = str(uuid4())
    new_raw, new_hash = create_refresh_token()
    await db.execute(
        update(Session).where(Session.id == session.id).values(
            jti=new_jti,
            refresh_token_hash=new_hash,
            expires_at=_utcnow() + REFRESH_TTL,
        )
    )
    await cache.zadd("revoked_jtis", {session.jti: (_utcnow() + ACCESS_TTL).timestamp()})

    access = create_access_token(str(session.user_id), new_jti, session.family_id, private_key)
    return {"access_token": access, "refresh_token": new_raw}
```

### 1.5 Schema PostgreSQL + Alembic

```python
# migrations/versions/0001_identity_schema.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(254), nullable=False, unique=True),
        sa.Column("display_name", sa.String(64), nullable=False),
        sa.Column("role", sa.String(16), nullable=False, server_default="member"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
    )
    op.create_table(
        "devices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("platform", sa.String(32), nullable=False),
        sa.Column("public_key_id", sa.Text, nullable=False, unique=True),
        sa.Column("public_key_cbor", sa.LargeBinary, nullable=False),
        sa.Column("sign_count", sa.BigInteger, nullable=False, server_default="0"),
        sa.Column("is_trusted", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("last_seen", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_devices_user_id", "devices", ["user_id"])
    op.create_table(
        "sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("device_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("devices.id", ondelete="CASCADE"), nullable=True),
        sa.Column("jti", sa.String(64), nullable=False, unique=True),
        sa.Column("family_id", sa.String(64), nullable=False),
        sa.Column("refresh_token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("ip_address", sa.String(45)),
        sa.Column("user_agent", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_sessions_family_id", "sessions", ["family_id"])
    op.create_index("ix_sessions_expires_at", "sessions", ["expires_at"])
```

## 2. Memory Layer (4 tier)

### 2.1 Short-term — Redis con MessagePack

```python
import msgpack
from dataclasses import dataclass
from redis.asyncio import Redis

SHORT_TERM_TTL = 3600  # 1h


@dataclass(frozen=True)
class SessionContext:
    session_id: str
    user_id: str
    messages: tuple[dict, ...]
    metadata: dict


class ShortTermMemory:
    def __init__(self, redis: Redis):
        self._redis = redis

    async def append_message(self, session_id: str, message: dict) -> SessionContext:
        """Pattern immutabile: leggi → nuovo oggetto → scrivi."""
        existing = await self.get(session_id)
        if existing is None:
            raise ValueError(f"Session {session_id} not found")
        updated = SessionContext(
            session_id=existing.session_id,
            user_id=existing.user_id,
            messages=(*existing.messages, message),  # nuovo tuple
            metadata=existing.metadata,
        )
        await self._redis.set(
            f"ctx:{session_id}",
            msgpack.packb(updated.__dict__, use_bin_type=True),
            ex=SHORT_TERM_TTL,
        )
        return updated
```

### 2.2 Long-term — mem0 + PostgreSQL + Qdrant

mem0 v2.0.2 (mag 2026): 93.4 su LongMemEval (+26 vs versione precedente), scala fino a 1M token su BEAM.

```python
from mem0 import Memory

MEMORY_CONFIG = {
    "vector_store": {
        "provider": "qdrant",
        "config": {"collection_name": "jarvis_memories", "host": "qdrant", "port": 6333},
    },
    "llm": {
        "provider": "anthropic",
        "config": {"model": "claude-haiku-4-5", "temperature": 0.0},  # economico per estrazione
    },
}

memory = Memory.from_config(MEMORY_CONFIG)


async def remember_turn(user_id: str, session_id: str, agent_id: str, messages: list[dict]):
    """Scope: user_id (cross-session) · run_id (sessione) · agent_id (multi-agent)."""
    return memory.add(messages, user_id=user_id, run_id=session_id, agent_id=agent_id).get("results", [])


async def recall(query: str, user_id: str, limit: int = 5) -> list[dict]:
    return memory.search(query=query, user_id=user_id, limit=limit).get("results", [])
```

### 2.3 Semantic — Qdrant hybrid search

```python
from qdrant_client import QdrantClient, models

qdrant = QdrantClient(host="qdrant", port=6333)

qdrant.create_collection(
    "jarvis_knowledge",
    vectors_config={
        "dense": models.VectorParams(size=1024, distance=models.Distance.COSINE, on_disk=True)
    },
    sparse_vectors_config={
        "sparse": models.SparseVectorParams(modifier=models.Modifier.IDF)  # BM25 nativo
    },
)
qdrant.create_payload_index("jarvis_knowledge", "user_id", models.PayloadSchemaType.KEYWORD)
qdrant.create_payload_index("jarvis_knowledge", "created_at", models.PayloadSchemaType.DATETIME)
```

### 2.4 Health vault — HAPI FHIR isolato

Il servizio HAPI FHIR gira in rete Docker dedicata `jarvis-health-net`, **non esposta all'esterno**. Solo `health-gateway` con mTLS può accedere. I dati sanitari **non transitano** per il memory layer generico.

### 2.5 Decay & GC

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()


@scheduler.scheduled_job("interval", hours=24)
async def purge_stale_memories() -> None:
    cutoff = datetime.utcnow() - timedelta(days=365)
    # Qdrant: rimozione points oltre soglia
    old, _ = qdrant.scroll(
        collection_name="jarvis_knowledge",
        scroll_filter=models.Filter(must=[models.FieldCondition(
            key="created_at", range=models.DatetimeRange(lt=cutoff.isoformat())
        )]),
        limit=1000,
    )
    if old:
        qdrant.delete("jarvis_knowledge", points_selector=models.PointIdsList(points=[p.id for p in old]))
    # PG sessions, Redis revoke list scaduti
    await redis.zremrangebyscore("revoked_jtis", "-inf", datetime.utcnow().timestamp())
```

## 3. LLM Router

### 3.1 Capability-based routing

Il router valuta 4 dimensioni:

1. **Complessità**: lunghezza contesto, tool calls, ragionamento multi-step
2. **Privacy**: dati sanitari/PII → solo locale
3. **Latenza**: SLA UI (streaming, max ms)
4. **Costo**: budget mensile residuo

```python
from dataclasses import dataclass
from enum import StrEnum


class ModelTier(StrEnum):
    SMALL = "small"     # < 8B
    MEDIUM = "medium"   # 8-30B
    LARGE = "large"     # 30B+


class PrivacyLevel(StrEnum):
    PUBLIC = "public"
    PERSONAL = "personal"
    HEALTH = "health"   # solo locale


@dataclass(frozen=True)
class RoutingContext:
    prompt_tokens: int
    has_tool_calls: bool
    privacy_level: PrivacyLevel
    required_tier: ModelTier
    max_latency_ms: int
    user_budget_remaining: float


@dataclass(frozen=True)
class Provider:
    name: str
    model_id: str
    tier: ModelTier
    is_local: bool
    cost_per_1k_input: float
    cost_per_1k_output: float
    avg_latency_ms: int
    supports_tool_calls: bool
```

### 3.2 Provider registry

```python
PROVIDER_REGISTRY: list[Provider] = [
    # Locale (Ollama)
    Provider("ollama", "llama3.2:3b",       ModelTier.SMALL,  True,  0.0, 0.0,  200, False),
    Provider("ollama", "qwen2.5-coder:14b", ModelTier.MEDIUM, True,  0.0, 0.0,  800, True),
    Provider("ollama", "llama3.3:70b",      ModelTier.LARGE,  True,  0.0, 0.0, 4000, True),
    # Cloud
    Provider("anthropic", "claude-haiku-4-5",  ModelTier.SMALL,  False, 0.001, 0.005,  350, True),
    Provider("anthropic", "claude-sonnet-4-6", ModelTier.MEDIUM, False, 0.003, 0.015,  800, True),
    Provider("anthropic", "claude-opus-4-7",   ModelTier.LARGE,  False, 0.005, 0.025, 2000, True),
    Provider("openai",    "gpt-4.1-mini",      ModelTier.SMALL,  False, 0.0004, 0.0016, 400, True),
    Provider("groq",      "llama-3.3-70b",     ModelTier.LARGE,  False, 0.0006, 0.0006, 150, True),
]
```

### 3.3 Router con fallback

```python
class LLMRouter:
    def __init__(self, cloud_enabled: bool = True):
        self._cloud_enabled = cloud_enabled

    def route(self, ctx: RoutingContext) -> list[Provider]:
        """Ritorna lista [primary, fallback_1, ...] ordinata."""
        candidates = self._filter_candidates(ctx)
        return sorted(candidates, key=lambda p: self._score(p, ctx))

    def _filter_candidates(self, ctx: RoutingContext) -> list[Provider]:
        out = []
        for p in PROVIDER_REGISTRY:
            if ctx.privacy_level == PrivacyLevel.HEALTH and not p.is_local:
                continue
            if not self._cloud_enabled and not p.is_local:
                continue
            if ctx.has_tool_calls and not p.supports_tool_calls:
                continue
            cost = (ctx.prompt_tokens / 1000) * p.cost_per_1k_input
            if cost > ctx.user_budget_remaining:
                continue
            out.append(p)
        return out

    def _score(self, p: Provider, ctx: RoutingContext) -> float:
        latency_penalty = 0 if p.avg_latency_ms <= ctx.max_latency_ms else 10.0
        cost = p.cost_per_1k_input * 100
        local_bonus = -2.0 if p.is_local else 0.0
        return latency_penalty + cost + local_bonus
```

### 3.4 Prompt caching (Anthropic)

Cache abbatte costi 90% e latency 85% su prompt con system lungo o documenti grandi. Cache read = 0.1x prezzo base; write = 1.25x (ROI positivo dopo 1 hit).

```python
import anthropic

_client = anthropic.Anthropic()


async def complete_with_document_cache(document: str, question: str) -> str:
    response = _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=[
            {"type": "text", "text": "Sei Jarvis..."},
            {
                "type": "text",
                "text": document,
                "cache_control": {"type": "ephemeral", "ttl": "1h"},
            },
        ],
        messages=[{"role": "user", "content": question}],
    )
    return response.content[0].text
```

### 3.5 Cost tracking

```python
@dataclass(frozen=True)
class UsageRecord:
    provider: str
    model_id: str
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    cost_usd: float


async def record_usage(redis, user_id: str, record: UsageRecord) -> float:
    ym = datetime.utcnow().strftime("%Y-%m")
    key = f"budget:{user_id}:{ym}"
    new_total = await redis.incrbyfloat(key, record.cost_usd)
    await redis.expire(key, 60 * 60 * 24 * 35)
    if new_total > MONTHLY_BUDGET_USD * 0.9:
        await redis.set(f"budget_alert:{user_id}", "local_only", ex=3600)
    return new_total
```

## 4. Integrazione LangGraph completa

```python
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_id: str
    session_id: str
    privacy_level: str


def build_llm(provider: str, model: str):
    if provider == "ollama":
        return ChatOllama(model=model)
    if provider == "anthropic":
        return ChatAnthropic(model=model)
    raise ValueError(f"Unknown: {provider}")


async def jarvis_node(state: AgentState) -> AgentState:
    user_msg = state["messages"][-1].content
    memories = await recall(user_msg, state["user_id"], limit=5)
    memory_context = "\n".join(f"- {m['memory']}" for m in memories)

    ctx = RoutingContext(
        prompt_tokens=len(user_msg.split()) * 2,
        has_tool_calls=False,
        privacy_level=PrivacyLevel(state["privacy_level"]),
        required_tier=ModelTier.MEDIUM,
        max_latency_ms=2000,
        user_budget_remaining=5.0,
    )
    providers = LLMRouter().route(ctx)
    primary, *fallbacks = providers
    llm = build_llm(primary.name, primary.model_id)
    system = SystemMessage(content=f"Sei Jarvis. Memorie:\n{memory_context}")

    try:
        response = await llm.ainvoke([system] + state["messages"])
    except Exception:
        if fallbacks:
            llm = build_llm(fallbacks[0].name, fallbacks[0].model_id)
            response = await llm.ainvoke([system] + state["messages"])
        else:
            raise

    await remember_turn(state["user_id"], state["session_id"], "jarvis",
                        [{"role": "user", "content": user_msg},
                         {"role": "assistant", "content": response.content}])
    return {**state, "messages": [response]}


graph = (
    StateGraph(AgentState)
    .add_node("jarvis", jarvis_node)
    .add_edge(START, "jarvis")
    .add_edge("jarvis", END)
    .compile()
)
```

## 5. Note architetturali

- **Immutabilità**: tutti i modelli `frozen=True` o equivalente Pydantic
- **Privacy by design**: `PrivacyLevel` propagato dall'input fino alla scelta provider
- **Observability**: ogni call LLM logga `cache_read_input_tokens` per ROI caching
- **Fallback offline**: `cloud_enabled=False` → solo Ollama locale

## Riferimenti

- [mem0 implementation guide](https://sureprompts.com/blog/mem0-implementation-guide)
- [Mem0 + Qdrant](https://qdrant.tech/documentation/frameworks/mem0/)
- [Anthropic prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [Authentik 2025.12 release](https://docs.goauthentik.io/releases/2025.12/)
- [WebAuthn passkey QR codes](https://www.corbado.com/blog/webauthn-passkey-qr-code)
- [JWT lifecycle management](https://skycloak.io/blog/jwt-token-lifecycle-management-expiration-refresh-revocation-strategies/)
- [LangGraph 1.0](https://blog.langchain.com/langchain-langgraph-1dot0/)
