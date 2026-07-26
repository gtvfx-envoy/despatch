"""Stack type abstraction for envoy_despatch."""

from typing import List, Optional


class StackType:
    """Represents a stack configuration state.

    Args:
        name: Display name of the stack.
        group: Group attribute for sorting ($blue.group or custom).
        is_inactive: Whether this stack is marked as inactive.
        icon: Icon filename for this stack state.
        notice: Optional status message to display.
        path: Stack path/identifier (e.g., "bfd::production").

    """

    def __init__(
        self,
        name: str = "Unknown",
        group: str = "",
        is_inactive: bool = False,
        icon: str = "default.svg",
        notice: str = "",
        path: Optional[str] = None,
    ):
        self._name = name
        self._group = group or ""
        self._is_inactive = is_inactive
        self._icon = icon
        self._notice = notice
        self._path = path or name

    @property
    def name(self) -> str:
        """Display name of the stack."""
        return self._name

    @property
    def group(self) -> str:
        """Group attribute for sorting."""
        return self._group

    @property
    def is_inactive(self) -> bool:
        """Whether this stack is marked as inactive."""
        return self._is_inactive

    @property
    def icon(self) -> str:
        """Icon filename for this stack state."""
        return self._icon

    @property
    def notice(self) -> str:
        """Status message to display (empty if none)."""
        return self._notice

    @property
    def path(self) -> str:
        """Stack path/identifier."""
        return self._path

    @property
    def display_name(self) -> str:
        """Formatted display name with inactive indicator."""
        prefix = "\U0001F512 " if self._is_inactive else ""
        return "{}{}".format(prefix, self._name)

    def __repr__(self) -> str:
        return "{}(name={!r}, group={!r})".format(
            self.__class__.__name__, self._name, self._group
        )


class ProductionStack(StackType):
    """Stack representing a live production environment."""

    def __init__(self, name: str = "Production", path: Optional[str] = None):
        super().__init__(
            name=name,
            icon="production.svg",
            notice="Live stack",
            path=path,
        )


class DeveloperStack(StackType):
    """Stack representing a developer/test environment."""

    def __init__(self, name: str = "Developer", path: Optional[str] = None):
        super().__init__(
            name=name,
            icon="developer.svg",
            notice="Dev stack",
            path=path,
        )


class DisconnectedStack(StackType):
    """Stack state when the system cannot reach the backend."""

    def __init__(self):
        super().__init__(
            name="Disconnected",
            icon="disconnected.svg",
            notice="Cannot connect to envoy backend",
        )


class InvalidStack(StackType):
    """Stack state when the configuration is invalid or missing."""

    def __init__(self, reason: str = "Invalid configuration"):
        super().__init__(name="Invalid", icon="error.svg", notice=reason)


def getStackType(
    stackName: Optional[str] = None,
    group: str = "",
    is_inactive: bool = False,
    path: Optional[str] = None,
) -> StackType:
    """Determine the appropriate stack type based on context.

    Args:
        stackName: Name of the active stack, or None for default.
        group: Group attribute for sorting.
        is_inactive: Whether this stack is inactive.
        path: Stack path/identifier.

    Returns:
        Appropriate StackType instance.

    """
    if stackName is None:
        return DisconnectedStack()

    name_lower = stackName.lower()
    if "dev" in name_lower or "test" in name_lower:
        return DeveloperStack(stackName, group=group, is_inactive=is_inactive, path=path)
    return ProductionStack(stackName, group=group, is_inactive=is_inactive, path=path)
