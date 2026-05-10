---
title: "Server boot & runtime issues · Open-Jarvis"
description: "Errors that happen on the first server start (Alembic migrations, JWT signature, env vars, port collision) and verified step-by-step fixes."
keywords: "open-jarvis server crash, alembic upgrade, jwt signature failed, asyncpg, env_prefix, port already in use"
---

# Common problems · Server boot

## `relation "users" does not exist` on the first `docker compose up`

```text
sqlalchemy.exc.ProgrammingError: (psycopg.errors.UndefinedTable)
relation "users" does not exist
```

**Symptom.** Stack starts, `/health` answers, but the first
`/api/v1/auth/register` returns `500 Internal Server Error`.

**Cause.** Postgres exists but is **empty** — Alembic migrations were
never applied. By default the `server` container runs:

```sh
alembic upgrade head && exec uvicorn jarvis_server.api.main:app …
```

If you see this error, you may be using an older image, or a
`docker-compose.override.yml` that replaced the `command:`.

**Fix.**

```bash
docker compose run --rm server alembic upgrade head
docker compose exec postgres psql -U jarvis -d jarvis -c "\dt"
```

You should see `users`, `devices`, `sessions`, `mfa_credentials`,
`audit_events`, `memory_items`, `pairing_codes`, `alembic_version`.

**Prevention.** Don't strip `command:` from the compose. Override
extends, doesn't replace.

## `Signature verification failed` with `--workers 2` or more

**Symptom.** Login OK, then 401 on the next call. Sometimes works,
sometimes doesn't.

**Cause.** In dev (no `JARVIS_JWT_PRIVATE_KEY_PEM`) the server
**generates an ephemeral ES256 keypair per process** at boot. With
`--workers >1` each worker has its own keypair: a token signed by
worker A is not verifiable by worker B.

**Dev fix.** `docker-compose.yml` is already set to `--workers 1`:

```yaml
server:
  command: >
    sh -c "alembic upgrade head &&
           exec uvicorn jarvis_server.api.main:app
                --host 0.0.0.0 --port 8080
                --workers 1 --proxy-headers"
```

**Production fix.** Set a stable keypair:

```bash
openssl ecparam -name prime256v1 -genkey -noout -out jwt-private.pem
openssl ec -in jwt-private.pem -pubout -out jwt-public.pem

export JARVIS_JWT_PRIVATE_KEY_PEM="$(cat jwt-private.pem)"
export JARVIS_JWT_PUBLIC_KEY_PEM="$(cat jwt-public.pem)"
```

Store `jwt-private.pem` in a secret manager (Vault, AWS SM). You can
then bump workers to 4+ safely.

**Prevention.** `assert_production_safe()` refuses production startup
without keys — that's why.

## `ModuleNotFoundError: No module named 'asyncpg'`

**Cause.** The URL uses `postgresql+asyncpg://...` but the server
ships **psycopg3** (`psycopg[binary,pool]`).

**Fix.**

```diff
- JARVIS_DATABASE_URL=postgresql+asyncpg://jarvis:jarvis@localhost:5432/jarvis
+ JARVIS_DATABASE_URL=postgresql+psycopg://jarvis:jarvis@localhost:5432/jarvis
```

`postgresql+psycopg` enables psycopg3 async mode (introduced in v3.0).
Performance and feature parity with asyncpg are great for Open-Jarvis.

## `port is already allocated`

See [Build & Docker → port collision](build-docker.md#port-is-already-allocated-8080-5432-6379-6333).

## `make server-dev` doesn't read `.env`

**Symptom.** You set `JARVIS_DATABASE_URL=...` in repo-root `.env`
but server-dev uses the default (`sqlite+aiosqlite:///./jarvis-dev.db`).

**Cause.** `make server-dev` does `cd server && uv run uvicorn ...`:
pydantic-settings looks for `.env` in the cwd, i.e. `server/.env`,
which doesn't exist.

**Fix.** The Makefile already passes `--env-file ../.env`:

```bash
cd server && uv run uvicorn jarvis_server.api.main:app \
    --reload --host 0.0.0.0 --port 8080 --env-file ../.env
```

## `value is not a valid email address: ... reserved name`

**Cause.** RFC 6761 reserved TLDs (`.local`, `.test`, `.localhost`,
`.invalid`, `.example`, `.onion`) are rejected by the email validator.

**Fix.** Use `@example.com`, a real domain, or an internal corporate
TLD (e.g. `@home.lan`).

## Container `unhealthy` with healthcheck timeout

```bash
docker compose exec server python -c \
  "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8080/health',timeout=3).read())"
```

If the answer is OK but status is still unhealthy, wait 30-60 s.

If no answer:

```bash
docker compose logs server --tail=50
```

Look for: `Application startup failed.`, `Address already in use`,
`Connection refused` toward postgres (you tampered with `depends_on`).

## Container restarts in loop

```bash
diff <(grep '^[A-Z]' .env) <(grep '^[A-Z]' .env.example) | head -20
```

Add the missing keys, then:

```bash
docker compose up -d --force-recreate server
```

## `permission denied` on `/var/run/docker.sock`

```bash
sudo usermod -aG docker $USER
newgrp docker
docker info  # works without sudo
```

## See also

- [Build & Docker](build-docker.md)
- [Glossary error codes](index.md#error-code-glossary)
