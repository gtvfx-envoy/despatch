# Stack Examples

These examples use contrived bundle locations. Replace them with paths to real
Envoy bundles before loading the files.

## Minimal workstation Stack

[Download `minimal.estack`](examples/minimal.estack){ .md-button }

```yaml
name: workstation
bundles:
  - path: C:/studio/bundles/globals
  - path: C:/studio/bundles/creative-tools
```

The namespace defaults to `gt`, the source defaults to local, and bundles load
in the declared order.

## Portable development Stack

[Download `portable-development.estack`](examples/portable-development.estack){ .md-button }

```yaml
name: development
namespace: studio:development
metadata:
  owner: developer-experience
  purpose: local-development
bundles:
  - path: ${STUDIO_BUNDLE_ROOT}/globals
    metadata:
      role: baseline
  - path: ../bundles/project-tools
    metadata:
      role: checkout
  - path: ~/envoy-bundles/user-overrides
    metadata:
      role: personal
```

This combines an environment-variable path, a path relative to the Stack file,
and a home-relative path. Every path must resolve to a valid bundle on the
machine loading it.

## Published production Stack

[Download `production.estack`](examples/production.estack){ .md-button }

```yaml
name: production
namespace: studio:lighting
source:
  type: local
pinned_version: "2026.07"
metadata:
  owner: lighting-tools
  tier: production
  support_channel: "#lighting-tools"
bundles:
  - path: ${STUDIO_BUNDLE_ROOT}/globals/4.2.0
    metadata:
      role: baseline
      required: true
  - path: ${STUDIO_BUNDLE_ROOT}/pythoncore/3.11.9
    metadata:
      role: runtime
  - path: ${SHOW_BUNDLE_ROOT}/lighting/12.4.1
    metadata:
      role: department
      support_tier: critical
```

This demonstrates every currently supported document field. The pinned version
and metadata are informational; the bundle paths still identify the actual
contents loaded by Envoy.

!!! warning

    YAML field names are strict. Unsupported fields, duplicate resolved bundle
    paths, missing variables, empty bundle lists, and invalid bundle directories
    cause the Stack to be rejected.
