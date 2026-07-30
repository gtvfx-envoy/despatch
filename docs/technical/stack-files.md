# Stack Files

A Stack is a strict YAML document with the exact `.estack` extension. It names
an ordered collection of Envoy bundles that together form an isolated runtime
environment.

## Complete schema

```yaml
name: production
namespace: studio:lighting
source:
  type: local
pinned_version: "2026.07"
metadata:
  owner: platform-tools
  tier: production
bundles:
  - path: ${STUDIO_BUNDLE_ROOT}/globals
    metadata:
      role: baseline
  - path: ../bundles/lighting-tools
    metadata:
      role: project
```

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Non-empty Stack name; must match its slot when published as a named Stack |
| `namespace` | No | Colon-separated context namespace; defaults to `gt` |
| `source` | No | Source descriptor; only `type: local` is currently supported |
| `pinned_version` | No | Informational version label; it does not fetch or pin bundle contents |
| `metadata` | No | Arbitrary Stack-local YAML values for consumers and automation |
| `bundles` | Yes | Non-empty ordered list of bundle declarations |
| `bundles[].path` | Yes | Bundle filesystem path |
| `bundles[].metadata` | No | Arbitrary metadata local to that bundle's Stack entry |

Unknown fields are rejected. Bundle paths must be unique after resolution, and
each path must identify a valid Envoy bundle.

## Path handling

- Relative paths resolve from the directory containing the `.estack` file.
- `${VARNAME}` expands from the process environment. An undefined variable is
  a validation error.
- `~`, `~/`, and `~\` expand from `USERPROFILE` or `HOME`.
- Forward slashes are convenient in YAML and supported on Windows.
- Bundle order is preserved and can affect Envoy command/environment
  composition.

## Named and contextual Stacks

`ENVOY_STACK_ROOTS` contains one or more named Stack registries. A named Stack
slot contains immutable versioned `.estack` files and a `latest` pointer:

```text
stacks/
└── studio/
    ├── 2026-07-27T10-30-00.estack
    ├── 2026-07-20T09-15-00.estack
    └── latest
```

Given `ENVOY_STACK_CONTEXT=studio:lighting:show_a`, Envoy attempts namespaces
from most to least specific—`studio:lighting:show_a`, `studio:lighting`, and
`studio`—then falls back to `gt`. Multiple Stacks matching the same namespace
are an error.

See [Examples](../examples.md) for annotated files and downloads. Publishing
and registry maintenance are covered by the
[Envoy user configuration guide](https://gtvfx-contrib.github.io/gt-envoy/user-config/).
