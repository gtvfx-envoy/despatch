from pathlib import Path

import envoy


def makeBundle(bundle_path: Path) -> Path:
    envoy_directory = bundle_path / ".envoy"
    envoy_directory.mkdir(parents=True)
    (envoy_directory / "commands.json").write_text('{"sample": {}}', encoding="utf-8")
    return bundle_path


def loadExample(example_name: str, stack_path: Path, replacements: dict[str, str]):
    example_path = Path(__file__).parents[1] / "docs" / "examples" / example_name
    contents = example_path.read_text(encoding="utf-8")
    for original, replacement in replacements.items():
        contents = contents.replace(original, replacement.replace("\\", "/"))
    stack_path.write_text(contents, encoding="utf-8")
    stack = envoy.Stack(stack_path)
    assert tuple(stack.bundles)
    return stack


def testMinimalStackExampleLoads(tmp_path):
    globals_bundle = makeBundle(tmp_path / "globals")
    creative_bundle = makeBundle(tmp_path / "creative-tools")

    stack = loadExample(
        "minimal.estack",
        tmp_path / "minimal.estack",
        {
            "C:/studio/bundles/globals": str(globals_bundle),
            "C:/studio/bundles/creative-tools": str(creative_bundle),
        },
    )

    assert stack.name == "minimal"
    assert stack.namespace == "gt"


def testPortableStackExampleLoads(monkeypatch, tmp_path):
    stack_directory = tmp_path / "stacks"
    stack_directory.mkdir()
    studio_root = tmp_path / "studio"
    makeBundle(studio_root / "globals")
    makeBundle(tmp_path / "bundles" / "project-tools")
    user_directory = tmp_path / "user"
    makeBundle(user_directory / "envoy-bundles" / "user-overrides")
    monkeypatch.setenv("STUDIO_BUNDLE_ROOT", str(studio_root))
    monkeypatch.setenv("USERPROFILE", str(user_directory))

    stack = loadExample(
        "portable-development.estack",
        stack_directory / "portable-development.estack",
        {},
    )

    assert stack.name == "portable-development"
    assert stack.namespace == "studio:development"
    assert stack.metadata["owner"] == "developer-experience"
    assert len(stack.bundles) == 3


def testProductionStackExampleLoads(monkeypatch, tmp_path):
    studio_root = tmp_path / "studio"
    show_root = tmp_path / "show"
    makeBundle(studio_root / "globals" / "4.2.0")
    makeBundle(studio_root / "pythoncore" / "3.11.9")
    makeBundle(show_root / "lighting" / "12.4.1")
    monkeypatch.setenv("STUDIO_BUNDLE_ROOT", str(studio_root))
    monkeypatch.setenv("SHOW_BUNDLE_ROOT", str(show_root))

    stack = loadExample(
        "production.estack",
        tmp_path / "production.estack",
        {},
    )

    assert stack.name == "production"
    assert stack.pinned_version == "2026.07"
    assert stack.metadata["tier"] == "production"
    assert len(stack.bundles) == 3


def testRepositoryBuildStackLoads(monkeypatch, tmp_path):
    fixture_path = Path(__file__).parent / "fixtures" / "stacks" / "build" / "build.estack"
    contents = fixture_path.read_text(encoding="utf-8")
    bundle_prefix = "${ENVOY_STUDIO_BNDLS}/"
    bundle_paths = [
        line.strip().removeprefix("- path: ")
        for line in contents.splitlines()
        if line.strip().startswith("- path: ")
    ]

    assert bundle_paths
    assert all(bundle_path.startswith(bundle_prefix) for bundle_path in bundle_paths)

    studio_bundle_root = tmp_path / "studio-bundles"
    for bundle_path in bundle_paths:
        makeBundle(studio_bundle_root / bundle_path.removeprefix(bundle_prefix))
    monkeypatch.setenv("ENVOY_STUDIO_BNDLS", str(studio_bundle_root))

    stack = envoy.Stack(fixture_path)

    assert stack.name == "build"
    assert stack.namespace == "gt:despatch:ci"
    assert len(stack.bundles) == len(bundle_paths)
