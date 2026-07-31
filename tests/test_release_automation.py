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

    def testPrepareReleaseUpdatesAllPins(self):
        """Preparation synchronizes both versions and both Envoy defaults."""
        temporary_directory = self.enterContext(tempfile.TemporaryDirectory())
        repository_root = Path(temporary_directory)
        (repository_root / "py" / "despatch").mkdir(parents=True)
        (repository_root / ".github" / "workflows").mkdir(parents=True)
        (repository_root / "pyproject.toml").write_text(
            '[project]\nname = "envoy-despatch"\nversion = "0.1.0"\n',
            encoding="utf-8",
        )
        (repository_root / "py" / "despatch" / "__init__.py").write_text(
            '__version__ = "0.1.0"\n', encoding="utf-8"
        )
        (repository_root / ".github" / "workflows" / "build-release.yml").write_text(
            "default: v0.5.1\nenv: ${{ inputs.envoy_release || 'v0.5.1' }}\n",
            encoding="utf-8",
        )
        release_automation.prepareRelease(repository_root, "0.2.0", "v0.6.0")
        state = release_automation.checkRelease(repository_root, "0.2.0", "v0.6.0")
        self.assertEqual(state, {"version": "0.2.0", "envoy_tag": "v0.6.0"})


if __name__ == "__main__":
    unittest.main()
