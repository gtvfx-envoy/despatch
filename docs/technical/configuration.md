# Configuration

Despatch reads two separate user configuration stores: its own launcher
preferences and Envoy's shared runtime selection.

## Despatch settings

Default location:

| Platform | Path |
|---|---|
| Windows | `%APPDATA%\Despatch\settings.json` |
| macOS/Linux fallback | `~/.config/despatch/settings.json` |

Use `despatch --settings PATH` for an alternate file. This is useful for tests
or isolated launcher profiles.

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

The launcher reads and writes Envoy's `stack` user setting. Its default file is
`%APPDATA%\envoy\user_config.json` on Windows and
`~/.config/envoy/user_config.json` on macOS/Linux. `ENVOY_USER_CONFIG` can
override that location.

```json
{
  "stack": "studio"
}
```

## Environment variables

| Variable | Purpose in Despatch |
|---|---|
| `ENVOY_STACK` | Highest-priority named Stack or `.estack` path during Automatic resolution |
| `ENVOY_STACK_CONTEXT` | Colon-separated named Stack context used during Automatic resolution |
| `ENVOY_STACK_ROOTS` | Platform-separated named Stack registry roots |
| `ENVOY_BNDL_ROOTS` | Platform-separated roots used by Automatic discovery |
| `ENVOY_USER_CONFIG` | Alternate Envoy user configuration path |
| `ENVOY_BUNDLE_CACHE` | Override Envoy's local production Bundle cache |
| `ENVOY_DISABLE_DISCOVERY_CACHE=1` | Disable Envoy's bundle discovery cache |
| `ENVOY_DEV_MODE=1` | Default an unconfigured Despatch session to Automatic resolution |

Windows path lists use semicolons; Unix path lists use colons. Stack contexts
always use colons.

The Stack selector directly reads and writes Envoy's shared `stack` setting.
When Despatch is in Automatic mode, `discoverBundlesAuto()` applies
`ENVOY_STACK`, then the user setting, then `ENVOY_STACK_CONTEXT`, before
falling back to `ENVOY_BNDL_ROOTS`.

For the full Envoy environment and precedence reference, see
[Envoy user configuration](https://gtvfx-contrib.github.io/gt-envoy/user-config/)
and [bundle discovery](https://gtvfx-contrib.github.io/gt-envoy/bundle-discovery/).

## Logging

`--log-level` accepts `DEBUG`, `INFO`, `WARNING`, or `ERROR`. Supply
`--log-directory DIR` to write `despatch.log` with rotation at 2 MiB and three
backups. Console logging uses the same threshold.
