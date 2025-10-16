# Contributing

## Development Environment

```bash
python -m venv .venv && . .venv/bin/activate
pip install -U pip
pip install -e .
```

## Quality Gates

- `uv run ruff format && uv run ruff check . --fix`
- `uv run pyright`
- `uv run pylint --fail-under=9.5 src/exa_direct tests`
- `uv run python -m pytest -q`

## Code Style

- Python 3.10+; src/ layout.
- Google-style docstrings on public functions and classes.
- JSON to stdout; avoid side-effect printing from client layer.

## Tests

- Place unit tests in `tests/`.
- Mock network calls; do not hit real endpoints.

## Adding Commands

- Add a subparser in `src/exa_direct/cli.py`.
- Implement corresponding method in `src/exa_direct/client.py`.
- Add CLI tests that assert service method calls and output shape.

## Reporting Issues

- Provide the CLI command, output, and environment details (Python version, OS, EXA_API_KEY presence).
