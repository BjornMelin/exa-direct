"""Shared fixtures for unit tests."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest

from exa_direct import client as client_module
from exa_direct._testing import StubService


@pytest.fixture(name="stub_service_type")
def _stub_service_type() -> type[StubService]:
    """Return the stub service type for reuse across tests."""
    return StubService


@pytest.fixture
def stub_service(stub_service_type: type[StubService]) -> StubService:
    """Provide a fresh stub service instance."""
    return stub_service_type()


@pytest.fixture(autouse=True)
def disable_http2_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Ensure httpx clients created in tests do not require HTTP/2 extras."""
    original_client = client_module.httpx.Client

    def _client(*args: Any, **kwargs: Any):
        kwargs["http2"] = False
        return original_client(*args, **kwargs)

    monkeypatch.setattr(client_module.httpx, "Client", _client)
    yield
    monkeypatch.setattr(client_module.httpx, "Client", original_client)


@pytest.fixture
def enable_openai(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Toggle OpenAI integrations during tests and clean up afterwards."""
    monkeypatch.setenv("EXA_DIRECT_ENABLE_OPENAI", "1")
    yield
    monkeypatch.delenv("EXA_DIRECT_ENABLE_OPENAI", raising=False)
