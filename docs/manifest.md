# Despatch manifest reference

An Envoy bundle exposes applications to Despatch through
`.envoy/despatch.json`.

```json
{
  "schemaVersion": 1,
  "groups": [
    {
      "id": "creative",
      "name": "Creative",
      "order": 10
    }
  ],
  "applications": [
    {
      "id": "krita",
      "name": "Krita",
      "command": "krita",
      "args": [],
      "description": "Digital painting application",
      "icon": "krita.svg",
      "group": "creative",
      "keywords": ["paint", "image"],
      "platforms": ["windows"],
      "inTerminal": false
    }
  ]
}
```

## Top-level fields

- `schemaVersion` is required and must currently be `1`.
- `groups` is optional. It contains display sections local to the bundle.
- `applications` is required. Only entries in this array appear in Despatch.

## Groups

- `id` is a required non-empty identifier unique within the manifest.
- `name` is the required display label.
- `order` is optional and defaults to the group's array position. Lower values
  appear first.

## Applications

- `id`, `name`, and `command` are required non-empty strings.
- `id` must be unique within the manifest. Despatch combines the bundle ID and
  application ID to form a globally stable identity.
- `command` must exist somewhere in the active Envoy Stack.
- `args` and `keywords` are optional arrays of strings.
- `description` is optional display text.
- `group` optionally refers to a group declared by the same manifest.
- `icon` is optional. Its value is a filename or relative path below the
  bundle's repo-level `resources/icons` directory. For example, `krita.svg`
  resolves to `resources/icons/krita.svg`, while `creative/krita.svg` resolves
  to `resources/icons/creative/krita.svg`. Absolute paths and paths escaping
  `resources/icons` are rejected.
- `platforms` optionally limits the entry to `windows`, `macos`, or `linux`.
- `inTerminal` optionally launches the command in a new console and defaults to
  `false`.

Malformed manifests and entries do not prevent Despatch from starting. Valid
entries remain available, while precise diagnostics are written to the log and
summarized in the main window.
