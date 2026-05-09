---
title: "Web auth · 2FA email + TOTP + Passkey"
description: "Gestione utenti, login, multi-factor authentication via email OTP, app authenticator TOTP (RFC 6238), WebAuthn passkey, hardware token."
keywords: "Argon2id, TOTP, WebAuthn, passkey, FIDO2, magic link, email OTP, GDPR, RBAC"
---

# Web Auth · Multi-2FA

**Stack mag 2026:** FastAPI 0.115, pyotp 2.9, webauthn 2.7.1, argon2-cffi 23.1, @simplewebauthn/browser 13.x

## 1. User profile

```python
from enum import Enum
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"  # TTL 48h


class ThemePreference(str, Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class PrivacyMode(str, Enum):
    STANDARD = "standard"
    REDUCED = "reduced"      # niente testo conversazioni in log
    ANONYMOUS = "anonymous"  # solo metadati tecnici


class UserProfile(BaseModel):
    id: UUID = uuid4()
    email: EmailStr
    display_name: str
    avatar_url: str | None = None
    role: UserRole = UserRole.MEMBER
    theme: ThemePreference = ThemePreference.SYSTEM
    language: str = "it"
    tts_voice: str | None = None
    privacy_mode: PrivacyMode = PrivacyMode.STANDARD
    mfa_enabled: bool = False
    created_at: datetime
    last_login_at: datetime | None = None
    is_active: bool = True
```

### Multi-utente isolation

Ogni query DB include `owner_id = current_user.id`. PostgreSQL Row-Level Security raccomandato come difesa in profondità.

### RBAC

```python
from fastapi import Depends, HTTPException

ROLE_HIERARCHY = {UserRole.OWNER: 4, UserRole.ADMIN: 3, UserRole.MEMBER: 2, UserRole.GUEST: 1}


def require_role(min_role: UserRole):
    def dep(current_user: UserProfile = Depends(get_current_user)):
        if ROLE_HIERARCHY[current_user.role] < ROLE_HIERARCHY[min_role]:
            raise HTTPException(403, "Permessi insufficienti")
        return current_user
    return dep


# Usage:
# @router.delete("/users/{uid}")
# async def delete_user(uid: UUID, _=Depends(require_role(UserRole.ADMIN))):
```

### Sezioni profilo UI

- **I miei dispositivi**: lista pairing attivi con `device_name`, `ip_address`, `last_seen`, pulsante revoca (server-side)
- **I miei dati GDPR**: export JSON/ZIP via task asincrono → email link entro 72h
- **Activity log**: timestamp, event_type, ip, user_agent. Visibile solo all'utente

## 2. Login flow base

### Argon2id (OWASP 2025)

```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Parametri OWASP 2025: memory=128MB, time=3, parallelism=4
_ph = PasswordHasher(time_cost=3, memory_cost=131072, parallelism=4, hash_len=32, salt_len=16)


def hash_password(plain: str) -> str:
    return _ph.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _ph.verify(hashed, plain)
    except VerifyMismatchError:
        return False


PASSWORD_POLICY = {
    "min_length": 12,
    "require_uppercase": True,
    "require_digit": True,
    "require_special": True,
    "pwned_check": True,  # API HaveIBeenPwned k-anonymity
}
```

### Magic link passwordless

JWT monouso ES256, scadenza 15 min, invalidato dopo uso (tabella `used_tokens`). Non riutilizzabile anche se intercettato.

### Session cookie

```python
SESSION_COOKIE_SETTINGS = {
    "key": "jarvis_session",
    "httponly": True,
    "secure": True,
    "samesite": "strict",
    "max_age": 86400 * 14,
    "path": "/",
}
```

### Brute force protection

- Per IP: 20 tentativi / 5 min (slowapi + Redis)
- Per account: 5 tentativi falliti consecutivi → lockout 15 min + notifica email
- 3 lockout in 24h → richiede verifica email

## 3. MFA implementations

### 3.1 TOTP (RFC 6238)

```python
import pyotp
import qrcode
import io
import base64
import secrets


def generate_totp_secret() -> str:
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str, issuer: str = "open-jarvis") -> str:
    return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer)


def generate_qr_base64(uri: str) -> str:
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def verify_totp(secret: str, code: str) -> bool:
    return pyotp.TOTP(secret).verify(code, valid_window=1)  # ±30s NTP drift


def generate_backup_codes(count: int = 10) -> list[str]:
    return [secrets.token_hex(5).upper() for _ in range(count)]
```

