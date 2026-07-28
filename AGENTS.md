# Despatch Repository Instructions

## Coding standards

Follow `.github/copilot-instructions.md` for Python naming, formatting,
docstrings, built-in shadowing, and exception-handling standards.

## Domain terminology

- Use **Stack** for the runtime container that selects and isolates Envoy
  bundles.
- Use **Bundle** for an Envoy-managed unit and its cache representation.
- Stack files are YAML documents with the `.estack` extension.
- Do not introduce the retired Pipeline, Bundle Config, Package, or Package
  Cache monikers into user-facing text or the corresponding Envoy integration
  APIs. Generic uses of words such as package or configuration remain valid
  when they refer to Python packaging or unrelated application settings.

## Runtime contract

- Target Python 3.11. Envoy supplies the `Qt` compatibility shim, PySide6, and
  the Envoy Python API during normal source execution.
- Import Qt APIs through `Qt`, not directly through PySide6.
- Preserve compatibility with both source execution and the frozen Windows
  executable.
- Use `envoy python` for ordinary Python development and verification. Use
  `scripts/build-executable.ps1` for standalone executable generation.
- Do not commit workstation-specific drive letters, artifact-share locations,
  or cache paths.

## Executable and release work

Use the repository-local `build-despatch-executable` skill for PyInstaller,
frozen-runtime, executable dependency, or executable release-workflow changes.

Generated files under `build/` and `dist/` are ignored. When reporting a build,
state whether the artifact was retained and provide its exact path.

Do not claim that PyInstaller was fully tested merely because the freeze command
completed. Run the final windowed executable and verify its version and frozen
worker routes.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
