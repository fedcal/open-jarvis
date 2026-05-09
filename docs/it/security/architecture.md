---
title: "Architettura di sicurezza · VPS hardening + threat model"
description: "Sicurezza completa Open-Jarvis: VPS hardening, WireGuard mesh, mTLS, OWASP Top 10, JWT ES256, threat modeling STRIDE, GDPR compliance, supply chain security."
keywords: "VPS hardening, fail2ban, Caddy TLS 1.3, WireGuard, Tailscale, mTLS, OWASP, STRIDE, SLSA Level 3, sops, age, Vault"
---

# Architettura di sicurezza

Postura di sicurezza completa per Open-Jarvis: VPS cloud + dispositivi personali (PC, smartphone, smartwatch, occhiali AR, wearable medicali).

## 1. VPS hardening

### 1.1 SSH hardening

```ini
# /etc/ssh/sshd_config
Port 2222
AddressFamily inet
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3
LoginGraceTime 20
ClientAliveInterval 300
ClientAliveCountMax 2
AllowUsers jarvis
X11Forwarding no
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com
KexAlgorithms curve25519-sha256,diffie-hellman-group16-sha512
```

```bash
ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key
rm -f /etc/ssh/ssh_host_rsa_key /etc/ssh/ssh_host_dsa_key
systemctl restart sshd
```

**fail2ban v1.1.x:**

```ini
# /etc/fail2ban/jail.d/jarvis-ssh.conf
[sshd]
enabled  = true
port     = 2222
maxretry = 3
bantime  = 3600
findtime = 600
backend  = systemd
```

### 1.2 Firewall (default-deny)

Solo 3 porte esposte: 443 HTTPS, 2222 SSH, 51820 WireGuard.

```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow 2222/tcp comment "SSH hardened"
ufw allow 443/tcp  comment "HTTPS TLS 1.3"
ufw allow 51820/udp comment "WireGuard VPN"
ufw limit 2222/tcp
ufw enable
```

### 1.3 Reverse proxy: Caddy 2.9 (TLS 1.3 auto)

```caddyfile
{
  email admin@yourdomain.com
  servers {
    protocols h1 h2 h3
  }
}

jarvis.yourdomain.com {
  tls {
    protocols tls1.3
    curves    x25519
  }

  header {
    Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
    Content-Security-Policy   "default-src 'self'; script-src 'self'; object-src 'none'"
    X-Frame-Options           "DENY"
    X-Content-Type-Options    "nosniff"
    Referrer-Policy           "strict-origin-when-cross-origin"
    Permissions-Policy        "geolocation=(), microphone=(self), camera=(self)"
    -Server
    -X-Powered-By
  }

  rate_limit {
    zone api_global {
      key   {remote_host}
      events 100
      window 1m
    }
  }

  reverse_proxy /api/* localhost:8000
  reverse_proxy /* localhost:3000
}
```

### 1.4 Container security

```dockerfile
# Distroless multi-stage
FROM python:3.13-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM gcr.io/distroless/python3-debian12:nonroot
COPY --from=builder /root/.local /root/.local
COPY --chown=nonroot:nonroot ./app /app
USER nonroot
WORKDIR /app
EXPOSE 8000
ENTRYPOINT ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose hardened
services:
  api:
    image: ghcr.io/open-jarvis/api:latest
    user: "65532:65532"
    read_only: true
    tmpfs: ["/tmp:size=64m,mode=1777"]
    security_opt:
      - apparmor:jarvis-api
      - no-new-privileges:true
      - seccomp:./seccomp/api.json
    cap_drop: [ALL]
    cap_add: [NET_BIND_SERVICE]
```

!!! warning "Trivy → Grype 2026"
    Trivy rimosso dalla pipeline CI dopo supply chain attacks marzo 2026. Sostituito con **Syft** (SBOM) + **Grype** (vulnerability scan).

```bash
syft ghcr.io/open-jarvis/api:latest -o cyclonedx-json > sbom.json
grype ghcr.io/open-jarvis/api:latest --fail-on high
```

### 1.5 AppArmor profile

```bash
# /etc/apparmor.d/jarvis-api
#include <tunables/global>
profile jarvis-api flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>
  network inet tcp,
  network inet udp,
  deny network raw,
  /app/** r,
  /tmp/  rw,
  deny /etc/shadow r,
  deny /proc/*/mem rw,
  capability net_bind_service,
  deny capability sys_admin,
}
```

