# Global Install with uv

This guide covers installing the `exa` CLI globally with [uv](https://docs.astral.sh/uv/) so you can run commands in
any shell without activating a virtual environment.

## Prerequisites

- `uv` 0.4.0 or newer on your `PATH`.
- A local clone of `exa-direct`.
- (Optional) Environment variables such as `EXA_API_KEY` exported or stored in `.env`.

### Install uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify the installation and restart your shell if the binary cannot be found immediately:

```bash
uv --version
```

## Development Install (editable)

Run this from `/home/bjorn/repos/exa-direct` to expose the CLI globally while reflecting local code edits instantly.

```bash
uv tool install --editable .
```

`uv` creates an isolated tool environment and drops a shim (typically under `~/.local/bin`).
If the shim directory is not already on your `PATH`, run `uv tool update-shell` and reopen the terminal session.

```bash
uv tool update-shell
```

## Stable Snapshot Install (wheel)

When you need a reproducible snapshot (e.g., CI artifacts or a shared build), install from the
generated wheel instead of editable sources.

```bash
uv build
uv tool install dist/exa_direct-*.whl
```

To target a specific Python runtime, append `--python <version>` (for example, `--python 3.11`).

## Verification

```bash
uv tool list          # confirm the tool is registered
which exa             # or: where exa (Windows CMD/PowerShell)
exa --version
```

`uv tool dir` prints the directory containing the shimmed executables if you need to inspect it directly.

## Maintenance Commands

- **Reinstall after changes (editable flow):**

  ```bash
  uv tool install --reinstall --editable .
  ```

- **Upgrade a published build (wheel flow):**

  ```bash
  uv build
  uv tool install --reinstall dist/exa_direct-*.whl
  ```

- **Uninstall:**

  ```bash
  uv tool uninstall exa
  ```

- **Self-update uv (optional but recommended):**

  ```bash
  uv self update
  ```

## Troubleshooting

- **`exa` not found:** Ensure the shim directory is on `PATH` (`uv tool update-shell` prints the update snippet).
- **Old executable still runs:** Re-run the appropriate `uv tool install --reinstall ...` command.
- **Multiple uv-installed tools colliding on names:**
  - Use `uv tool uninstall <name>` to remove the conflicting installation before reinstalling.

For additional background on the tool workflow, refer to the official documentation: <https://docs.astral.sh/uv/guides/tools/>.
