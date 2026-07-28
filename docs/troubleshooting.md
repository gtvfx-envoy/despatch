# Troubleshooting

## Applications do not appear

1. Confirm that a Stack is selected and the launcher does not say **Choose a
   Stack**.
2. Select **Refresh**.
3. Confirm the bundle contains `.envoy/despatch.json`.
4. Confirm each manifest `command` exists in the active Stack.
5. Check whether another manifest suppresses the bundle or application.
6. Check `platforms`, global group IDs, JSON syntax, and the Despatch log.

Run Envoy's diagnosis command to inspect Stack and bundle resolution:

```powershell
envoy --diagnose
```

## A Stack cannot be selected

Common causes include:

- The filename does not end in the exact `.estack` extension.
- YAML syntax or field names are invalid.
- An environment variable in a bundle path is undefined.
- A bundle path does not exist or is not a valid Envoy bundle.
- Two entries resolve to the same bundle path.
- A named Stack's document name does not match its registry slot.

Despatch restores the previous selection after an unsuccessful switch.

## The wrong Stack is active

The Stack selector uses the Stack saved in Envoy user configuration. Automatic
resolution additionally honors `ENVOY_STACK` and `ENVOY_STACK_CONTEXT` through
Envoy discovery. Inspect the current shell and process environment, then use
`envoy --diagnose` to see the resolved source.

## An application fails to start

- Right-click it and choose **Copy Envoy command**, then run that command in a
  terminal to see Envoy output.
- Confirm the command executable is available in the Envoy-resolved `PATH`.
- Run `envoy --diagnose COMMAND` for the command shown in the manifest.
- Enable `--log-level DEBUG` and a `--log-directory` for Despatch diagnostics.

## The global shortcut cannot be enabled

The shortcut must contain a modifier and supported key. Another application
may already own it. Try a different combination such as `Ctrl+Shift+D`.
Global shortcuts are currently supported only on Windows.

## Start at sign in fails

Windows startup integration locates `envoy` or `en` on `PATH`. Confirm it is
available from a normal PowerShell session. The standalone executable is still
launched through Envoy so it receives the expected runtime configuration.

## Documentation does not open

The packaged executable starts a loopback-only static server and asks the
system browser to open it. Verify that local firewall or browser policy allows
`127.0.0.1` connections and that a default browser is configured.

In a source checkout, build the site with:

```powershell
envoy python -m properdocs build --clean
```

Without a local build, source execution opens the published GitHub Pages site.