App compatibili: Google Authenticator, Authy, **Aegis** (open source raccomandato), 1Password, Bitwarden.

### 3.2 Email OTP

6 cifre, TTL 10 min, max 3 tentativi, rate limit 1 req/60s per utente. Codice hashato SHA-256 in DB.

### 3.3 SMS OTP (sconsigliato)

Vulnerabile a SIM swapping e SS7. Se necessario: provider OTP-specific (Twilio Verify, Vonage), TTL ≤ 5 min, **mai unico fattore** per operazioni alto rischio. NIST SP 800-63B deprecia SMS dal 2024.

### 3.4 WebAuthn / Passkey

Phishing-resistant by design (challenge include origin). Synced passkey AAL2-compliant (NIST 800-63-4 lug 2025).

```python
import webauthn
from webauthn.helpers.structs import PublicKeyCredentialDescriptor, AuthenticatorTransport

RP_ID = "jarvis.local"
RP_NAME = "open-jarvis"
ORIGIN = "https://jarvis.local"


def begin_registration(user_id: bytes, username: str, existing: list):
    return webauthn.generate_registration_options(
        rp_id=RP_ID,
        rp_name=RP_NAME,
        user_id=user_id,
        user_name=username,
        exclude_credentials=[
            PublicKeyCredentialDescriptor(id=c.credential_id) for c in existing
        ],
    )


def complete_registration(credential, challenge: bytes, expected_origin: str):
    return webauthn.verify_registration_response(
        credential=credential,
        expected_challenge=challenge,
        expected_rp_id=RP_ID,
        expected_origin=expected_origin,
    )


def begin_authentication(credentials: list):
    return webauthn.generate_authentication_options(
        rp_id=RP_ID,
        allow_credentials=[
            PublicKeyCredentialDescriptor(
                id=c.credential_id, transports=[AuthenticatorTransport.INTERNAL]
            )
            for c in credentials
        ],
    )


def complete_authentication(credential, challenge: bytes, stored_cred):
    return webauthn.verify_authentication_response(
        credential=credential,
        expected_challenge=challenge,
        expected_rp_id=RP_ID,
        expected_origin=ORIGIN,
        credential_public_key=stored_cred.public_key,
        credential_current_sign_count=stored_cred.sign_count,
    )
```

### 3.5 Hardware token U2F/FIDO2

YubiKey 5, Google Titan: stesso stack WebAuthn, nessuna libreria aggiuntiva. Raccomandato come 2FA obbligatorio per ruolo Owner.

### 3.6 Step-up auth

Operazioni sensibili (cambio email, cancellazione account) richiedono ri-auth ≤ 5 min:

```python
from datetime import datetime, timedelta, timezone
from fastapi import Request, HTTPException

STEP_UP_WINDOW = timedelta(minutes=5)


def require_step_up(request: Request) -> None:
    session = request.state.session
    verified_at = session.get("step_up_verified_at")
    if not verified_at:
        raise HTTPException(403, "step_up_required")
    if datetime.now(timezone.utc) - verified_at > STEP_UP_WINDOW:
        raise HTTPException(403, "step_up_expired")
```

## 4. FastAPI endpoint completi

