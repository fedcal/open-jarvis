"""ASGI entrypoint for production servers (uvicorn, gunicorn).

Run with::

    uvicorn jarvis_server.api.main:app --host 0.0.0.0 --port 8080
"""

from __future__ import annotations

from jarvis_server.api.app import create_app

app = create_app()

__all__ = ["app"]
