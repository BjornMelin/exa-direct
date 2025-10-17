# Testing & Quality Gates

This project uses a lightweight, enforceable quality pipeline.

## Commands

- Format & Lint:

```bash
uv run ruff format
uv run ruff check . --fix
```

- Types:

```bash
uv run pyright
```

- Lint minimum score:

```bash
uv run pylint --fail-under=9.5 src/exa_direct tests
```

- Tests:

```bash
uv run python -m pytest -q
```

## Scope

- Unit tests validate CLI dispatch for each command and basic research/context flows.
- Streaming is validated as line output (no network calls in tests).

## Notes

- Pylint C901 is ignored for the main dispatcher to avoid over-refactoring a simple CLI.
- Keep tests hermetic; no real network calls.
