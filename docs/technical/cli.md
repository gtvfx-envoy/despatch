# CLI Reference

```text
despatch [--popup] [--settings PATH] [--log-directory DIR]
         [--log-level LEVEL] [--docs] [--version]
```

| Option | Description |
|---|---|
| `--popup` | Show the launcher immediately instead of starting only in the tray |
| `--settings PATH` | Use an alternate Despatch settings JSON file |
| `--log-directory DIR` | Write rotating logs to this directory |
| `--log-level LEVEL` | Set `DEBUG`, `INFO`, `WARNING`, or `ERROR`; default is `ERROR` |
| `--docs` | Open this documentation and exit |
| `--version` | Print the Despatch version and exit |

Examples:

```powershell
# Start in the notification area
despatch

# Show the launcher immediately with diagnostic logging
despatch --popup --log-level DEBUG --log-directory "$env:TEMP/despatch-logs"

# Open the packaged offline documentation
despatch --docs
```

Internal worker and documentation-server switches are intentionally hidden and
are not stable public interfaces.
