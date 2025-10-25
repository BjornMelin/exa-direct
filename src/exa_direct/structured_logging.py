"""Application logging configuration using structlog."""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache
from typing import Any

import structlog

__all__ = ["bind", "configure", "get_logger", "redact_payload"]

_SENSITIVE_KEYS = {
    "api_key",
    "authorization",
    "x-api-key",
    "password",
    "token",
    "secret",
}
_MAX_VALUE_LENGTH = 2048


def _shared_processors() -> list[structlog.types.Processor]:
    """Return the shared processors for structlog."""
    return [
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]


def configure() -> None:
    """Configure structlog using console or JSON renderers based on environment."""
    formatter = os.getenv("EXA_DIRECT_LOG_FORMAT", "json").lower()
    if formatter not in {"json", "console"}:
        formatter = "json"

    # Create the processors list.
    processors = _shared_processors()
    if formatter == "console":
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer())

    # Configure structlog.
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    _load_redact_setting.cache_clear()
    _load_redact_setting()


@lru_cache(maxsize=1)
def _load_redact_setting() -> bool:
    return os.getenv("EXA_DIRECT_LOG_REDACT", "1").lower() not in {"0", "false", "no"}


def _redact_value(key: str | None, value: Any) -> Any:
    if key and key.lower() in _SENSITIVE_KEYS:
        return "***"
    if isinstance(value, str) and len(value) > _MAX_VALUE_LENGTH:
        return value[:_MAX_VALUE_LENGTH] + "…"
    if isinstance(value, dict):
        return {k: _redact_value(k, v) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact_value(None, item) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact_value(None, item) for item in value)
    return value


def redact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a redacted copy of the payload when redaction is enabled."""
    if not _load_redact_setting():
        return payload
    return {key: _redact_value(key, value) for key, value in payload.items()}


@contextmanager
def bind(**kwargs: str) -> Iterator[None]:
    """Bind context variables for the duration of the block."""
    # Bind the context variables.
    bound_keys = {}
    for key, value in kwargs.items():
        if value is None:
            continue
        # Bind the context variable.
        structlog.contextvars.bind_contextvars(**{key: value})
        bound_keys[key] = value
    try:
        yield
    finally:
        # Unbind the context variables.
        if bound_keys:
            structlog.contextvars.unbind_contextvars(*bound_keys.keys())


def get_logger(name: str = "exa_direct") -> structlog.BoundLogger:
    """Return a structlog logger bound to the given name."""
    return structlog.get_logger(name)
