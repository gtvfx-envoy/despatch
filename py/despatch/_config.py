"""User configuration for envoy_despatch."""

import json
import os
from typing import Any, Dict, List, Optional


DEFAULT_CONFIG_DIR = os.path.join(
    os.environ.get("APPDATA", os.path.expanduser("~")),
    "envoy_despatch",
)
DEFAULT_CONFIG_PATH = os.path.join(DEFAULT_CONFIG_DIR, "config.json")

# Default configuration values
_DEFAULTS: Dict[str, Any] = {
    "favorites": {},  # {app_name: bool}
    "favorite_stacks": [],  # list of stack names
    "active_stack": None,
    "stack_mode": "classic",  # "classic" or "hidden"
    "auto_download_updates": True,
    "keep_window_open_on_launch": False,
    "recent_custom_stacks": [],  # list of recent custom stack paths
    "time_machine_expiration": None,  # ISO timestamp when TM expires
}


class Config:
    """Persistent user configuration for envoy_despatch.

    Stores favorites, active stack, and other user preferences as JSON.

    Args:
        config_path: Path to the configuration file. Defaults to platform-specific location.

    """

    def __init__(self, config_path: Optional[str] = None):
        self._config_path = config_path or DEFAULT_CONFIG_PATH
        self._data: Dict[str, Any] = {}
        self._load()

    # --- Favorites ---

    @property
    def favorites(self) -> Dict[str, bool]:
        """Dictionary mapping application names to favorite status.

        Returns:
            Dict of {name: bool} for favorited applications.

        """
        return self._data.get("favorites", {})

    @favorites.setter
    def favorites(self, value: Dict[str, bool]) -> None:
        self._data["favorites"] = value
        self.save()

    def isFavorite(self, name: str) -> bool:
        """Check if an application is marked as a favorite.

        Args:
            name: Application display name.

        Returns:
            True if the application is favorited.

        """
        return self.favorites.get(name, False)

    def toggleFavorite(self, name: str) -> bool:
        """Toggle the favorite status of an application.

        Args:
            name: Application display name.

        Returns:
            New favorite status after toggling.

        """
        current = self.favorites.get(name, False)
        new_status = not current
        self.favorites[name] = new_status
        return new_status

    # --- Favorite stacks ---

    @property
    def favorite_stacks(self) -> List[str]:
        """List of favorited stack names.

        Returns:
            List of stack name strings.

        """
        return self._data.get("favorite_stacks", [])

    @favorite_stacks.setter
    def favorite_stacks(self, value: List[str]) -> None:
        self._data["favorite_stacks"] = value
        self.save()

    def addFavoriteStack(self, name: str) -> None:
        """Add a stack to favorites if not already present.

        Args:
            name: Stack name to favorite.

        """
        if name not in self.favorite_stacks:
            self.favorite_stacks.append(name)

    def removeFavoriteStack(self, name: str) -> None:
        """Remove a stack from favorites.

        Args:
            name: Stack name to unfavorite.

        """
        if name in self.favorite_stacks:
            self.favorite_stacks.remove(name)

    # --- Active stack ---

    @property
    def active_stack(self) -> Optional[str]:
        """Name of the currently active stack.

        Returns:
            stack name string, or None if not set.

        """
        return self._data.get("active_stack")

    @active_stack.setter
    def active_stack(self, value: Optional[str]) -> None:
        self._data["active_stack"] = value
        self.save()

    # --- stack Mode ---

    @property
    def stack_mode(self) -> str:
        """Current stack display mode.

        Returns:
            "classic" or "hidden".

        """
        return self._data.get("stack_mode", _DEFAULTS["stack_mode"])

    @stack_mode.setter
    def stack_mode(self, value: str) -> None:
        if value not in ("classic", "hidden"):
            raise ValueError(f"Invalid stack mode: {value}")
        self._data["stack_mode"] = value
        self.save()

    # --- Settings ---

    @property
    def auto_download_updates(self) -> bool:
        """Whether to automatically cache packages on stack change.

        Returns:
            True if auto-download is enabled.

        """
        return self._data.get("auto_download_updates", _DEFAULTS["auto_download_updates"])

    @auto_download_updates.setter
    def auto_download_updates(self, value: bool) -> None:
        self._data["auto_download_updates"] = value
        self.save()

    @property
    def keep_window_open_on_launch(self) -> bool:
        """Whether to keep the main window open after launching an app.

        Returns:
            True if window should stay open.

        """
        return self._data.get("keep_window_open_on_launch", _DEFAULTS["keep_window_open_on_launch"])

    @keep_window_open_on_launch.setter
    def keep_window_open_on_launch(self, value: bool) -> None:
        self._data["keep_window_open_on_launch"] = value
        self.save()

    # --- Time Machine ---

    @property
    def time_machine_expiration(self) -> Optional[str]:
        """ISO timestamp when Time Machine expiration occurs.

        Returns:
            ISO timestamp string, or None if not in Time Machine mode.

        """
        return self._data.get("time_machine_expiration")

    @time_machine_expiration.setter
    def time_machine_expiration(self, value: Optional[str]) -> None:
        self._data["time_machine_expiration"] = value
        self.save()

    # --- Custom stacks ---

    @property
    def recent_custom_stacks(self) -> List[str]:
        """List of recently used custom stack file paths.

        Returns:
            List of file path strings.

        """
        return self._data.get("recent_custom_stacks", [])

    @recent_custom_stacks.setter
    def recent_custom_stacks(self, value: List[str]) -> None:
        self._data["recent_custom_stacks"] = value
        self.save()

    def addRecentCustomStack(self, path: str) -> None:
        """Add a custom stack path to recent list (max 10).

        Args:
            path: File path of the custom stack.

        """
        recent = self.recent_custom_stacks
        if path in recent:
            recent.remove(path)
        recent.insert(0, path)
        self.recent_custom_stacks = recent[:10]

    # --- Persistence ---

    def _load(self) -> None:
        """Load configuration from disk."""
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, "r") as f:
                    loaded = json.load(f)
                self._data = {**_DEFAULTS, **loaded}
            except (json.JSONDecodeError, IOError):
                self._data = dict(_DEFAULTS)

    def save(self) -> None:
        """Save configuration to disk."""
        os.makedirs(os.path.dirname(self._config_path) or ".", exist_ok=True)
        with open(self._config_path, "w") as f:
            json.dump(self._data, f, indent=2)