```python
from fastapi import APIRouter, Response, Request, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from uuid import UUID

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TOTPVerifyRequest(BaseModel):
    session_token: str
    code: str


@router.post("/register", status_code=201)
async def register(body: dict):
    validate_password_policy(body["password"])
    hashed = hash_password(body["password"])
    user = await create_user(body["email"], hashed, body["display_name"])
    await send_verification_email(user.email)
    return {"message": "Verifica la tua email."}


@router.post("/login")
async def login(body: LoginRequest, response: Response):
    user = await get_user_by_email(body.email)
    if not user or not verify_password(body.password, user.password_hash):
        await record_failed_attempt(body.email)
        raise HTTPException(401, "Credenziali non valide.")
    if user.mfa_enabled:
        pending_token = create_pending_session(user.id)  # 5 min
        return {"mfa_required": True, "session_token": pending_token,
                "mfa_methods": user.enrolled_mfa_methods}
    set_session_cookie(response, create_session(user.id))
    return {"message": "Login completato."}


@router.post("/2fa/totp/verify")
async def verify_totp_endpoint(body: TOTPVerifyRequest, response: Response):
    user = await get_user_from_pending(body.session_token)
    if not verify_totp(user.totp_secret, body.code):
        raise HTTPException(401, "Codice TOTP non valido.")
    set_session_cookie(response, create_session(user.id))
    return {"message": "2FA completato."}


@router.post("/2fa/email/send")
async def send_email_otp(body: dict):
    user = await get_user_from_pending(body["session_token"])
    otp = generate_email_otp(user.id)
    await send_otp_email(user.email, otp)
    return {"message": "OTP inviato."}


@router.post("/2fa/email/verify")
async def verify_email_otp(body: dict, response: Response):
    user = await get_user_from_pending(body["session_token"])
    if not check_email_otp(user.id, body["code"]):
        raise HTTPException(401, "OTP non valido o scaduto.")
    set_session_cookie(response, create_session(user.id))
    return {"message": "2FA via email completato."}


@router.post("/passkey/register/begin")
async def passkey_register_begin(request: Request,
                                  current_user=Depends(get_current_user)):
    existing = await get_user_credentials(current_user.id)
    options = begin_registration(current_user.id.bytes, current_user.email, existing)
    request.session["webauthn_challenge"] = options.challenge
    return options


@router.post("/passkey/login")
async def passkey_login(request: Request, credential: dict, response: Response):
    user_handle = extract_user_handle(credential)
    user = await get_user_by_id(UUID(bytes=user_handle))
    stored = await get_credential(credential["id"])
    challenge = request.session.pop("webauthn_challenge", None)
    result = complete_authentication(credential, challenge, stored)
    await update_sign_count(stored.id, result.new_sign_count)
    set_session_cookie(response, create_session(user.id))
    return {"message": "Login con passkey completato."}
```

## 5. Frontend React

### Passkey

```typescript
// @simplewebauthn/browser 13.x
import { startRegistration, startAuthentication } from "@simplewebauthn/browser";


export async function registerPasskey(): Promise<void> {
  const opts = await fetch("/auth/passkey/register/begin", {
    method: "POST", credentials: "include",
  }).then(r => r.json());

  let attResp;
  try {
    attResp = await startRegistration({ optionsJSON: opts });
  } catch (err) {
    if (err instanceof Error && err.name === "InvalidStateError") {
      throw new Error("Passkey già registrata su questo dispositivo.");
    }
    throw err;
  }

  const verify = await fetch("/auth/passkey/register/complete", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(attResp),
  });
  if (!verify.ok) throw new Error("Registrazione fallita.");
}


export async function authenticateWithPasskey(): Promise<void> {
  const opts = await fetch("/auth/passkey/challenge", {
    method: "POST", credentials: "include",
  }).then(r => r.json());

  const authResp = await startAuthentication({ optionsJSON: opts });

  const verify = await fetch("/auth/passkey/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(authResp),
  });
  if (!verify.ok) throw new Error("Autenticazione fallita.");
}
```

### TOTP wizard

```tsx
import { useState, useEffect } from "react";


interface TOTPSetupData {
  qr_base64: string;
  backup_codes: string[];
  secret: string;
}


export function TOTPEnrollmentWizard() {
  const [step, setStep] = useState<"qr" | "verify" | "backup">("qr");
  const [setup, setSetup] = useState<TOTPSetupData | null>(null);
  const [code, setCode] = useState("");

  useEffect(() => {
    fetch("/auth/2fa/totp/setup/begin", { method: "POST", credentials: "include" })
      .then(r => r.json())
      .then(setSetup);
  }, []);

  async function confirm() {
    const r = await fetch("/auth/2fa/totp/setup/confirm", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ code }),
    });
    if (!r.ok) throw new Error("Codice non valido");
    setStep("backup");
  }

  if (step === "qr" && setup) {
    return (
      <div>
        <p>Scansiona con la tua app authenticator:</p>
        <img src={`data:image/png;base64,${setup.qr_base64}`} alt="QR TOTP" />
        <button onClick={() => setStep("verify")}>Continua</button>
      </div>
    );
  }
  if (step === "verify") {
    return (
      <div>
        <input value={code} onChange={e => setCode(e.target.value)}
               maxLength={6} autoComplete="one-time-code" placeholder="Codice 6 cifre" />
        <button onClick={confirm}>Verifica</button>
      </div>
    );
  }
  if (step === "backup" && setup) {
    return (
      <div>
        <p><strong>Salva questi codici di recupero — visibili solo ora:</strong></p>
        <pre>{setup.backup_codes.join("\n")}</pre>
        <p>Ogni codice è monouso. Conservali offline.</p>
      </div>
    );
  }
  return <div>Caricamento...</div>;
}
```

