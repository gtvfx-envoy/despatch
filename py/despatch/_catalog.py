"""Load Despatch manifests from active Envoy bundles."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from . import _constants, _models


def getCurrentPlatform() -> str:
    """Return the manifest platform token for this interpreter."""
    if sys.platform == "win32":
        return "windows"
    if sys.platform == "darwin":
        return "macos"
    return "linux"


class CatalogLoader:
    """Build immutable catalog snapshots from an Envoy gateway.

    Args:
        gateway: Object providing loadBundles and current configuration methods.
        platform_name: Optional manifest platform override used by tests.

    """

    def __init__(self, gateway: Any, platform_name: str | None = None):
        self._gateway = gateway
        self._platform_name = platform_name or getCurrentPlatform()

    def loadCatalog(self) -> _models.CatalogSnapshot:
        """Load and validate all manifests in the active configuration.

        Returns:
            Complete application catalog and recoverable diagnostics.

        """
        bundles = self._gateway.loadBundles()
        configuration_name = self._gateway.getCurrentConfigurationName()
        command_names = {
            command_name for bundle in bundles for command_name in bundle.commands
        }
        groups: list[_models.CatalogGroup] = []
        applications: list[_models.ApplicationEntry] = []
        diagnostics: list[_models.CatalogDiagnostic] = []

        for bundle in bundles:
            manifest_path = bundle.envoy_directory / _constants.MANIFEST_FILENAME
            if not manifest_path.is_file():
                continue
            manifest_data = self._readManifest(manifest_path, diagnostics)
            if manifest_data is None:
                continue
            bundle_groups, bundle_applications = self._parseManifest(
                bundle,
                manifest_path,
                manifest_data,
                command_names,
                diagnostics,
            )
            groups.extend(bundle_groups)
            applications.extend(bundle_applications)

        groups.sort(key=lambda group: (group.order, group.name.casefold(), group.stable_id))
        applications.sort(key=lambda application: (application.order, application.name.casefold()))
        return _models.CatalogSnapshot(
            configuration_name=configuration_name,
            applications=tuple(applications),
            groups=tuple(groups),
            diagnostics=tuple(diagnostics),
        )

    @staticmethod
    def _readManifest(
        manifest_path: Path,
        diagnostics: list[_models.CatalogDiagnostic],
    ) -> dict[str, Any] | None:
        """Read one manifest and report recoverable parse failures."""
        try:
            with manifest_path.open("r", encoding="utf-8") as manifest_file:
                manifest_data = json.load(manifest_file)
        except OSError as error:
            diagnostics.append(
                _models.CatalogDiagnostic(
                    "error", f"Unable to read manifest: {error}", manifest_path
                )
            )
            return None
        except json.JSONDecodeError as error:
            diagnostics.append(
                _models.CatalogDiagnostic(
                    "error",
                    f"Invalid JSON at line {error.lineno}, column {error.colno}: {error.msg}",
                    manifest_path,
                )
            )
            return None
        if not isinstance(manifest_data, dict):
            diagnostics.append(
                _models.CatalogDiagnostic("error", "Manifest root must be an object", manifest_path)
            )
            return None
        if manifest_data.get("schemaVersion") != _constants.MANIFEST_SCHEMA_VERSION:
            diagnostics.append(
                _models.CatalogDiagnostic(
                    "error",
                    f"Unsupported schemaVersion; expected {_constants.MANIFEST_SCHEMA_VERSION}",
                    manifest_path,
                )
            )
            return None
        return manifest_data

    def _parseManifest(
        self,
        bundle: _models.BundleRecord,
        manifest_path: Path,
        manifest_data: dict[str, Any],
        command_names: set[str],
        diagnostics: list[_models.CatalogDiagnostic],
    ) -> tuple[list[_models.CatalogGroup], list[_models.ApplicationEntry]]:
        """Validate one parsed manifest."""
        groups = self._parseGroups(bundle, manifest_path, manifest_data.get("groups"), diagnostics)
        group_ids = {group.stable_id for group in groups}
        applications_data = manifest_data.get("applications")
        if not isinstance(applications_data, list):
            diagnostics.append(
                _models.CatalogDiagnostic(
                    "error", "'applications' must be an array", manifest_path
                )
            )
            return groups, []

        applications: list[_models.ApplicationEntry] = []
        seen_ids: set[str] = set()
        for order, application_data in enumerate(applications_data):
            application = self._parseApplication(
                bundle,
                manifest_path,
                application_data,
                order,
                command_names,
                group_ids,
                seen_ids,
                diagnostics,
            )
            if application is not None:
                applications.append(application)
        return groups, applications

    @staticmethod
    def _parseGroups(
        bundle: _models.BundleRecord,
        manifest_path: Path,
        groups_data: Any,
        diagnostics: list[_models.CatalogDiagnostic],
    ) -> list[_models.CatalogGroup]:
        """Validate manifest group declarations."""
        if groups_data is None:
            return []
        if not isinstance(groups_data, list):
            diagnostics.append(
                _models.CatalogDiagnostic("warning", "'groups' must be an array", manifest_path)
            )
            return []
        groups: list[_models.CatalogGroup] = []
        seen_ids: set[str] = set()
        for order, group_data in enumerate(groups_data):
            if not isinstance(group_data, dict):
                diagnostics.append(
                    _models.CatalogDiagnostic(
                        "warning", "Group entries must be objects", manifest_path
                    )
                )
                continue
            group_id = group_data.get("id")
            group_name = group_data.get("name")
            if not isinstance(group_id, str) or not group_id.strip():
                diagnostics.append(
                    _models.CatalogDiagnostic(
                        "warning", "Group 'id' must be a string", manifest_path
                    )
                )
                continue
            if not isinstance(group_name, str) or not group_name.strip():
                diagnostics.append(
                    _models.CatalogDiagnostic(
                        "warning", "Group 'name' must be a string", manifest_path
                    )
                )
                continue
            if group_id in seen_ids:
                diagnostics.append(
                    _models.CatalogDiagnostic(
                        "warning", f"Duplicate group id '{group_id}'", manifest_path
                    )
                )
                continue
            seen_ids.add(group_id)
            declared_order = group_data.get("order", order)
            if not isinstance(declared_order, int):
                declared_order = order
            groups.append(
                _models.CatalogGroup(
                    stable_id=f"{bundle.bundle_id}:{group_id}",
                    name=group_name.strip(),
                    order=declared_order,
                    bundle_id=bundle.bundle_id,
                )
            )
        return groups

    def _parseApplication(
        self,
        bundle: _models.BundleRecord,
        manifest_path: Path,
        application_data: Any,
        order: int,
        command_names: set[str],
        group_ids: set[str],
        seen_ids: set[str],
        diagnostics: list[_models.CatalogDiagnostic],
    ) -> _models.ApplicationEntry | None:
        """Validate one application entry and construct its model."""
        if not isinstance(application_data, dict):
            self._addApplicationDiagnostic(
                diagnostics, manifest_path, order, "entry must be an object"
            )
            return None
        application_id = application_data.get("id")
        name = application_data.get("name")
        command = application_data.get("command")
        if not isinstance(application_id, str) or not application_id.strip():
            self._addApplicationDiagnostic(diagnostics, manifest_path, order, "'id' is required")
            return None
        if application_id in seen_ids:
            self._addApplicationDiagnostic(
                diagnostics, manifest_path, order, f"duplicate id '{application_id}'"
            )
            return None
        seen_ids.add(application_id)
        if not isinstance(name, str) or not name.strip():
            self._addApplicationDiagnostic(diagnostics, manifest_path, order, "'name' is required")
            return None
        if not isinstance(command, str) or not command.strip():
            self._addApplicationDiagnostic(
                diagnostics, manifest_path, order, "'command' is required"
            )
            return None
        if command not in command_names:
            self._addApplicationDiagnostic(
                diagnostics,
                manifest_path,
                order,
                f"command '{command}' is not available in the active Envoy configuration",
            )
            return None
        platforms = application_data.get("platforms", [])
        if platforms and (
            not isinstance(platforms, list)
            or not all(isinstance(platform_name, str) for platform_name in platforms)
        ):
            self._addApplicationDiagnostic(
                diagnostics, manifest_path, order, "'platforms' must be an array of strings"
            )
            return None
        if platforms and self._platform_name not in {value.casefold() for value in platforms}:
            return None
        args = application_data.get("args", [])
        keywords = application_data.get("keywords", [])
        if not isinstance(args, list) or not all(isinstance(value, str) for value in args):
            self._addApplicationDiagnostic(
                diagnostics, manifest_path, order, "'args' must be an array of strings"
            )
            return None
        if not isinstance(keywords, list) or not all(isinstance(value, str) for value in keywords):
            self._addApplicationDiagnostic(
                diagnostics, manifest_path, order, "'keywords' must be an array of strings"
            )
            return None
        description = application_data.get("description", "")
        if not isinstance(description, str):
            self._addApplicationDiagnostic(
                diagnostics, manifest_path, order, "'description' must be a string"
            )
            return None
        in_terminal = application_data.get("inTerminal", False)
        if not isinstance(in_terminal, bool):
            self._addApplicationDiagnostic(
                diagnostics, manifest_path, order, "'inTerminal' must be a boolean"
            )
            return None
        group_id = ""
        declared_group = application_data.get("group")
        if declared_group is not None:
            if not isinstance(declared_group, str):
                self._addApplicationDiagnostic(
                    diagnostics, manifest_path, order, "'group' must be a string"
                )
                return None
            group_id = f"{bundle.bundle_id}:{declared_group}"
            if group_id not in group_ids:
                self._addApplicationDiagnostic(
                    diagnostics,
                    manifest_path,
                    order,
                    f"group '{declared_group}' is not declared",
                )
                return None
        icon_path = self._resolveIconPath(
            bundle.root,
            application_data.get("icon"),
            manifest_path,
            order,
            diagnostics,
        )
        return _models.ApplicationEntry(
            stable_id=f"{bundle.bundle_id}:{application_id}",
            application_id=application_id,
            bundle_id=bundle.bundle_id,
            name=name.strip(),
            command=command,
            args=tuple(args),
            description=description.strip(),
            icon_path=icon_path,
            group_id=group_id,
            keywords=tuple(keywords),
            in_terminal=in_terminal,
            order=order,
            source_path=manifest_path,
        )

    def _resolveIconPath(
        self,
        bundle_root: Path,
        icon_value: Any,
        manifest_path: Path,
        order: int,
        diagnostics: list[_models.CatalogDiagnostic],
    ) -> Path | None:
        """Resolve a safe icon path below the bundle's resources/icons directory."""
        if icon_value is None:
            return None
        if not isinstance(icon_value, str) or not icon_value.strip():
            self._addApplicationDiagnostic(
                diagnostics, manifest_path, order, "'icon' must be a non-empty string"
            )
            return None
        root = (bundle_root / _constants.RESOURCE_ICONS_DIRECTORY).resolve()
        candidate = (root / icon_value).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            self._addApplicationDiagnostic(
                diagnostics,
                manifest_path,
                order,
                "icon path escapes the bundle resources/icons directory",
            )
            return None
        if not candidate.is_file():
            self._addApplicationDiagnostic(
                diagnostics,
                manifest_path,
                order,
                f"icon file does not exist under resources/icons: {icon_value}",
            )
            return None
        return candidate

    @staticmethod
    def _addApplicationDiagnostic(
        diagnostics: list[_models.CatalogDiagnostic],
        manifest_path: Path,
        order: int,
        message: str,
    ) -> None:
        """Append a consistently formatted application diagnostic."""
        diagnostics.append(
            _models.CatalogDiagnostic(
                "warning", f"Application entry {order + 1}: {message}", manifest_path
            )
        )