```bash
apparmor_parser -r /etc/apparmor.d/jarvis-api
```

### 1.6 Audit log: auditd + Loki

```text
# /etc/audit/rules.d/jarvis.rules
-w /etc/ssh/sshd_config -p wa -k jarvis_ssh_config
-w /app/server/auth/    -p rwxa -k jarvis_auth
-a always,exit -F arch=b64 -S execve -k jarvis_exec
-a always,exit -F arch=b64 -S open -F exit=-EACCES -k jarvis_access_denied
-w /etc/passwd -p wa -k jarvis_identity
```

Forwarding via Promtail → Loki per query.

## 2. Network security VPS ↔ devices

### WireGuard hub-and-spoke

```ini
# /etc/wireguard/wg0.conf — VPS hub
[Interface]
Address    = 10.10.0.1/24
ListenPort = 51820
PrivateKey = <VPS_PRIVATE_KEY>
PostUp     = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown   = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]   # Desktop
PublicKey  = <DESKTOP_PUB>
AllowedIPs = 10.10.0.2/32

[Peer]   # Mobile
PublicKey  = <MOBILE_PUB>
AllowedIPs = 10.10.0.3/32

[Peer]   # Watch
PublicKey  = <WATCH_PUB>
AllowedIPs = 10.10.0.4/32
```

### Tailscale (managed alternative)

```bash
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up --authkey=tskey-... --advertise-tags=tag:jarvis-node
```

ACL JSON:

```json
{
  "tagOwners": { "tag:jarvis-node": ["autogroup:admin"] },
  "acls": [
    { "action": "accept",
      "src": ["tag:jarvis-node"],
      "dst": ["tag:jarvis-node:8000"] }
  ]
}
```

### mTLS inter-service

```python
import httpx
import ssl


def build_mtls_client(cert: str, key: str, ca: str) -> httpx.Client:
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=ca)
    ctx.load_cert_chain(certfile=cert, keyfile=key)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_3
    ctx.verify_mode = ssl.CERT_REQUIRED
    return httpx.Client(verify=ctx, timeout=10.0)
```

### Cloudflare Tunnel (zero-trust)

```yaml
# cloudflared/config.yml
tunnel: <TUNNEL_ID>
credentials-file: /etc/cloudflared/credentials.json
ingress:
  - hostname: api.jarvis.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404
```

Cloudflare Zero Trust Access aggiunge SSO davanti.

### IP allowlist admin

```caddyfile
@admin_external {
  path /admin/*
  not remote_ip 10.10.0.0/24
}
handle @admin_external { respond 403 }
```

## 3. Application-layer security

### OWASP Top 10 2025 mitigations

| Rischio | Mitigazione Jarvis |
|---|---|
| A01 Broken Access Control | RBAC + IDOR checks su ogni query DB |
| A02 Crypto Failures | TLS 1.3 forzato, bcrypt cost=12, AES-256-GCM at-rest |
| A03 Injection | Pydantic strict + SQLAlchemy ORM, no raw SQL |
| A04 Insecure Design | Threat model STRIDE per ogni componente |
| A05 Misconfig | Hardening checklist in CI, Semgrep |
| A07 Auth Failures | JWT ES256 + refresh rotation + family revocation |
| A10 SSRF | Whitelist URL scraping, blocco IMDS 169.254.169.254 |

### Rate limiting (slowapi + Redis)

```python
from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379",
    default_limits=["200/minute", "2000/hour"],
)


def create_app() -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None)  # disabilita /docs in prod
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    return app


@router.post("/chat")
@limiter.limit("30/minute")
async def chat(request: Request, body: ChatRequest):
    ...
```

### Input validation strict