## 6. Email delivery

### Provider managed

| Provider | Free tier | DKIM/DMARC |
|---|---|---|
| **Postmark** | 100 msg/mese | automatico |
| **Mailgun** | 1000 msg/mese (EU) | configurabile |
| **AWS SES** | 62.000/mese da EC2 | configurabile |
| **Resend** | 3000/mese | automatico, SDK TS/Python |

### Self-hosted

- **Postal** (transactional, dashboard)
- **Mailcow** (Docker, completo)
- **Mail-in-a-Box** (single-domain)

Pro: zero dipendenze esterne. Contro: gestione blacklist IP, warm-up reputazione.

### Anti-bounce

Suppression list locale: bounce permanente (5xx) blocca futuri invii. Bounce soft (4xx) retry 3x con backoff esponenziale.

## 7. Best practice 2026

### Passkey-first sign-up

`window.PublicKeyCredential !== undefined` → CTA primario "Crea passkey". Email+password come secondaria. FIDO Alliance 2025: 87% aziende adotta FIDO2; team passkey-first vedono 50-70% adozione volontaria in 6 mesi.

### OIDC quick onboarding

"Sign in with Apple/Google" via authlib 1.4.x. Opzionale, disabilitato di default in Jarvis privacy-first.

### Privacy-preserving auth

No CDN esterni nel flow auth. Font, JS, QR serviti localmente. Log: solo metadata (timestamp, IP anonymized, user agent).

### Audit log

```python
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone


class AuditEvent(str, Enum):
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    MFA_ENROLLED = "mfa_enrolled"
    MFA_VERIFIED = "mfa_verified"
    PASSWORD_CHANGED = "password_changed"
    PASSKEY_REGISTERED = "passkey_registered"
    ACCOUNT_LOCKED = "account_locked"
    DATA_EXPORT_REQUESTED = "data_export_requested"
    ACCOUNT_DELETED = "account_deleted"


@dataclass(frozen=True)
class AuditRecord:
    user_id: UUID
    event: AuditEvent
    ip_address: str
    user_agent: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict = field(default_factory=dict)


async def record_audit_event(record: AuditRecord) -> None:
    await db.execute(
        "INSERT INTO audit_log VALUES ($1,$2,$3,$4,$5,$6)",
        record.user_id, record.event.value, record.ip_address,
        record.user_agent, record.timestamp, record.metadata
    )
```

## Dipendenze Python (mag 2026)

```text
fastapi==0.115.12
pydantic[email]==2.11.x
argon2-cffi==23.1.0
pyotp==2.9.0
qrcode[pil]==8.1.x
webauthn==2.7.1
slowapi==0.1.9
redis==5.2.x
python-jose[cryptography]==3.4.x
emails==0.6.x
```

## Frontend (mag 2026)

```json
{
  "@simplewebauthn/browser": "^13.0.0",
  "qrcode": "^1.5.4",
  "react": "^19.0.0",
  "typescript": "^5.8.x"
}
```

## Riferimenti

- [PyOTP](https://pyauth.github.io/pyotp/)
- [py_webauthn](https://github.com/duo-labs/py_webauthn)
- [SimpleWebAuthn](https://simplewebauthn.dev/)
- [Argon2 OWASP 2025](https://medium.com/@sumanbhadrasuman/password-security-in-2025-why-argon2id-is-the-standard-you-should-use-7c0797349836)
- [NIST SP 800-63-4 (lug 2025)](https://csrc.nist.gov/publications/detail/sp/800-63-4)
- [FIDO Alliance Passkeys 2025](https://cybersecurity.nusummit.com/blog/why-passkeys-are-finally-taking-over-in-2025/)
