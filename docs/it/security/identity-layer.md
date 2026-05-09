# Identity Layer (M1.1)

> Sistema di autenticazione, sessioni e MFA di Open-Jarvis. Implementato
> nel pacchetto `jarvis_server.identity`.

Open-Jarvis adotta un identity layer **self-hosted, asimmetrico e
ABAC-ready**: nessun servizio cloud è obbligatorio per autenticare gli
utenti, ogni installazione genera (o monta) la propria coppia di chiavi
ES256 e tutti i dati identitari rimangono nel database del server.

## Componenti

| Modulo | Responsabilità |
|--------|----------------|
| `identity.enums` | `Role`, `Permission`, `MfaMethod`, `DevicePlatform` |
| `identity.orm` | Modelli SQLAlchemy 2 (`User`, `Device`, `Session`, `MfaCredential`, `AuditEvent`) |
| `identity.schemas` | DTO Pydantic v2 (request/response, frozen) |
| `identity.passwords` | Hashing Argon2id con parametri OWASP-2025 |
| `identity.tokens` | JWT ES256 + refresh token (raw + SHA-256 hash + family) |
| `identity.mfa` | TOTP, email OTP, backup codes |
| `identity.service` | Orchestrazione (`register`, `login`, `refresh`, `revoke_*`) |
| `api.deps` | Dipendenze FastAPI (`get_db`, `require_access_token`, RBAC) |
| `api.routes.auth` | Endpoint REST `/api/v1/auth/*` |

## Storage delle password

- Algoritmo: **Argon2id**
- Parametri: `time_cost=3`, `memory_cost=128 MiB`, `parallelism=4`,
  `hash_len=32`, `salt_len=16` (linee guida OWASP, maggio 2025)
- Confronto: tempo costante via `argon2-cffi` con re-hash automatico in
  caso di parametri obsoleti

```python
from jarvis_server.identity import passwords as pw
hashed = pw.hash_password("super-secret-passphrase!")
assert pw.verify_password("super-secret-passphrase!", hashed)
```

## Token model

| Token | Algoritmo | TTL | Storage |
|-------|-----------|-----|---------|
| Access | JWT ES256 (firmato P-256) | 15 min (`JARVIS_JWT_ACCESS_TTL_SECONDS`) | mai persistito; viaggia in `Authorization: Bearer …` |
| Refresh | URL-safe random 48 byte | 30 giorni (`JARVIS_JWT_REFRESH_TTL_SECONDS`) | DB (`sessions.refresh_token_hash`, SHA-256) |

Claims dell'access token:

```
sub  : user UUID
did  : device UUID (opzionale)
jti  : id univoco (uguale al refresh corrispondente)
fid  : family_id (raggruppa rotazioni)
role : owner | admin | member | guest
iat / exp / iss / aud
```

### Refresh token rotation

Ad ogni `/api/v1/auth/refresh`:

1. Si verifica che il refresh esista e non sia scaduto/revocato.
2. Il record corrente viene marcato `is_revoked=True`.
3. Viene emesso un nuovo refresh con **lo stesso `family_id`** ma `jti`
   diverso.
4. Se un client invia un refresh **già rotato**, l'intera famiglia
   viene revocata (token-reuse detection) e l'utente è costretto a
   re-loggare. Questo previene il furto silenzioso di una sessione.

## RBAC e ABAC

Quattro ruoli gerarchici: `OWNER > ADMIN > MEMBER > GUEST`. Ogni ruolo
mappa a un `frozenset[Permission]` (vedi `enums.ROLE_PERMISSIONS`).

Esempio di route protetta:

```python
from fastapi import APIRouter, Depends
from jarvis_server.api.deps import require_role, require_permission
from jarvis_server.identity.enums import Permission, Role

router = APIRouter(prefix="/api/v1/admin")

@router.get("/users", dependencies=[Depends(require_role(Role.ADMIN))])
async def list_users(): ...

@router.post(
    "/llm/cloud",
    dependencies=[Depends(require_permission(Permission.LLM_CLOUD))],
)
async def call_cloud_llm(): ...
```

## Multi-Factor Authentication

| Metodo | Dettagli |
|--------|----------|
| **TOTP** | RFC 6238, SHA-1, 6 cifre, finestra ±30 s, generazione QR PNG inline |
| **Email OTP** | numerico, 4-10 cifre, hash Argon2id at-rest, TTL configurabile |
| **Backup codes** | 10 codici da 16 caratteri, hash Argon2id, monouso |
| **Passkey / WebAuthn** | (M1.6, in roadmap) |

Quando un utente con MFA attivo esegue il login, l'endpoint restituisce
una `MfaChallenge` con `challenge_token` e `allowed_methods`. Il client
deve completare la verifica entro `mfa_challenge_ttl_seconds` (default
300) prima che vengano emessi i token.

## Audit log

Ogni evento sensibile finisce in `audit_events`:

- `user.register`, `user.login` (success / fail / fail.disabled)
- `session.refresh`, `session.reuse`
- (futuro) `mfa.enrol`, `mfa.verify`, `oauth.link`

La tabella è **append-only**: i write avvengono dentro la stessa
transazione dell'azione che le origina, garantendo coerenza.

## Configurazione

```bash
# Database
JARVIS_DATABASE_URL=postgresql+asyncpg://jarvis:secret@db:5432/jarvis

# JWT
JARVIS_JWT_PRIVATE_KEY_PEM="-----BEGIN PRIVATE KEY-----\n…"
JARVIS_JWT_PUBLIC_KEY_PEM="-----BEGIN PUBLIC KEY-----\n…"
JARVIS_JWT_ACCESS_TTL_SECONDS=900
JARVIS_JWT_REFRESH_TTL_SECONDS=2592000

# MFA
JARVIS_MFA_CHALLENGE_TTL_SECONDS=300
JARVIS_MFA_EMAIL_OTP_LENGTH=6
```

In **development** le chiavi JWT possono essere omesse: il server ne
genera una coppia ephemera al primo avvio. In **produzione** vengono
imposte tramite `Settings.assert_production_safe()`.

## Endpoint REST

| Metodo | Path | Auth | Body | Risposta |
|--------|------|------|------|----------|
| `POST` | `/api/v1/auth/register` | — | `RegisterRequest` | `UserPublic` (201) |
| `POST` | `/api/v1/auth/login` | — | `LoginRequest` | `TokenPair` o `MfaChallenge` |
| `POST` | `/api/v1/auth/refresh` | — | `RefreshRequest` | `TokenPair` |
| `POST` | `/api/v1/auth/logout` | Bearer | — | 204 |
| `GET`  | `/api/v1/auth/me` | Bearer | — | `UserPublic` |

## Test

La suite `tests/identity/` copre:

- hashing & verification password (5 unit test)
- emissione/verifica JWT ES256 + rotazione refresh (8 unit test)
- TOTP / email OTP / backup codes (15 unit test)
- service layer end-to-end (10 unit test)

`tests/integration/test_auth_endpoints.py` esegue 11 scenari HTTP via
ASGI (register / login / refresh / reuse-detection / me / logout) con
SQLite in-memory.

Coverage del modulo identity: **>90 %** (linea + branch).

## Riferimenti

- OWASP — _Password Storage Cheat Sheet_ (2025)
- RFC 6238 — _TOTP: Time-Based One-Time Password Algorithm_
- RFC 7519 — _JSON Web Token_
- IETF draft — _OAuth 2.1_
- NIST SP 800-63B — _Digital Identity Guidelines_
