"""Tests for Despatch release automation."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "release_automation.py"
SPEC = importlib.util.spec_from_file_location("release_automation", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
release_automation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release_automation)


class ReleaseAutomationTests(unittest.TestCase):
    """Exercise deterministic release preparation."""

    def testValidateVersionAcceptsSemver(self):
        """Valid SemVer values are returned unchanged."""
        for version in ("0.1.0", "1.0.0-rc.1", "2.3.4+build.5"):
            with self.subTest(version=version):
                self.assertEqual(release_automation.validateVersion(version), version)

    def testValidateVersionRejectsInvalidValues(self):
        """Invalid release values are rejected."""
        for version in ("v0.1.0", "01.2.3", "1.2", "latest"):
            with self.subTest(version=version), self.assertRaises(ValueError):
                release_automation.validateVersion(version)

    def testVersionToTag(self):
        """Unprefixed dependency versions convert to Git tags."""
        self.assertEqual(release_automation.versionToTag("0.6.1"), "v0.6.1")
        with self.assertRaises(ValueError):
            release_automation.versionToTag("v0.6.1")

    def makeRepository(self, envoy_pin: str | None = "0.5.1") -> Path:
        """Create a minimal repository; omit the Envoy pin table when envoy_pin is None."""
        temporary_directory = self.enterContext(tempfile.TemporaryDirectory())
        repository_root = Path(temporary_directory)
        (repository_root / "py" / "despatch").mkdir(parents=True)
        pyproject_contents = '[project]\nname = "envoy-despatch"\nversion = "0.1.0"\n'
        if envoy_pin is not None:
            pyproject_contents += f'\n[tool.despatch]\nenvoy-version = "{envoy_pin}"\n'
        (repository_root / "pyproject.toml").write_text(pyproject_contents, encoding="utf-8")
        (repository_root / "py" / "despatch" / "__init__.py").write_text(
            '__version__ = "0.1.0"\n', encoding="utf-8"
        )
        return repository_root

    def testPrepareReleaseUpdatesAllPins(self):
        """Preparation synchronizes both versions and the Envoy pin."""
        repository_root = self.makeRepository()
        release_automation.prepareRelease(repository_root, "0.2.0", "0.6.0")
        state = release_automation.checkRelease(repository_root, "0.2.0", "0.6.0")
        self.assertEqual(state, {"version": "0.2.0", "envoy_tag": "v0.6.0"})

    def testPrepareReleaseNeverRewritesWorkflows(self):
        """Workflow files stay untouched because the release App cannot push them."""
        repository_root = self.makeRepository()
        workflow_path = repository_root / ".github" / "workflows" / "build-release.yml"
        workflow_path.parent.mkdir(parents=True)
        workflow_path.write_text("default: 0.5.1\n", encoding="utf-8")
        release_automation.prepareRelease(repository_root, "0.2.0", "0.6.0")
        self.assertEqual(workflow_path.read_text(encoding="utf-8"), "default: 0.5.1\n")

    def testPrepareReleaseRequiresAnEnvoyPin(self):
        """Preparation fails closed when pyproject.toml has no Envoy pin to update."""
        repository_root = self.makeRepository(envoy_pin=None)
        with self.assertRaisesRegex(RuntimeError, "Envoy release pin"):
            release_automation.prepareRelease(repository_root, "0.2.0", "0.6.0")


if __name__ == "__main__":
    unittest.main()
