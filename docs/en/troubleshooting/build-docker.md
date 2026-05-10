---
title: "Build & Docker problems · Open-Jarvis"
description: "Common errors during Open-Jarvis container build (Docker, pip wheel, Python, Tauri, Capacitor) and verified fixes."
keywords: "open-jarvis docker build error, pip wheel readme, hatchling, build fix"
---

# Common problems · Build & Docker

## `Readme file does not exist: README.md`

```text
=> ERROR [builder 6/6] RUN pip install --upgrade pip && pip wheel --wheel-dir /wheels .
…
OSError: Readme file does not exist: README.md
```

**Symptom.** `docker build` (or `docker compose build`) stops in the
builder second stage. The key message is `Readme file does not exist`.

**Cause.** `pyproject.toml` declares `readme = "README.md"`. Hatchling
**requires** the file to exist in the build context. The Dockerfile
copied only Python files + `pyproject.toml`, leaving `README.md` out.
Same error if `.dockerignore` excludes the README.

**Fix.**

1. Add `README.md` to the builder's COPY:

   ```diff
   -COPY pyproject.toml ./
   +COPY pyproject.toml README.md ./
    COPY jarvis_server ./jarvis_server
   ```

2. Verify `.dockerignore`:

   ```bash
   grep -E '^README' server/.dockerignore && echo "PROBLEM"
   ```

3. Rebuild:

   ```bash
   docker compose build --no-cache server
   ```

**Prevention.** General rule: **if `pyproject.toml` references a file,
that file must be in the build context**.

## `pip wheel` very slow on the first `docker build`

**Fix.** Enable BuildKit cache mount:

```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && pip wheel --wheel-dir /wheels .
```

## `permission denied: ./scripts/something.sh`

**Cause.** Script doesn't have the exec bit (Git on Windows ignores
POSIX permissions).

**Fix.**

```bash
git update-index --chmod=+x scripts/x.sh
git add scripts/x.sh && git commit -m "chore: mark x.sh executable"
```

## `port is already allocated` (8080, 5432, 6379, 6333)

**Symptom.** `docker compose up` fails with `Bind for 0.0.0.0:8080
failed: port is already allocated`.

**Cause.** A previous server instance is still alive, or a non-Docker
process is listening.

**Fix.** Override host ports in `.env`:

```bash
JARVIS_HOST_PORT=8090
POSTGRES_HOST_PORT=15432
REDIS_HOST_PORT=16379
QDRANT_HOST_PORT=16333
QDRANT_GRPC_HOST_PORT=16334
```

After editing `.env`:

```bash
docker compose down
docker compose up -d
docker compose ps
curl http://localhost:8090/health
```

To find who holds a port:

```bash
ss -tlnp | grep -E '8080|5432|6379|6333'    # Linux
lsof -iTCP -sTCP:LISTEN | grep 8080         # macOS / BSD
Get-NetTCPConnection -State Listen -LocalPort 8080  # PowerShell
```

!!! warning "Internal container ports never change"
    Only the **host** ports (left side of `HOST:CONTAINER`) move.
    `JARVIS_DATABASE_URL` keeps pointing at `postgres:5432` (service
    name), not `localhost:15432`.

## `no space left on device`

```bash
docker system df
docker system prune -af
docker volume prune  # WARNING: drops unreferenced volumes
```

Cron prevention:

```cron
0 3 * * 0 /usr/bin/docker system prune -af --filter "until=168h"
```

## Build fails only on Apple Silicon (`linux/arm64`)

**Cause.** A wheel doesn't ship arm64 bin for the Python version.

**Workaround.** Force amd64 with emulation:

```bash
docker buildx build --platform linux/amd64 -t jarvis-server:dev .
```

**Real fix.** Bump dependency versions; arm64 wheels usually exist.

## Image size too large

```bash
docker history jarvis-server:dev --no-trunc | head -20
```

Make sure the multi-stage runtime image doesn't include
`build-essential`.

## `failed to solve: cannot resolve image`

GHCR-published images are M1.7. For now compile locally with
`docker compose build`.

## See also

- [Server upgrade](../user-manual/updates.md#1-update-the-server)
- [Server VPS install](../user-manual/install/server.md)
- [Glossary error codes](index.md#error-code-glossary)
