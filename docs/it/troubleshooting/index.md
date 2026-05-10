---
title: "Problemi comuni e come risolverli · Open-Jarvis"
description: "Knowledge base curata di errori frequenti, sintomi e soluzioni step-by-step per server, agent, build, deploy e runtime di Open-Jarvis."
keywords: "open-jarvis troubleshooting, problemi comuni, errori, FAQ tecnica, debug, fix"
---

# Problemi comuni e come risolverli

Questa è la knowledge base **operativa** di Open-Jarvis: una raccolta
curata di errori che la community ha già visto, con causa e fix
verificato.

!!! tip "Convenzioni di lettura"
    Ogni voce segue lo schema **Sintomo → Causa → Fix → Prevenzione**.
    Quando il problema può lasciare lo stato del sistema in un punto
    intermedio, troverai una checkbox `Verifica` con il comando di
    diagnostica.

## Indice tematico

- [Build & Docker](build-docker.md)
- [Avvio server runtime](server-runtime.md)
- [Database / Alembic](database.md) (in arrivo)
- [Identity, JWT, MFA](identity.md) (in arrivo)
- [Memory & vector store](memory.md) (in arrivo)
- [LLM router & adapters](llm.md) (in arrivo)
- [Chat (SSE / WebSocket)](chat.md) (in arrivo)
- [Pairing dispositivi](pairing.md) (in arrivo)

## Come segnalare un nuovo problema

Se il tuo errore non è coperto:

1. Cerca con il box di ricerca della docs (in alto a destra).
2. Cerca tra le issue: <https://github.com/fedcal/open-jarvis/issues>.
3. Se davvero non c'è nulla, [apri una nuova issue](https://github.com/fedcal/open-jarvis/issues/new/choose)
   con il template `Bug report`. Include:
    - **Versione** del server (`curl /health | jq .version`)
    - **Comando esatto** che hai eseguito
    - **Output completo** dell'errore (stdout + stderr)
    - **Sistema**: distro Linux + kernel, Docker version, hostname
    - **Cosa hai già provato**

Le PR che aggiungono nuove voci a questa knowledge base sono
particolarmente benvenute. Vedi [Contribuire](../contributing/index.md).

## Diagnostica rapida del sistema

Comando one-shot per raccogliere lo stato di un'installazione:

```bash
./scripts/diagnose.sh > diagnose-$(date +%F).txt
```

Lo script raccoglie (sempre **redactando segreti**):

- versioni: server, Docker, Compose, Postgres, Qdrant
- esito di `/health`
- ultimi 200 righe di log per ogni container
- count tabelle DB (no contenuti)
- spazio disco e RAM disponibili

Allega il file `diagnose-*.txt` all'issue: il triage diventa molto
più veloce.

## Glossario degli error code

| HTTP | Significato standard Open-Jarvis |
|------|----------------------------------|
| 401  | Token assente / invalido / scaduto |
| 403  | Token valido ma scope insufficiente o `user_id` mismatch |
| 404  | Risorsa non esistente per il chiamante |
| 409  | Conflitto: email duplicata, pairing già usato |
| 422  | Validazione Pydantic fallita |
| 5xx  | Bug server: apri issue con il `request_id` dei log |
