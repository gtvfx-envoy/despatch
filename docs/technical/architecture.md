# Architecture

Despatch is a presentation and dispatch layer over the Envoy Python API. It
does not resolve command environments itself.

```mermaid
sequenceDiagram
    participant User
    participant Despatch
    participant Envoy
    participant Stack as .estack
    participant Bundles
    participant Process

    User->>Despatch: Choose Stack or refresh
    Despatch->>Envoy: Resolve selection and load bundles
    Envoy->>Stack: Parse strict YAML
    Stack-->>Envoy: Ordered bundle paths
    Envoy->>Bundles: Validate bundles and commands
    Despatch->>Bundles: Read .envoy/despatch.json
    Despatch-->>User: Display searchable catalog
    User->>Despatch: Launch application
    Despatch->>Envoy: Spawn command with Stack context
    Envoy->>Process: Build isolated environment and start
```

## Responsibilities

| Component | Responsibility |
|---|---|
| Envoy Stack | Selects the ordered bundles forming a runtime container |
| Envoy bundle | Declares commands and environment files |
| Despatch manifest | Selects and describes commands exposed in the UI |
| Despatch settings | Stores local presentation and convenience preferences |
| Envoy user config | Stores the shared selected Stack |

Catalog refreshes and launches run outside the Qt UI thread. Application launch
uses an isolated worker so frozen and source executions produce the same Envoy
runtime behavior.

## Source and frozen execution

Despatch supports the Envoy-provided Python 3.11 runtime and a one-file Windows
executable. The executable contains Envoy, Qt.py, PySide6, product resources,
and this documentation site. The same manifest, Stack, and settings formats
apply in both modes.
