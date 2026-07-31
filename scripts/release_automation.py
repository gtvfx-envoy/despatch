"""Release and Envoy compatibility automation for Despatch."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

SEMVER_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
DIRECT_ENVOY_APIS = (
    "Stack",
    "discoverBundlesAuto",
    "getConfigRoot",
    "isStackName",
    "listNamedStacks",
    "loadUserConfig",
    "proc.spawn",
    "resolveNamedStack",
)


def validateVersion(version: str) -> str:
    """Validate and return an unprefixed semantic version."""
    if not SEMVER_PATTERN.fullmatch(version):
        raise ValueError(f"Invalid semantic version: {version!r}")
    return version


def validateTag(tag: str) -> str:
    """Validate and return a v-prefixed semantic-version tag."""
    if not tag.startswith("v"):
        raise ValueError(f"Release tag must start with 'v': {tag!r}")
    validateVersion(tag[1:])
    return tag


def replaceExactly(
    path: Path,
    pattern: re.Pattern,
    replacement: str,
    expected_count: int,
    description: str,
) -> None:
    """Apply a deterministic text replacement with an exact match count."""
    contents = path.read_text(encoding="utf-8")
    updated, replacement_count = pattern.subn(replacement, contents)
    if replacement_count != expected_count:
        raise RuntimeError(
            f"Expected {expected_count} {description} values in {path}; found {replacement_count}."
        )
    path.write_text(updated, encoding="utf-8")


def parseReleaseState(repository_root: Path) -> dict:
    """Read the synchronized Despatch version and Envoy workflow pin."""
    pyproject_contents = (repository_root / "pyproject.toml").read_text(encoding="utf-8")
    init_contents = (repository_root / "py" / "despatch" / "__init__.py").read_text(
        encoding="utf-8"
    )
    workflow_contents = (repository_root / ".github" / "workflows" / "build-release.yml").read_text(
        encoding="utf-8"
    )
    project_match = re.search(
        r'(?ms)^\[project\]\s*.*?^version\s*=\s*"([^"]+)"$',
        pyproject_contents,
    )
    init_match = re.search(r'(?m)^__version__\s*=\s*"([^"]+)"$', init_contents)
    workflow_tags = re.findall(r"v\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", workflow_contents)
    if project_match is None or init_match is None or len(workflow_tags) != 2:
        raise RuntimeError("Despatch release versions or Envoy workflow defaults are malformed.")
    project_version = project_match.group(1)
    init_version = init_match.group(1)
    if project_version != init_version:
        raise RuntimeError(
            f"pyproject.toml version {project_version} disagrees with __init__ {init_version}."
        )
    if len(set(workflow_tags)) != 1:
        raise RuntimeError(f"Envoy workflow defaults disagree: {workflow_tags}")
    return {"version": project_version, "envoy_tag": workflow_tags[0]}


def checkRelease(
    repository_root: Path,
    expected_version: str | None = None,
    expected_envoy_tag: str | None = None,
) -> dict:
    """Validate Despatch release versions and the embedded Envoy pin."""
    state = parseReleaseState(repository_root)
    validateVersion(state["version"])
    validateTag(state["envoy_tag"])
    if expected_version and state["version"] != validateVersion(expected_version):
        raise RuntimeError(f"Expected Despatch {expected_version}, found {state['version']}.")
    if expected_envoy_tag and state["envoy_tag"] != validateTag(expected_envoy_tag):
        raise RuntimeError(
            f"Expected embedded Envoy {expected_envoy_tag}, found {state['envoy_tag']}."
        )
    return state


def prepareRelease(repository_root: Path, version: str, envoy_tag: str) -> None:
    """Synchronize the Despatch version and both embedded Envoy defaults."""
    validated_version = validateVersion(version)
    validated_tag = validateTag(envoy_tag)
    replaceExactly(
        repository_root / "pyproject.toml",
        re.compile(r'(?ms)(^\[project\]\s*.*?)^version\s*=\s*"[^"]+"$'),
        rf'\g<1>version = "{validated_version}"',
        1,
        "project version",
    )
    replaceExactly(
        repository_root / "py" / "despatch" / "__init__.py",
        re.compile(r'(?m)^__version__\s*=\s*"[^"]+"$'),
        f'__version__ = "{validated_version}"',
        1,
        "package version",
    )
    replaceExactly(
        repository_root / ".github" / "workflows" / "build-release.yml",
        re.compile(r"v\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?"),
        validated_tag,
        2,
        "Envoy release pin",
    )
    checkRelease(repository_root, validated_version, validated_tag)


def gitOutput(repository_root: Path, arguments: list[str]) -> str:
    """Run Git and return stripped standard output."""
    completed_process = subprocess.run(
        ["git", *arguments],
        cwd=repository_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed_process.stdout.strip()


def lockfileHasDependencyChanges(envoy_root: Path, base_tag: str, head_tag: str) -> bool:
    """Return whether Envoy's lockfile changed beyond workspace version lines."""
    patch = gitOutput(
        envoy_root,
        ["diff", "--unified=0", base_tag, head_tag, "--", "rust/Cargo.lock"],
    )
    changed_lines = [
        line[1:].strip()
        for line in patch.splitlines()
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
    ]
    return any(not re.fullmatch(r'version = "[^"]+"', line) for line in changed_lines)


