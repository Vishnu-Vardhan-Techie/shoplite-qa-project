"""Shared fixtures: starts the ShopLite app on a free port for the whole test session."""
import socket
import threading

import pytest
from werkzeug.serving import make_server

from app.app import app


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def base_url():
    """Overrides pytest-playwright's base_url so page.goto('/login') works."""
    port = _free_port()
    server = make_server("127.0.0.1", port, app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()
