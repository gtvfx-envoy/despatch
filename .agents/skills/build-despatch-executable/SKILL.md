---
name: build-despatch-executable
description: Build, diagnose, validate, and release Despatch's one-file Windows executable. Use when generating or testing despatch.exe; changing PyInstaller configuration, packaging dependencies, frozen-process behavior, packaged resources, or executable build scripts; or modifying the GitHub Actions executable release workflow.
---

# Build Despatch Executable

Use the repository's packaging path as the source of truth. Do not recreate the
build with ad hoc PyInstaller commands.

## Inspect the packaging contract

Read these files before changing or running the build:

- `scripts/build-executable.ps1`
- `scripts/pyinstaller_entry.py`
- `pyinstaller.spec`
- `pyproject.toml`
- `.github/workflows/build-release.yml`
- `py/despatch/__main__.py`
- `py/despatch/_envoy_gateway.py`

Preserve unrelated working-tree changes.

## Preserve frozen-runtime behavior

- Keep `scripts/pyinstaller_entry.py` as the PyInstaller entry point. Never
  execute `despatch/__main__.py` directly from the spec; its relative imports
  require package context.
- Treat `sys.executable` as `despatch.exe` when `sys.frozen` is true. Route
  isolated child launches through the hidden `--launch-worker` mode rather
  than `python -m despatch._launch_worker`.
- Preserve the `resources` to `despatch/resources` data mapping and verify that
  the packaged product icon resolves.
- Produce a windowed final executable. Use the build script's `-Console` switch
  only to expose diagnostic tracebacks, then rebuild without it.
- Keep Envoy and its native extension in the hidden imports.

## Keep dependency pins coherent

Read current values instead of copying versions from this skill. When upgrading:

- Synchronize the PyInstaller pin in `pyproject.toml` and
  `scripts/build-executable.ps1`.
- Check Python, PySide6, and Qt.py compatibility together.
- Verify that the Envoy release pinned by the workflow contains exactly one
  compatible Windows ABI3 wheel.
- Update Envoy API preflight checks, gateway tests, and hidden imports when the
  packaged API surface changes.

Do not encode workstation-specific repository, cache, drive-letter, or artifact
share paths in committed files. Use repository configuration and script
parameters to discover or override them.

## Build and validate

1. Run the Python tests and full Ruff lint and format checks through Envoy.
2. Run `./scripts/build-executable.ps1` from PowerShell. Use
   `-PythonExecutable` only with an explicitly prepared Python 3.11 environment.
3. Confirm that `dist/despatch.exe` exists and is non-empty.
4. Run `--version` against the final windowed executable and require exit code
   zero.
5. Exercise the hidden frozen worker route with a temporary request and confirm
   that it writes a structured result. An intentionally invalid request should
   return exit code 2 with an `Invalid launch request` result.
6. Review PyInstaller's warning file for missing required modules. Ignore only
   understood platform-specific or optional imports.
7. When changing release automation, retain both manual workflow artifacts and
   tag-triggered GitHub Release uploads.

Do not describe PyInstaller as tested merely because analysis completed or an
EXE was written. Validate the final windowed artifact itself.

## Report the result

Report:

- The executable's absolute path, byte size, and SHA-256 hash.
- Whether the artifact remains on disk and whether Git ignores it.
- Test, lint, format, build, and frozen smoke-test outcomes.
- Any unresolved PyInstaller warnings or release dependency assumptions.
