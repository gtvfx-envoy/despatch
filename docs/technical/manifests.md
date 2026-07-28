# Bundle Manifests

An Envoy bundle opts applications into Despatch by adding
`.envoy/despatch.json`. Envoy commands not listed in this manifest remain
available from the command line but do not appear in the launcher.

## Example

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
      "args": ["--new-instance"],
      "description": "Digital painting and illustration",
      "icon": "creative/krita.svg",
      "group": "creative",
      "keywords": ["paint", "image", "concept"],
      "platforms": ["windows", "linux"],
      "inTerminal": false
    }
  ]
}
```

## Top-level fields

| Field | Required | Description |
|---|---|---|
| `schemaVersion` | Yes | Must currently be `1` |
| `groups` | No | Display sections local to this bundle |
| `applications` | Yes | Applications exposed to Despatch |

## Groups

| Field | Required | Description |
|---|---|---|
| `id` | Yes | Non-empty identifier unique within the manifest |
| `name` | Yes | Display label |
| `order` | No | Numeric sort order; defaults to array position |

Groups from different bundles remain distinct even when they share an `id`.

## Applications

| Field | Required | Description |
|---|---|---|
| `id` | Yes | Non-empty identifier unique within the manifest |
| `name` | Yes | User-facing display name |
| `command` | Yes | Command available somewhere in the active Envoy Stack |
| `args` | No | Array of command arguments |
| `description` | No | Secondary text shown by the launcher |
| `icon` | No | Relative file below the bundle's `resources/icons` directory |
| `group` | No | Group `id` declared by this same manifest |
| `keywords` | No | Additional search terms |
| `platforms` | No | Any of `windows`, `macos`, or `linux` |
| `inTerminal` | No | Launch in a new console; defaults to `false` |

Application identity combines the bundle ID and application ID. This makes
favorites and history stable across refreshes while avoiding collisions
between bundles.

## Icons and path safety

`icon: krita.svg` resolves to `resources/icons/krita.svg` at the bundle root;
`icon: creative/krita.svg` resolves below that directory. Absolute paths,
missing files, and paths escaping `resources/icons` are rejected.

SVG and common raster formats supported by the active Qt binding can be used.
Provide a square icon that remains legible at 34 × 34 pixels.

## Validation and diagnostics

Malformed manifests do not prevent Despatch from starting. Valid entries from
the same or other bundles remain available. Despatch writes precise diagnostics
to its log and summarizes the issue count in the launcher.

An application is omitted when its command is unavailable, its platform does
not match, its group is undeclared, or required fields are invalid.

Bundle command and environment definitions remain Envoy configuration. See
[Envoy Core Concepts](https://gtvfx-contrib.github.io/gt-envoy/concepts/).