def workspaceManifestHasDependencyChanges(envoy_root: Path, base_tag: str, head_tag: str) -> bool:
    """Return whether Envoy's workspace manifest changed beyond its release version."""
    patch = gitOutput(
        envoy_root,
        ["diff", "--unified=0", base_tag, head_tag, "--", "rust/Cargo.toml"],
    )
    changed_lines = [
        line[1:].strip()
        for line in patch.splitlines()
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
    ]
    return any(not re.fullmatch(r'version = "[^"]+"', line) for line in changed_lines)


def classifyImpact(envoy_root: Path, base_tag: str, head_tag: str) -> dict:
    """Classify Envoy release changes that can affect Despatch."""
    validateTag(base_tag)
    validateTag(head_tag)
    changed_files = tuple(
        line
        for line in gitOutput(envoy_root, ["diff", "--name-only", base_tag, head_tag]).splitlines()
        if line
    )
    relevant_files = [
        file_path
        for file_path in changed_files
        if file_path.startswith("rust/envoy-core/src/")
        or file_path.startswith("rust/envoy-py/")
        or file_path == "pyproject.toml"
        or file_path == "rust/envoy-core/Cargo.toml"
    ]
    if "rust/Cargo.lock" in changed_files and lockfileHasDependencyChanges(
        envoy_root, base_tag, head_tag
    ):
        relevant_files.append("rust/Cargo.lock")
    if "rust/Cargo.toml" in changed_files and workspaceManifestHasDependencyChanges(
        envoy_root, base_tag, head_tag
    ):
        relevant_files.append("rust/Cargo.toml")
    return {
        "classification": "review" if relevant_files else "none",
        "relevant": bool(relevant_files),
        "base_tag": base_tag,
        "head_tag": head_tag,
        "changed_files": list(changed_files),
        "relevant_files": relevant_files,
        "direct_apis": list(DIRECT_ENVOY_APIS),
    }


def writeGitHubOutput(output_path: Path, values: dict[str, str]) -> None:
    """Append simple values to a GitHub Actions output file."""
    with output_path.open("a", encoding="utf-8") as output_file:
        for name, value in values.items():
            output_file.write(f"{name}={value}\n")


def buildIssueReport(
    impact_path: Path,
    result_path: Path,
    run_url: str,
    output_path: Path,
    github_output: Path | None,
) -> None:
    """Build the Despatch release-impact issue body."""
    impact = json.loads(impact_path.read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    classification = result["classification"]
    marker = f"<!-- envoy-compatibility:{impact['head_tag']} -->"
    relevant_files = "\n".join(f"- `{file_path}`" for file_path in impact["relevant_files"])
    checks = "\n".join(f"- {name}: `{outcome}`" for name, outcome in result["checks"].items())
    direct_apis = "\n".join(f"- `{api}`" for api in DIRECT_ENVOY_APIS)
    body = f"""{marker}
Envoy {impact['head_tag']} was released after the currently embedded {impact['base_tag']}.

## Automated assessment

- Release impact: **{classification}**
- Validation run: {run_url}

### Relevant Envoy changes

{relevant_files}

### Windows source and executable validation

{checks}

### Envoy Python APIs used directly

{direct_apis}

## Maintainer checklist

- [ ] Review behavioral changes, even if all automated checks pass.
- [ ] Decide whether a Despatch release should embed this Envoy runtime.
- [ ] If releasing, use **Prepare Release** with Envoy tag `{impact['head_tag']}`.
- [ ] If no release is needed, close this issue with the rationale.
"""
    output_path.write_text(body, encoding="utf-8")
    if github_output:
        writeGitHubOutput(github_output, {"classification": classification, "marker": marker})


def buildParser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("--expect-version")
    check_parser.add_argument("--expect-envoy-tag")
    check_parser.add_argument("--github-output")
    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--version", required=True)
    prepare_parser.add_argument("--envoy-tag", required=True)
    impact_parser = subparsers.add_parser("impact")
    impact_parser.add_argument("--envoy-root", required=True)
    impact_parser.add_argument("--base-tag", required=True)
    impact_parser.add_argument("--head-tag", required=True)
    impact_parser.add_argument("--output", required=True)
    impact_parser.add_argument("--github-output")
    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("--impact", required=True)
    report_parser.add_argument("--result", required=True)
    report_parser.add_argument("--run-url", required=True)
    report_parser.add_argument("--output", required=True)
    report_parser.add_argument("--github-output")
    return parser


def main(arguments: list[str] | None = None) -> int:
    """Run Despatch release automation."""
    parser = buildParser()
    args = parser.parse_args(arguments)
    repository_root = Path(__file__).resolve().parent.parent
    try:
        if args.command == "check":
            state = checkRelease(repository_root, args.expect_version, args.expect_envoy_tag)
            print(f"Despatch v{state['version']} embeds Envoy {state['envoy_tag']}.")
            if args.github_output:
                writeGitHubOutput(
                    Path(args.github_output),
                    {"version": state["version"], "envoy_tag": state["envoy_tag"]},
                )
        elif args.command == "prepare":
            prepareRelease(repository_root, args.version, args.envoy_tag)
        elif args.command == "impact":
            result = classifyImpact(Path(args.envoy_root), args.base_tag, args.head_tag)
            Path(args.output).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            if args.github_output:
                writeGitHubOutput(
                    Path(args.github_output),
                    {"relevant": str(result["relevant"]).lower()},
                )
        else:
            buildIssueReport(
                Path(args.impact),
                Path(args.result),
                args.run_url,
                Path(args.output),
                Path(args.github_output) if args.github_output else None,
            )
    except (OSError, RuntimeError, subprocess.CalledProcessError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
