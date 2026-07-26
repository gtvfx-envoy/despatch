"""Boundary between Despatch and the Envoy Python API."""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from types import ModuleType
from typing import Any

from . import _models


class EnvoyUnavailableError(RuntimeError):
    """Raised when the Envoy Python API cannot be loaded or queried."""


class ConfigurationSwitchError(RuntimeError):
    """Raised when a named Envoy configuration cannot be activated."""


class EnvoyGateway:
    """Discover configurations and dispatch applications through Envoy.

    Args:
        envoy_module: Optional module override used by tests.

    """

    def __init__(self, envoy_module: ModuleType | Any | None = None):
        self._envoy_module = envoy_module

    def preflight(self) -> str:
        """Validate the Envoy Python API and return its version.

        Returns:
            Envoy version string.

        Raises:
            EnvoyUnavailableError: If the module or required API is unavailable.

        """
        envoy_module = self._getEnvoyModule()
        required_names = (
            "BundleConfig",
            "discoverBundlesAuto",
            "getCurrentBundleConfig",
            "listNamedConfigs",
            "loadUserConfig",
            "proc",
            "resolveNamedConfig",
        )
        missing = [name for name in required_names if not hasattr(envoy_module, name)]
        if missing:
            joined_names = ", ".join(missing)
            raise EnvoyUnavailableError(f"Envoy Python API is missing: {joined_names}")
        return str(getattr(envoy_module, "__version__", "unknown"))

    def listConfigurations(self) -> tuple[_models.NamedConfiguration, ...]:
        """Return published named configurations.

        Returns:
            Configurations sorted by name.

        """
        try:
            entries = self._getEnvoyModule().listNamedConfigs()
            configurations = [
                _models.NamedConfiguration(
                    name=str(entry.name),
                    version=str(entry.version),
                    path=Path(entry.path),
                )
                for entry in entries
            ]
        except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as error:
            raise EnvoyUnavailableError(f"Unable to list Envoy configurations: {error}") from error
        return tuple(sorted(configurations, key=lambda entry: entry.name.casefold()))

    def getCurrentConfigurationName(self) -> str | None:
        """Return the globally selected named configuration.

        Returns:
            Configured name, or None when Envoy uses automatic discovery.

        """
        try:
            user_config = self._getEnvoyModule().loadUserConfig()
            configured_value = user_config.get("bundles_config")
        except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as error:
            raise EnvoyUnavailableError(
                f"Unable to read Envoy user configuration: {error}"
            ) from error
        if not configured_value:
            return None
        envoy_module = self._getEnvoyModule()
        if envoy_module.isConfigName(configured_value):
            return str(configured_value)
        return None

    def switchConfiguration(self, configuration_name: str | None) -> None:
        """Validate and persist a named configuration globally.

        Args:
            configuration_name: Published name, or None for automatic discovery.

        Raises:
            ConfigurationSwitchError: If resolution, validation, or persistence fails.

        """
        envoy_module = self._getEnvoyModule()
        try:
            user_config = envoy_module.loadUserConfig()
            if configuration_name is None:
                user_config.unset("bundles_config")
                user_config.save()
                return
            resolved_path = envoy_module.resolveNamedConfig(configuration_name)
            if resolved_path is None:
                raise ConfigurationSwitchError(
                    f"Envoy configuration '{configuration_name}' could not be resolved"
                )
            configuration = envoy_module.BundleConfig(resolved_path)
            tuple(configuration.bundles)
            user_config.set("bundles_config", configuration_name)
            user_config.save()
        except ConfigurationSwitchError:
            raise
        except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as error:
            raise ConfigurationSwitchError(
                f"Unable to activate Envoy configuration '{configuration_name}': {error}"
            ) from error

    def loadBundles(self) -> tuple[_models.BundleRecord, ...]:
        """Load bundles participating in the active Envoy configuration.

        Returns:
            Bundle records suitable for catalog discovery.

        """
        envoy_module = self._getEnvoyModule()
        try:
            configuration = envoy_module.getCurrentBundleConfig()
            if configuration is not None:
                return tuple(self._recordFromBundle(bundle) for bundle in configuration.bundles)
            return tuple(
                self._recordFromBundleInfo(bundle_info)
                for bundle_info in envoy_module.discoverBundlesAuto()
            )
        except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as error:
            raise EnvoyUnavailableError(f"Unable to load Envoy bundles: {error}") from error

    def spawnApplication(self, application: _models.ApplicationEntry) -> int:
        """Dispatch an application through an isolated Envoy worker.

        Args:
            application: Catalog entry to launch.

        Returns:
            Process identifier reported by Envoy.

        """
        request = {
            "commandLine": [application.command, *application.args],
            "inTerminal": application.in_terminal,
        }
        creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        with tempfile.TemporaryDirectory(prefix="despatch-launch-") as temporary_directory:
            request_path = Path(temporary_directory) / "request.json"
            result_path = Path(temporary_directory) / "result.json"
            request_path.write_text(json.dumps(request), encoding="utf-8")
            completed_process = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "despatch._launch_worker",
                    str(request_path),
                    str(result_path),
                ],
                check=False,
                creationflags=creation_flags,
            )
            result = self._readLaunchResult(result_path)
        if completed_process.returncode != 0:
            message = result.get("error") or "Envoy launch worker failed"
            raise RuntimeError(str(message))
        process_id = result.get("processId")
        if not isinstance(process_id, int):
            raise RuntimeError("Envoy launch worker returned an invalid process id")
        return process_id

    @staticmethod
    def _readLaunchResult(result_path: Path) -> dict[str, Any]:
        """Read a result produced by the isolated launch worker."""
        try:
            result = json.loads(result_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as error:
            raise RuntimeError("Envoy launch worker did not return a valid result") from error
        if not isinstance(result, dict):
            raise RuntimeError("Envoy launch worker result must be an object")
        return result

    def formatCommand(self, application: _models.ApplicationEntry) -> str:
        """Format an application as a copyable Envoy command line.

        Args:
            application: Catalog entry to format.

        Returns:
            Platform-quoted command line.

        """
        return subprocess.list2cmdline(["envoy", application.command, *application.args])

    def _getEnvoyModule(self) -> ModuleType | Any:
        """Import Envoy lazily so pure modules remain testable."""
        if self._envoy_module is not None:
            return self._envoy_module
        try:
            self._envoy_module = importlib.import_module("envoy")
        except ImportError as error:
            raise EnvoyUnavailableError(
                "The Envoy Python API is unavailable. Start Despatch with 'envoy despatch'."
            ) from error
        return self._envoy_module

    def _recordFromBundle(self, bundle: Any) -> _models.BundleRecord:
        """Convert an Envoy Bundle into a catalog record."""
        root = Path(bundle.path)
        return _models.BundleRecord(
            bundle_id=str(bundle.bndlid),
            root=root,
            envoy_directory=Path(bundle.envoy_env),
            commands=tuple(str(command) for command in bundle.commands),
            version=str(bundle.version),
            is_production=bool(bundle.is_production),
        )

    def _recordFromBundleInfo(self, bundle_info: Any) -> _models.BundleRecord:
        """Convert an auto-discovered BundleInfo into a catalog record."""
        root = Path(bundle_info.root)
        envoy_directory = Path(bundle_info.envoy_env)
        return _models.BundleRecord(
            bundle_id=str(bundle_info.bndlid),
            root=root,
            envoy_directory=envoy_directory,
            commands=self._readCommandNames(envoy_directory / "commands.json"),
        )

    @staticmethod
    def _readCommandNames(commands_path: Path) -> tuple[str, ...]:
        """Read command names for BundleInfo, which does not expose them."""
        try:
            with commands_path.open("r", encoding="utf-8") as commands_file:
                commands_data = json.load(commands_file)
        except (OSError, json.JSONDecodeError):
            return ()
        if not isinstance(commands_data, dict):
            return ()
        return tuple(str(name) for name in commands_data)
