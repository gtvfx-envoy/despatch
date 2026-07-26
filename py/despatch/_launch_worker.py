"""Isolated worker that dispatches one application through Envoy."""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


def launchApplication(
    request: dict[str, Any],
    envoy_module: ModuleType | Any | None = None,
) -> int:
    """Spawn an application through the Envoy Python API.

    Args:
        request: Validated launch request containing commandLine and inTerminal.
        envoy_module: Optional module override used by tests.

    Returns:
        Process identifier returned by Envoy.

    """
    module = envoy_module or importlib.import_module("envoy")
    creation_flags = (
        getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
        if request["inTerminal"]
        else getattr(subprocess, "CREATE_NO_WINDOW", 0)
    )
    process = module.proc.spawn(
        request["commandLine"],
        creationflags=creation_flags,
    )
    return int(process.pid)


def _readRequest(request_path: Path) -> dict[str, Any]:
    """Read and validate one JSON launch request from disk."""
    with request_path.open("r", encoding="utf-8") as request_file:
        request = json.load(request_file)
    if not isinstance(request, dict):
        raise ValueError("Launch request must be an object")
    command_line = request.get("commandLine")
    if (
        not isinstance(command_line, list)
        or not command_line
        or not all(isinstance(value, str) for value in command_line)
    ):
        raise ValueError("Launch request commandLine must be a non-empty string array")
    in_terminal = request.get("inTerminal")
    if not isinstance(in_terminal, bool):
        raise ValueError("Launch request inTerminal must be a boolean")
    return {"commandLine": command_line, "inTerminal": in_terminal}


def _writeResult(result_path: Path, result: dict[str, Any]) -> None:
    """Write a launch result for the parent process."""
    result_path.write_text(json.dumps(result), encoding="utf-8")


def main(arguments: list[str] | None = None) -> int:
    """Dispatch a request file and write its result file."""
    worker_arguments = list(sys.argv[1:] if arguments is None else arguments)
    if len(worker_arguments) != 2:
        print("Expected request and result file paths", file=sys.stderr)
        return 2
    request_path = Path(worker_arguments[0])
    result_path = Path(worker_arguments[1])
    try:
        request = _readRequest(request_path)
    except (json.JSONDecodeError, OSError, TypeError, ValueError) as error:
        _writeResult(result_path, {"error": f"Invalid launch request: {error}"})
        return 2
    try:
        process_id = launchApplication(request)
    except (AttributeError, ImportError, OSError, RuntimeError, TypeError, ValueError) as error:
        _writeResult(result_path, {"error": str(error) or error.__class__.__name__})
        return 1
    _writeResult(result_path, {"processId": process_id})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
