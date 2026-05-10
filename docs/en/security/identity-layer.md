---
title: "Identity Layer (M1.1) · Open-Jarvis"
description: "Authentication, sessions and MFA system of Open-Jarvis. Implemented in jarvis_server.identity. Argon2id, ES256 JWT, refresh rotation, RBAC, ABAC, MFA TOTP."
keywords: "open-jarvis identity, argon2id, es256, jwt, refresh rotation, mfa, totp, rbac"
---

# Identity Layer (M1.1)

> Authentication, sessions and MFA system of Open-Jarvis. Implemented
> in the `jarvis_server.identity` package.

Open-Jarvis adopts a **self-hosted, asymmetric, ABAC-ready** identity
layer: no cloud service is required to authenticate users, every
install generates (or mounts) its own ES256 keypair, and all identity
data stays inside the server's database.

## Components

| Module | Responsibility |
|--------|---------------|
| `identity.enums` | `Role`, `Permission`, `MfaMethod`, `DevicePlatform` |
| `identity.orm` | SQLAlchemy 2 models (`User`, `Device`, `Session`, `MfaCredential`, `AuditEvent`, `PairingCode`) |
| `identity.schemas` | Pydantic v2 DTOs (frozen) |
| `identity.passwords` | Argon2id hashing (OWASP-2025 parameters) |
| `identity.tokens` | ES256 JWT + refresh tokens (raw + SHA-256 hash + family) |
| `identity.mfa` | TOTP, email OTP, backup codes |
| `identity.pairing` | Single-use 6-digit + token pairing codes |
| `identity.service` | Workflows (`register`, `login`, `refresh`, `revoke_*`) |
| `api.deps` | FastAPI deps (`get_db`, `require_access_token`, RBAC) |
| `api.routes.auth` | REST endpoints `/api/v1/auth/*` |
| `api.routes.pairing` | REST endpoints `/api/v1/pairing/*` |

## Password storage

- Algorithm: **Argon2id**
- Parameters: `time_cost=3`, `memory_cost=128 MiB`, `parallelism=4`,
  `hash_len=32`, `salt_len=16` (OWASP guidelines, May 2025)
- Comparison: constant-time via `argon2-cffi` with auto-rehash on
  outdated parameters

## Token model

| Token | Algorithm | TTL | Storage |
|-------|-----------|-----|---------|
| Access | JWT ES256 (P-256 signed) | 15 min (`JARVIS_JWT_ACCESS_TTL_SECONDS`) | never persisted; in `Authorization: Bearer …` |
| Refresh | URL-safe random 48 bytes | 30 days (`JARVIS_JWT_REFRESH_TTL_SECONDS`) | DB (`sessions.refresh_token_hash`, SHA-256) |

Access token claims:

```
sub  : user UUID
did  : device UUID (optional)
jti  : unique id (matches the corresponding refresh)
fid  : family_id (groups rotations)
role : owner | admin | member | guest
iat / exp / iss / aud
```

### Refresh token rotation

On every `/api/v1/auth/refresh`:

1. Verify the refresh exists, isn't expired/revoked.
2. Mark the current row `is_revoked=True`.
3. Issue a new refresh **with the same `family_id`** and a new `jti`.
4. If a client sends a **previously rotated** refresh, the entire
   family is revoked (token-reuse detection) and the user must log in
   again. Prevents silent session theft.

## RBAC and ABAC

Four hierarchical roles: `OWNER > ADMIN > MEMBER > GUEST`. Each role
maps to a `frozenset[Permission]` (see `enums.ROLE_PERMISSIONS`).

Protected route example:

```python
from fastapi import APIRouter, Depends
from jarvis_server.api.deps import require_role, require_permission
from jarvis_server.identity.enums import Permission, Role

router = APIRouter(prefix="/api/v1/admin")

@router.get("/users", dependencies=[Depends(require_role(Role.ADMIN))])
async def list_users(): ...
```

## Multi-Factor Authentication

| Method | Detail |
|--------|--------|
| **TOTP** | RFC 6238, SHA-1, 6 digits, ±30 s window, inline PNG QR |
| **Email OTP** | numeric, 4-10 digits, Argon2id at-rest hash, configurable TTL |
| **Backup codes** | 10 16-char codes, Argon2id hashed, single-use |
| **Passkey / WebAuthn** | (M1.6, roadmap) |

When an MFA-enrolled user logs in, the endpoint returns an
`MfaChallenge` with `challenge_token` and `allowed_methods`. The
client must complete the verification within
`mfa_challenge_ttl_seconds` (default 300) before tokens are issued.

## Device pairing

Single-use pairing codes link new devices without re-typing creds.

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/v1/pairing/initiate` | Bearer | Generate 6-digit + URL-safe token (TTL 5 min) |
| `POST` | `/api/v1/pairing/redeem`   | — | Exchange the token for a device-bound `TokenPair` |

## Audit log

Every sensitive event lands in `audit_events`:

- `user.register`, `user.login` (success / fail / fail.disabled)
- `session.refresh`, `session.reuse`
- (future) `mfa.enrol`, `mfa.verify`, `oauth.link`

Append-only: writes happen in the same transaction as the originating
action.

## Configuration

```bash
# Database
JARVIS_DATABASE_URL=postgresql+psycopg://jarvis:secret@db:5432/jarvis

# JWT
JARVIS_JWT_PRIVATE_KEY_PEM="-----BEGIN PRIVATE KEY-----\n…"
JARVIS_JWT_PUBLIC_KEY_PEM="-----BEGIN PUBLIC KEY-----\n…"
JARVIS_JWT_ACCESS_TTL_SECONDS=900
JARVIS_JWT_REFRESH_TTL_SECONDS=2592000

# MFA
JARVIS_MFA_CHALLENGE_TTL_SECONDS=300
JARVIS_MFA_EMAIL_OTP_LENGTH=6
```

In **development** JWT keys may be omitted — the server builds an
ephemeral pair at first boot. In **production**
`Settings.assert_production_safe()` enforces them.

## REST endpoints

| Method | Path | Auth | Body | Response |
|--------|------|------|------|----------|
| `POST` | `/api/v1/auth/register` | — | `RegisterRequest` | `UserPublic` (201) |
| `POST` | `/api/v1/auth/login` | — | `LoginRequest` | `TokenPair` or `MfaChallenge` |
| `POST` | `/api/v1/auth/refresh` | — | `RefreshRequest` | `TokenPair` |
| `POST` | `/api/v1/auth/logout` | Bearer | — | 204 |
| `GET`  | `/api/v1/auth/me` | Bearer | — | `UserPublic` |

## Testing

The `tests/identity/` suite covers:

- password hashing & verification (5 unit tests)
- ES256 JWT issuance/verification + refresh rotation (8 unit tests)
- TOTP / email OTP / backup codes (15 unit tests)
- end-to-end service layer (10 unit tests)

`tests/integration/test_auth_endpoints.py` runs 11 HTTP scenarios over
ASGI (register/login/refresh/reuse-detection/me/logout) with in-memory
SQLite.

Identity module coverage: **>90%** (line + branch).

## References

- OWASP — *Password Storage Cheat Sheet* (2025)
- RFC 6238 — *TOTP*
- RFC 7519 — *JSON Web Token*
- IETF draft — *OAuth 2.1*
- NIST SP 800-63B — *Digital Identity Guidelines*
