"""Tests for retry/backoff behavior in `ExaService.context`.

These tests simulate the HTTP client used by :meth:`ExaService.context` to
exercise retry behaviour for request errors, HTTP 5xx responses, exhausted
backoff attempts, and non-retriable errors.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, cast

import pytest

from exa_direct import client as client_module


def _mk_http_status_error(response: Any) -> Exception:
    """Construct an `httpx.HTTPStatusError` for the active `httpx` module."""
    httpx = client_module.httpx
    kwargs: dict[str, Any] = {"response": response}
    if hasattr(httpx, "Request"):
        request = httpx.Request("GET", "https://example.invalid")
        kwargs["request"] = request
    return httpx.HTTPStatusError("server error", **kwargs)  # type: ignore[call-arg]


@dataclass
class _Response:
    """Simple `httpx.Response` stand-in used by the HTTP stub."""

    payload: dict[str, Any]
    status_code: int = 200

    def raise_for_status(self) -> None:
        """Raise an HTTPStatusError for 4xx/5xx responses."""
        if self.status_code >= 400:
            raise _mk_http_status_error(self)

    def json(self) -> dict[str, Any]:
        """Return the stored payload."""
        return self.payload


class _HttpStub:
    """HTTP client stub that records calls and delegates via a side effect."""

    def __init__(
        self,
        side_effect: Callable[[int, str, dict[str, Any]], Any],
    ) -> None:
        """Store the side effect callable for later invocations."""
        self._side_effect = side_effect
        self.calls: list[dict[str, Any]] = []

    def post(self, url: str, json: dict[str, Any]) -> Any:
        """Record the call and invoke the configured side effect."""
        index = len(self.calls)
        self.calls.append({"url": url, "json": json})
        return self._side_effect(index, url, json)

    def close(self) -> None:  # pragma: no cover - interface compat only
        """Provide the same surface area as `httpx.Client.close`."""
        return


@pytest.fixture(name="sleep_delays")
def _sleep_delays(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Patch `time.sleep` to capture backoff delays without slowing tests."""
    calls: list[float] = []

    def _fake_sleep(seconds: float) -> None:
        calls.append(seconds)

    monkeypatch.setattr(client_module.time, "sleep", _fake_sleep)
    return calls


def _make_service(
    side_effect: Callable[[int, str, dict[str, Any]], Any],
) -> tuple[client_module.ExaService, _HttpStub]:
    """Make a service with a side effect and an HTTP stub."""
    http_stub = _HttpStub(side_effect)
    service = client_module.ExaService(
        "api-key",
        http=cast(client_module.httpx.Client, http_stub),
    )
    return service, http_stub


@pytest.mark.parametrize(
    ("failure_sequence", "expected_sleeps"),
    [
        (["request", "request"], [0.1, 0.2]),
        (["server", "server"], [0.1, 0.2]),
    ],
)
def test_context_retries_then_succeeds(
    failure_sequence: list[str],
    expected_sleeps: list[float],
    sleep_delays: list[float],
) -> None:
    """Context should retry transient failures and return JSON on success."""
    httpx = client_module.httpx

    def _side_effect(index: int, url: str, payload: dict[str, Any]) -> Any:
        assert url.endswith("/context")
        assert payload == {"query": "pandas", "tokensNum": 128}
        if index < len(failure_sequence):
            failure = failure_sequence[index]
            if failure == "request":
                raise httpx.RequestError("boom")
            if failure == "server":
                return _Response({}, status_code=500)
        return _Response({"ok": True})

    svc, http_stub = _make_service(_side_effect)
    result = svc.context(query="pandas", tokens_num=128)

    assert result == {"ok": True}
    assert len(http_stub.calls) == len(failure_sequence) + 1
    assert sleep_delays == expected_sleeps


def test_context_eventually_succeeds_after_final_attempt(
    sleep_delays: list[float],
) -> None:
    """All backoff attempts fail, success occurs on the final forced attempt."""
    httpx = client_module.httpx

    def _side_effect(index: int, url: str, payload: dict[str, Any]) -> Any:
        assert url.endswith("/context")
        assert payload == {"query": "numpy"}
        if index < 3:
            raise httpx.RequestError(f"network-{index}")
        return _Response({"ok": True})

    svc, http_stub = _make_service(_side_effect)
    result = svc.context(query="numpy")

    assert result == {"ok": True}
    assert len(http_stub.calls) == 4  # 3 retries + final attempt
    assert sleep_delays == [0.1, 0.2, 0.5]


def test_context_raises_for_non_retriable_status(
    sleep_delays: list[float],
) -> None:
    """4xx responses should not be retried and should raise immediately."""

    def _side_effect(index: int, url: str, payload: dict[str, Any]) -> Any:
        del index, url, payload
        return _Response({}, status_code=429)

    svc, http_stub = _make_service(_side_effect)

    with pytest.raises(client_module.httpx.HTTPStatusError) as exc:
        svc.context(query="rate-limit")

    assert exc.value.response.status_code == 429  # type: ignore[union-attr]
    assert len(http_stub.calls) == 1
    assert sleep_delays == []


def test_context_propagates_final_failure(sleep_delays: list[float]) -> None:
    """If the final attempt fails, propagate the originating exception."""
    httpx = client_module.httpx

    def _side_effect(index: int, url: str, payload: dict[str, Any]) -> Any:
        del url, payload
        raise httpx.RequestError(f"still-down-{index}")

    svc, http_stub = _make_service(_side_effect)

    with pytest.raises(client_module.httpx.RequestError):
        svc.context(query="broken")

    assert len(http_stub.calls) == 4  # 3 retries + final attempt
    assert sleep_delays == [0.1, 0.2, 0.5]
