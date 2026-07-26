"""Typed domain models used by Despatch."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class NamedConfiguration:
    """A published Envoy bundle configuration."""

    name: str
    version: str
    path: Path


@dataclass(frozen=True, slots=True)
class BundleRecord:
    """Bundle metadata required for catalog discovery."""

    bundle_id: str
    root: Path
    envoy_directory: Path
    commands: tuple[str, ...]
    version: str = ""
    is_production: bool = False


@dataclass(frozen=True, slots=True)
class CatalogGroup:
    """A display group declared by a bundle manifest."""

    stable_id: str
    name: str
    order: int
    bundle_id: str


@dataclass(frozen=True, slots=True)
class ApplicationEntry:
    """A launchable Envoy command declared by a bundle manifest."""

    stable_id: str
    application_id: str
    bundle_id: str
    name: str
    command: str
    args: tuple[str, ...]
    description: str
    icon_path: Path | None
    group_id: str
    keywords: tuple[str, ...]
    in_terminal: bool
    order: int
    source_path: Path

    @property
    def command_line(self) -> tuple[str, ...]:
        """Command and arguments as an argv tuple."""
        return (self.command, *self.args)


@dataclass(frozen=True, slots=True)
class CatalogDiagnostic:
    """A recoverable issue encountered while loading a catalog."""

    severity: str
    message: str
    source_path: Path | None = None


@dataclass(frozen=True, slots=True)
class CatalogSnapshot:
    """A complete immutable application catalog snapshot."""

    configuration_name: str | None
    applications: tuple[ApplicationEntry, ...]
    groups: tuple[CatalogGroup, ...]
    diagnostics: tuple[CatalogDiagnostic, ...]

    def applicationMap(self) -> dict[str, ApplicationEntry]:
        """Return applications keyed by stable identity.

        Returns:
            Mapping of stable identity to application entry.

        """
        return {application.stable_id: application for application in self.applications}