```python
from pydantic import BaseModel, Field, field_validator
from typing import Annotated
import re

ALLOWED_DEVICES = frozenset({"desktop", "mobile", "watch", "glasses", "vr"})


class ChatRequest(BaseModel):
    model_config = {"strict": True, "extra": "forbid"}
    message: Annotated[str, Field(min_length=1, max_length=4096)]
    device_id: Annotated[str, Field(pattern=r"^[a-zA-Z0-9\-]{8,64}$")]
    device_type: str
    session_id: Annotated[str, Field(pattern=r"^[a-f0-9\-]{36}$")]

    @field_validator("message")
    @classmethod
    def sanitize(cls, v: str) -> str:
        cleaned = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", v)
        if not cleaned:
            raise ValueError("Empty after sanitization")
        return cleaned

    @field_validator("device_type")
    @classmethod
    def valid_device(cls, v: str) -> str:
        if v not in ALLOWED_DEVICES:
            raise ValueError(f"device_type must be one of {ALLOWED_DEVICES}")
        return v
```

### Secret management: age + sops

```yaml
# .sops.yaml
creation_rules:
  - path_regex: infra/secrets/.*\.ya?ml
    age: age1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

```bash
sops --encrypt --age $(cat ~/.config/sops/age/keys.txt | grep "public key" | awk '{print $NF}') \
     infra/secrets/api_keys.yaml > infra/secrets/api_keys.enc.yaml
```

### HashiCorp Vault (enterprise dynamic secrets)

```python
import hvac
from functools import lru_cache


@lru_cache(maxsize=1)
def get_vault_client() -> hvac.Client:
    client = hvac.Client(url="https://vault.internal:8200")
    client.auth.approle.login(
        role_id=os.environ["VAULT_ROLE_ID"],
        secret_id=os.environ["VAULT_SECRET_ID"],
    )
    return client


def get_llm_api_key(provider: str) -> str:
    client = get_vault_client()
    secret = client.secrets.kv.v2.read_secret_version(
        path=f"jarvis/llm/{provider}", mount_point="secret"
    )
    return secret["data"]["data"]["api_key"]
```

## 4. API security

### OAuth 2.1 + PKCE obbligatorio

```python
import hashlib
import secrets
import base64
from dataclasses import dataclass


@dataclass(frozen=True)
class PKCEChallenge:
    verifier: str
    challenge: str
    method: str = "S256"


def generate_pkce_challenge() -> PKCEChallenge:
    verifier = secrets.token_urlsafe(64)  # 86 chars ≈ 512 bit
    digest = hashlib.sha256(verifier.encode()).digest()
    return PKCEChallenge(
        verifier=verifier,
        challenge=base64.urlsafe_b64encode(digest).rstrip(b"=").decode(),
    )
```

### JWT ES256 + family revocation

```python
from datetime import datetime, timedelta, timezone
from jose import jwt
import uuid

ACCESS_TTL = timedelta(minutes=15)
REFRESH_TTL = timedelta(days=30)


def create_access_token(user_id: str, device_id: str, private_key: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id, "did": device_id,
        "iat": now, "exp": now + ACCESS_TTL,
        "jti": str(uuid.uuid4()),
        "iss": "open-jarvis", "aud": "jarvis-api",
    }
    return jwt.encode(payload, private_key, algorithm="ES256")


def create_refresh_token(user_id: str, family_id: str, private_key: str) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": user_id, "family": family_id,
            "iat": now, "exp": now + REFRESH_TTL,
            "jti": str(uuid.uuid4()), "type": "refresh",
        },
        private_key,
        algorithm="ES256",
    )
```

### Webhook signature verification

```python
import hashlib
import hmac
import time
from fastapi import HTTPException, Header, Request

WEBHOOK_MAX_AGE = 300  # 5 min


