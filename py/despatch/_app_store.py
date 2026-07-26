"""Application entry model and store for envoy_despatch."""

import json
import os
from dataclasses import field
from typing import ClassVar


class ApplicationEntry:
    """Represents a single application that can be launched.

    Args:
        name: Display name of the application.
        command: Command or identifier used to launch it.
        args: Additional arguments passed at launch.
        icon: Icon filename (relative to resources/icons/).
        description: Human-readable description.
        favorite: Whether this app is marked as a favorite.
        used: Whether this app has been launched before.
        parent: Parent group name for hierarchical menus.
        in_terminal: Whether this app should launch in a terminal.

    """

    name: str
    command: str
    args: list[str] = field(default_factory=list)
    icon: str | None = None
    description: str | None = None
    favorite: bool = False
    used: bool = False
    parent: str | None = None
    in_terminal: bool = False

    def to_dict(self) -> dict:
        """Serialize to dictionary.

        Returns:
            Dictionary representation suitable for JSON storage.

        """
        return {
            "name": self.name,
            "command": self.command,
            "args": self.args,
            "icon": self.icon,
            "description": self.description,
            "favorite": self.favorite,
            "used": self.used,
            "parent": self.parent,
            "inTerminal": self.in_terminal,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ApplicationEntry":
        """Deserialize from dictionary.

        Args:
            data: Dictionary with application fields.

        Returns:
            ApplicationEntry instance.

        """
        return cls(
            name=data["name"],
            command=data["command"],
            args=data.get("args", []),
            icon=data.get("icon"),
            description=data.get("description"),
            favorite=data.get("favorite", False),
            used=data.get("used", False),
            parent=data.get("parent"),
            in_terminal=data.get("inTerminal", False),
        )


class ApplicationStore:
    """Collection of application entries with caching and sorting.

    Provides lookup, filtering, and persistence for the set of applications
    available in the current envoy stack.

    Args:
        entries: Initial list of ApplicationEntry instances.

    """

    _cache: ClassVar[dict[str, "ApplicationStore"]] = {}

    def __init__(self, entries: list[ApplicationEntry] | None = None):
        self._entries: list[ApplicationEntry] = sorted(
            entries or [], key=lambda e: e.name.lower()
        )
        self._stacks: list = []  # Will be set by from_stack

    @property
    def entries(self) -> list[ApplicationEntry]:
        """List of all application entries, sorted by name."""
        return list(self._entries)

    @property
    def applications(self) -> list[ApplicationEntry]:
        """Alias for entries (compatibility)."""
        return self.entries

    @property
    def stacks(self) -> list:
        """List of stacks associated with this store."""
        return self._stacks

    @property
    def favorites(self) -> list[ApplicationEntry]:
        """Filter to only favorite applications."""
        return [e for e in self._entries if e.favorite]

    @classmethod
    def fromStack(cls, stack) -> "ApplicationStore":
        """Create an ApplicationStore from a stack object.

        In a full implementation, this would query the envoy backend for
        packages and their Package_Menu.json files. For now, returns empty store.

        Args:
            stack: stackType or similar object representing the active stack.

        Returns:
            ApplicationStore instance populated with entries from the stack.

        """
        # Check cache first
        if hasattr(stack, 'path'):
            try:
                return cls._cache[stack.path]
            except KeyError:
                pass

        # In a full implementation, this would:
        # 1. Query envoy backend for packages in the stack
        # 2. Load Package_Menu.json from each package
        # 3. Parse entries and build the store
        # For now, return empty store
        store = cls([])
        store._stacks = [stack] if hasattr(stack, 'path') else []
        
        # Cache production stacks only (as per reference behavior)
        if not hasattr(stack, 'is_inactive') or not stack.is_inactive:
            cls._cache[stack.path] = store
        
        return store

    def findByName(self, name: str) -> ApplicationEntry | None:
        """Find an application by exact name match.

        Args:
            name: Application display name.

        Returns:
            Matching entry, or None if not found.

        """
        for entry in self._entries:
            if entry.name.lower() == name.lower():
                return entry
        return None

    def findByCommand(self, command: str) -> ApplicationEntry | None:
        """Find an application by launch command.

        Args:
            command: Command identifier.

        Returns:
            Matching entry, or None if not found.

        """
        for entry in self._entries:
            if entry.command == command:
                return entry
        return None

    def search(self, query: str) -> list[ApplicationEntry]:
        """Fuzzy search across application names and commands.

        Args:
            query: Search string to match against.

        Returns:
            Matching entries, sorted by relevance.

        """
        if not query.strip():
            return []

        query_lower = query.lower()
        results = []
        for entry in self._entries:
            name_match = query_lower in entry.name.lower()
            cmd_match = query_lower in entry.command.lower()
            if name_match or cmd_match:
                results.append(entry)
        return sorted(results, key=lambda e: (not e.favorite, e.name.lower()))

    def saveFavorites(self, path: str) -> None:
        """Save favorite status for all entries to a JSON file.

        Args:
            path: Output file path.

        """
        data = {entry.name: entry.favorite for entry in self._entries if entry.favorite}
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def loadFavorites(cls, path: str) -> dict:
        """Load favorite status from a JSON file.

        Args:
            path: Input file path.

        Returns:
            Dictionary mapping application names to favorite status.

        """
        if not os.path.exists(path):
            return {}
        with open(path, "r") as f:
            return json.load(f)

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self):
        return iter(self._entries)
