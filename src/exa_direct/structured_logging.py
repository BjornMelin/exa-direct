"""Application logging configuration using structlog."""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager

import structlog

_CONTEXT_VARS = {
    "workflow_id": structlog.contextvars.bind_contextvars,
    "request_id": structlog.contextvars.bind_contextvars,
    "agent_run_id": structlog.contextvars.bind_contextvars,
}


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
