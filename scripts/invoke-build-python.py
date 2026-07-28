"""Run a build-time Python command and persist its real exit code."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def parseArgs(arguments: list[str] | None = None) -> argparse.Namespace:
    """Parse wrapper arguments and the child Python command."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", required=True, type=Path)
    parser.add_argument("--tool-directory", type=Path)
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    """Run the child interpreter and write its exit code for PowerShell."""
    args = parseArgs(arguments)
    child_arguments = list(args.arguments)
    if child_arguments[:1] == ["--"]:
        child_arguments = child_arguments[1:]
    child_environment = os.environ.copy()
    if args.tool_directory:
        existing_python_path = child_environment.get("PYTHONPATH", "")
        path_entries = [str(args.tool_directory)]
        if existing_python_path:
            path_entries.append(existing_python_path)
        child_environment["PYTHONPATH"] = os.pathsep.join(path_entries)
    completed_process = subprocess.run(
        [sys.executable, *child_arguments],
        check=False,
        env=child_environment,
    )
    args.status.write_text(
        json.dumps({"exitCode": completed_process.returncode}),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