async def verify_webhook(
    request: Request,
    x_signature: str = Header(..., alias="X-Jarvis-Signature"),
    x_timestamp: str = Header(..., alias="X-Jarvis-Timestamp"),
    secret: str = "",
) -> bytes:
    ts = int(x_timestamp)
    if abs(time.time() - ts) > WEBHOOK_MAX_AGE:
        raise HTTPException(400, "Timestamp expired")
    body = await request.body()
    expected = hmac.new(
        secret.encode(), f"{x_timestamp}.".encode() + body, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(f"sha256={expected}", x_signature):
        raise HTTPException(401, "Invalid signature")
    return body
```

## 5. Threat modeling STRIDE

| Componente | Spoofing | Tampering | Info Disclosure | DoS | Elevation |
|---|---|---|---|---|---|
| API Gateway | JWT forgery | Body injection | Response leaks | HTTP flood | SSRF → IMDS |
| WireGuard | Peer impersonation | Rogue peer | Traffic analysis | UDP flood | Pivot LAN |
| Memory (Qdrant) | Unauth access | Vector poisoning | Memory exfil | Bulk insert OOM | Admin API |
| LLM Router | Provider impersonation | Prompt injection | Prompt leak | Token budget | Tool abuse |
| Mobile Agent | Device cloning | Binary tampering | Keystroke capture | Battery drain | Root via exploit |
| Auth | Token replay | DB tamper | Hash leak | Login flood | Privilege escalation JWT |

### Defense in depth

```text
Livello 1 — Perimetro:   Cloudflare WAF + DDoS
Livello 2 — Network:     nftables default-deny + WireGuard
Livello 3 — Transport:   TLS 1.3 + mTLS inter-service
Livello 4 — Application: JWT ES256 + OAuth 2.1 PKCE + Rate Limit
Livello 5 — Data:        Pydantic strict + parameterized queries
Livello 6 — Secrets:     Vault dynamic + sops at-rest
Livello 7 — Runtime:     Distroless + rootless + seccomp + AppArmor
Livello 8 — Audit:       auditd + Loki + Wazuh alerting
```

## 6. Detect & respond

### Wazuh 4.11 SIEM self-hosted

```yaml
services:
  wazuh-manager:
    image: wazuh/wazuh-manager:4.11.0
    volumes:
      - wazuh_data:/var/ossec/data
      - ./custom_rules:/var/ossec/etc/rules/local_rules.xml:ro
    ports:
      - "1514:1514/udp"
      - "55000:55000"
```

### Honeypot endpoint

```python
from fastapi import APIRouter, Request
import logging

router = APIRouter()
hp = logging.getLogger("jarvis.honeypot")


@router.get("/api/v0/admin")
@router.post("/api/v0/admin")
@router.get("/.env")
@router.get("/wp-admin")
async def honeypot_trap(request: Request):
    hp.warning("HONEYPOT_HIT", extra={
        "ip": request.client.host,
        "path": request.url.path,
        "ua": request.headers.get("user-agent", ""),
        "method": request.method,
    })
    return {"detail": "Not Found"}
```

### Incident response runbook

**IR-001: JWT compromise**

1. CONTAIN — Revoca family refresh: `Redis DEL family:<id>`
2. IDENTIFY — Grep jti in Loki ultima ora
3. ERADICATE — Ruota chiave ES256, ri-emetti tutti i token
4. RECOVER — Notifica utente via canale out-of-band
5. LESSONS — Aggiorna fail2ban + soglie rate limit

**IR-002: Container escape**

1. ISOLATE — `docker stop` + snapshot volume
2. FORENSIC — Core dump + auditd export
3. REBUILD — Da zero, nuovo base image verificato
4. HARDEN — Aggiorna seccomp profile, blocklist syscall

## 7. GDPR compliance

### Privacy by design (Art. 25)

| Principio | Implementazione |
|---|---|
| Minimizzazione | Solo campi necessari in ChatRequest, no fingerprinting passivo |
| Limitazione finalità | Memoria per personalizzazione, **mai per training** |
| Integrità/riservatezza | AES-256-GCM Qdrant at-rest, TLS 1.3 in transit |
| Responsabilità | Tutti gli accessi loggati con user_id + timestamp |

### Right to erasure (Art. 17)

```python
@router.delete("/gdpr/users/{user_id}/data")
async def right_to_erasure(user_id: str, current=Depends(get_current_user)):
    if current.sub != user_id:
        raise HTTPException(403)
    deleted_vectors = await qdrant.delete_by_user(user_id)
    deleted_db = await db.execute(
        "DELETE FROM user_data WHERE user_id = $1 RETURNING count(*)", user_id
    )
    await token_store.revoke_all_for_user(user_id)
    audit_log.info("GDPR_ERASURE", user_id=user_id, vectors=deleted_vectors)
    return {
        "status": "erased",
        "deleted_vectors": deleted_vectors,
        "deleted_records": deleted_db,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
```

### DPIA template

| Dato | Base giuridica | Retention | Misure |
|---|---|---|---|
| Messaggi chat | Legittimo interesse | 90gg config | AES-256-GCM + TLS |
| Biometrici (HRV, CGM) | Consenso esplicito | 365gg | FHIR vault separato |
| Pattern comportamentali | Legittimo interesse | 30gg | Anonim. dopo 7gg |
| Log accesso | Obbligo NIS2 | 12 mesi | Read-only utente |

## 8. Supply chain security

### SBOM con Syft + CycloneDX

```yaml
# .github/workflows/sbom.yml
name: Generate SBOM
on: [push, release]
jobs:
  sbom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
      - run: syft dir:. -o cyclonedx-json=sbom.json
      - run: syft ghcr.io/open-jarvis/api:${{ github.sha }} -o cyclonedx-json=sbom-image.json
      - uses: actions/upload-artifact@v4
        with: { name: sbom, path: sbom*.json }
```

### SAST/DAST

```yaml
# .github/workflows/security.yml
jobs:
  semgrep:
    steps:
      - uses: returntocorp/semgrep-action@v1
        with:
          config: |
            p/python
            p/secrets
            p/owasp-top-ten
            p/fastapi
  codeql:
    steps:
      - uses: github/codeql-action/init@v3
        with: { languages: python }
      - uses: github/codeql-action/analyze@v3
  grype:
    steps:
      - uses: anchore/scan-action@v4
        with:
          image: ghcr.io/open-jarvis/api:${{ github.sha }}
          severity-cutoff: high
          fail-build: true
```

### Signed commits + SLSA Level 3

```bash
# SSH signing (raccomandato 2026)
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
```

```yaml
# Release con SLSA provenance
provenance:
  needs: [build]
  uses: slsa-framework/slsa-github-generator/.github/workflows/generator_container_slsa3.yml@v2
  with:
    image: ghcr.io/open-jarvis/api
    digest: ${{ needs.build.outputs.digest }}
  permissions:
    id-token: write
    contents: write
    actions: read
```

### Dependabot/Renovate

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:recommended", "security:openssf-scorecard"],
  "vulnerabilityAlerts": { "enabled": true, "labels": ["security"] },
  "packageRules": [
    { "matchUpdateTypes": ["patch"], "automerge": true }
  ]
}
```

## Appendice: pre-deploy checklist

### VPS

- [ ] SSH: porta cambiata, root disabilitato, key-only
- [ ] fail2ban attivo SSH + API
- [ ] ufw/nftables: solo 443, 2222, 51820
- [ ] Caddy: TLS 1.3, HSTS, CSP verificati
- [ ] AppArmor enforced
- [ ] Container distroless, nonroot, read-only
- [ ] auditd + Loki pipeline

### Network

- [ ] WireGuard AllowedIPs strict per peer
- [ ] mTLS certificati da CA interna
- [ ] Cloudflare Tunnel (no porte aperte VPS)

### Application

- [ ] Pydantic strict + extra=forbid
- [ ] JWT ES256 TTL 15 min + refresh rotation
- [ ] Rate limiting Redis-backed
- [ ] Webhook HMAC + anti-replay
- [ ] sops + age + Vault, no secret in chiaro

### CI/CD

- [ ] Semgrep + CodeQL verde
- [ ] Grype: no HIGH/CRITICAL
- [ ] SBOM generato e firmato
- [ ] Commit signed
- [ ] SLSA Level 3 provenance
- [ ] Dependabot/Renovate attivo

## Stack versioni mag 2026

| Tool | Versione | Ruolo |
|---|---|---|
| Caddy | 2.9 | Reverse proxy |
| WireGuard | kernel 6.17 built-in | VPN mesh |
| Wazuh | 4.11 | SIEM/XDR |
| Syft | 1.x | SBOM generation |
| Grype | 0.9x | Vulnerability scan |
| sops | 3.9 | Secret encryption |
| slowapi | 0.1.9 | Rate limiting |

## Riferimenti

- [OWASP Top 10:2025](https://owasp.org/Top10/2025/)
- [OAuth 2.1 RFC 9700](https://datatracker.ietf.org/doc/rfc9700/)
- [Wazuh SIEM](https://wazuh.com/)
- [Caddy 2.9 docs](https://caddyserver.com/docs/)
- [SLSA framework](https://slsa.dev/)
- [Tailscale ACL](https://tailscale.com/kb/1018/acls)
- [GDPR 2026](https://secureprivacy.ai/blog/gdpr-compliance-2026)
