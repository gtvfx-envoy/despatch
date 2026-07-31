# Configuration

Despatch reads two separate user configuration stores: its own launcher
preferences and Envoy's shared runtime selection.

## Despatch settings

Default location:

| Platform | Path |
|---|---|
| Windows | `%USERPROFILE%\.envoy\despatch\settings.json` |
| macOS/Linux | `~/.envoy/despatch/settings.json` |

Use `despatch --settings PATH` for an alternate file. This is useful for tests
or isolated launcher profiles. Otherwise, `DESPATCH_CONFIG_ROOT` can replace
the Despatch application directory directly, so the file is stored at
`$DESPATCH_CONFIG_ROOT/settings.json`. If that variable is unset or blank,
Despatch asks Envoy for its shared config root.

```json
{
  "autostart": false,
  "favorites": ["gt:creative:krita"],
  "globalShortcut": "Ctrl+Alt+Space",
  "globalShortcutEnabled": true,
  "keepOpenAfterLaunch": false,
  "recentApplications": ["gt:creative:krita"],
  "schemaVersion": 1,
  "stackRefreshIntervalSeconds": 300,
  "theme": "dark",
  "windowGeometry": ""
}
```

Despatch writes this file atomically. Invalid or unsupported values fall back
to defaults rather than preventing startup.

`stackRefreshIntervalSeconds` must be a whole-minute value from `60` through
`3600`. It defaults to `300`. Despatch applies this interval only to explicitly
selected named and custom Stacks; Automatic resolution disables file
monitoring.

Each normal probe reads only filesystem metadata. Named Stacks first resolve
their current registry `latest` pointer, while custom Stacks inspect their
selected `.estack` path directly. Failed probes use exponential retry delays
capped at five minutes, without ever retrying faster than the configured normal
interval.

## Envoy user configuration

The launcher reads and writes Envoy's `stack` user setting through the Envoy
Python API. Its default file is `~/.envoy/user_config.json` on every supported
platform. `ENVOY_CONFIG_ROOT` replaces the shared `~/.envoy` root, so the file
becomes `$ENVOY_CONFIG_ROOT/user_config.json` and Despatch settings become
`$ENVOY_CONFIG_ROOT/despatch/settings.json` unless `DESPATCH_CONFIG_ROOT` is
also set.

```json
{
  "stack": "studio"
}
```

## Environment variables

| Variable | Purpose in Despatch |
|---|---|
| `ENVOY_CONFIG_ROOT` | Absolute directory replacing the ecosystem-wide `~/.envoy` config root |
| `DESPATCH_CONFIG_ROOT` | Absolute Despatch-specific directory containing `settings.json`; takes precedence over the shared root for Despatch settings only |
| `ENVOY_STACK` | Highest-priority named Stack or `.estack` path during Automatic resolution |
| `ENVOY_STACK_CONTEXT` | Colon-separated named Stack context used during Automatic resolution |
| `ENVOY_STACK_ROOTS` | Platform-separated named Stack registry roots |
| `ENVOY_BNDL_ROOTS` | Platform-separated roots used by Automatic discovery |
| `ENVOY_BUNDLE_CACHE` | Override Envoy's local production Bundle cache |
| `ENVOY_DISABLE_DISCOVERY_CACHE=1` | Disable Envoy's bundle discovery cache |
| `ENVOY_DEV_MODE=1` | Default an unconfigured Despatch session to Automatic resolution |

Windows path lists use semicolons; Unix path lists use colons. Stack contexts
always use colons.

For predictable behavior, config-root overrides should be absolute paths.
Explicit `--settings` takes precedence over both environment variables. Blank
override values are ignored. Neither Envoy nor Despatch migrates or falls back
to files in the previous `%APPDATA%`, XDG, or `~/.config` locations.

The Stack selector directly reads and writes Envoy's shared `stack` setting.
When Despatch is in Automatic mode, `discoverBundlesAuto()` applies
`ENVOY_STACK`, then the user setting, then `ENVOY_STACK_CONTEXT`, before
falling back to `ENVOY_BNDL_ROOTS`.

For the full Envoy environment and precedence reference, see
[Envoy user configuration](https://gtvfx-envoy.github.io/envoy/user-config/)
and [bundle discovery](https://gtvfx-envoy.github.io/envoy/bundle-discovery/).

## Logging

`--log-level` accepts `DEBUG`, `INFO`, `WARNING`, or `ERROR`. Supply
`--log-directory DIR` to write `despatch.log` with rotation at 2 MiB and three
backups. Console logging uses the same threshold.
