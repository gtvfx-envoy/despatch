"""Icon loading and caching utilities for envoy_despatch."""

import os
from typing import Optional

from PySide6.QtGui import QIcon, QPixmap


# Cache directory relative to this module's resources folder
_RESOURCES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")
_ICON_CACHE: dict = {}


def get_resources_dir() -> str:
    """Return the absolute path to the resources directory.

    Returns:
        Path to the resources folder.

    """
    return _RESOURCES_DIR


def load_icon(name: str) -> QIcon:
    """Load an icon by name from the resources/icons directory.

    Icons are cached after first load to avoid repeated disk I/O.

    Args:
        name: Icon filename or path relative to the icons directory.
            Supports .png, .svg, and other Qt-supported formats.

    Returns:
        QIcon loaded from disk, or an empty QIcon if not found.

    """
    if name in _ICON_CACHE:
        return _ICON_CACHE[name]

    icon_path = os.path.join(_RESOURCES_DIR, "icons", name)
    if not os.path.exists(icon_path):
        # Try without extension
        for ext in (".png", ".svg", ".ico", ".jpg"):
            candidate = icon_path + ext
            if os.path.exists(candidate):
                icon_path = candidate
                break

    icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()
    _ICON_CACHE[name] = icon
    return icon


def load_pixmap(name: str) -> Optional[QPixmap]:
    """Load a pixmap by name from the resources/icons directory.

    Args:
        name: Pixmap filename or path relative to the icons directory.

    Returns:
        QPixmap loaded from disk, or None if not found.

    """
    icon = load_icon(name)
    return icon.pixmap(24, 24) if not icon.isNull() else None


def clear_cache() -> None:
    """Clear the icon cache."""
    _ICON_CACHE.clear()
