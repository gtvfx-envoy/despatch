# Despatch

Despatch is a Windows-first system tray launcher for applications managed by
[Envoy](https://github.com/gtvfx-contrib/gt-envoy). It discovers explicitly
declared application metadata from active Envoy bundles, presents a fast
searchable catalog, and always dispatches commands through Envoy's concatenated
environment.

## Runtime

Despatch targets the studio's Envoy-provided Python 3.11.9 environment. That
environment supplies the `Qt` compatibility shim and its selected Qt binding.
Application code imports from `Qt`; it does not import a binding directly.

Before running or developing Despatch, verify the environment:

```powershell
envoy --info python
envoy --which python
envoy python -c "import sys, Qt; print(sys.version); print(Qt.__binding__)"
```

Start the tray application with:

```powershell
envoy despatch
```

Show the main launcher immediately:

```powershell
envoy despatch --popup
```

Left-clicking the tray icon shows or raises the launcher. Right-clicking opens
a compact menu containing favorite applications, Envoy Stack switching,
refresh, settings, and quit actions. Closing the main window hides it to the
tray.

Despatch uses the Stack saved in Envoy's shared `stack` user setting. Named
Stacks and custom `.estack` files can be selected from the launcher. When no
Stack is saved, Despatch asks the user to choose one before presenting
applications. Set `ENVOY_DEV_MODE=1` to default an otherwise unconfigured
session to Automatic resolution. Automatic resolution can also be selected
manually for the current session.

## Development

All Python tooling must run through Envoy:

```powershell
envoy python -m pytest
envoy python -m ruff check .
envoy python -m build
```

Do not substitute a system `python` or `pip`; it will not contain the assembled
runtime used by Despatch.

## Application manifests

Bundles opt into the GUI by adding `.envoy/despatch.json`. Unlisted Envoy
commands remain available from the command line but are not shown in Despatch.
See [the manifest reference](docs/manifest.md) for the schema and validation
rules.

## Current milestone

The initial release covers named and custom Envoy Stacks, manifest discovery,
search, favorites, history, tray controls, application launch, terminal launch,
settings, login startup, global shortcut registration, and actionable errors.
Historical Stack browsing, feature overlays, and detailed cache
management are intentionally deferred until their Envoy APIs are stable.
