---
title: "Common problems & how to fix them · Open-Jarvis"
description: "Curated knowledge base of frequent errors, symptoms and step-by-step fixes for server, agents, build, deploy and runtime of Open-Jarvis."
keywords: "open-jarvis troubleshooting, common problems, errors, technical FAQ, debug, fix"
---

# Common problems & how to fix them

This is the **operational knowledge base** of Open-Jarvis: a curated
collection of errors the community has already met, with cause and
verified fix.

!!! tip "Reading conventions"
    Each entry follows **Symptom → Cause → Fix → Prevention**. When
    the problem can leave the system in a half-applied state, you'll
    find a `Verify` checkbox with the diagnostic command.

## Topical index

- [Build & Docker](build-docker.md)
- [Server runtime](server-runtime.md)
- Database / Alembic (coming)
- Identity, JWT, MFA (coming)
- Memory & vector store (coming)
- LLM router & adapters (coming)
- Chat (SSE / WebSocket) (coming)
- Device pairing (coming)

## How to report a new issue

If your error isn't covered:

1. Search this site (top-right).
2. Search issues: <https://github.com/fedcal/open-jarvis/issues>.
3. If nothing matches, [open a new issue](https://github.com/fedcal/open-jarvis/issues/new/choose)
   with the `Bug report` template. Include:
    - **Server version** (`curl /health | jq .version`)
    - **Exact command** you ran
    - **Full output** (stdout + stderr)
    - **System**: Linux distro + kernel, Docker version
    - **What you already tried**

PRs that add new entries to this KB are particularly welcome. See
[Contributing](../contributing/index.md).

## Quick system diagnostic

One-shot command to capture the state of an install:

```bash
./scripts/diagnose.sh > diagnose-$(date +%F).txt
```

The script collects (always **redacting secrets**):

- versions: server, Docker, Compose, Postgres, Qdrant
- `/health` outcome
- last 200 log lines per container
- DB table count (no contents)
- disk + RAM available

Attach `diagnose-*.txt` to the issue: triage gets way faster.

## Error code glossary

| HTTP | Open-Jarvis meaning |
|------|---------------------|
| 401  | Token missing / invalid / expired |
| 403  | Token valid but insufficient scope or `user_id` mismatch |
| 404  | Resource doesn't exist for the caller |
| 409  | Conflict: duplicate email, pairing already used |
| 422  | Pydantic validation failed |
| 5xx  | Server bug: open issue with the `request_id` from logs |
