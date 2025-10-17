"""Minimal stub package for `exa_py` used during tests.

This prevents import errors without requiring the real dependency.
The `Exa` type exposes attributes referenced by the client code but
methods raise NotImplementedError if actually invoked by tests.
"""

from __future__ import annotations

from typing import Any


class _Research:
    def create(self, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover
        """Placeholder for the SDK create method; not exercised in tests."""
        raise NotImplementedError

    def get(self, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover
        """Placeholder for the SDK get method; not exercised in tests."""
        raise NotImplementedError

    def list(self, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover
        """Placeholder for the SDK list method; not exercised in tests."""
        raise NotImplementedError

    def poll_until_finished(self, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover
        """Placeholder for the SDK poll_until_finished method."""
        raise NotImplementedError


class Exa:
    """Stub Exa client with a `research` namespace attribute."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover
        """Initialize stub with a research namespace."""
        self.research = _Research()

    # Search/contents/answer entry points (not used by current tests)
    def search(self, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover
        """Placeholder for search; not invoked by current tests."""
        raise NotImplementedError

    def get_contents(self, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover
        """Placeholder for get_contents; not invoked by current tests."""
        raise NotImplementedError

    def search_and_contents(self, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover
        """Placeholder for search_and_contents; not invoked by tests."""
        raise NotImplementedError

    def find_similar(self, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover
        """Placeholder for find_similar; not invoked by current tests."""
        raise NotImplementedError

    def find_similar_and_contents(
        self, *args: Any, **kwargs: Any
    ) -> Any:  # pragma: no cover
        """Placeholder for find_similar_and_contents; not invoked by tests."""
        raise NotImplementedError

    def answer(self, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover
        """Placeholder for answer; not invoked by current tests."""
        raise NotImplementedError

    def stream_answer(self, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover
        """Placeholder for stream_answer; not invoked by current tests."""
        raise NotImplementedError
