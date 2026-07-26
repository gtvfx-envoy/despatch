"""Icon loading and caching utilities for envoy_despatch."""

from pathlib import Path
import os

from Qt import QtGui


# Cache directory relative to this module's resources folder
_ARTIFACTS_DIR = Path(__file__).parents[1] / "artifacts"
_ICON_CACHE: dict[str, QtGui.QIcon] = {}


def getResourcesDir() -> Path:
    """Return the absolute path to the resources directory.

    Returns:
        Path to the resources folder.

    """
    return _ARTIFACTS_DIR


def loadIcon(name: str) -> QtGui.QIcon:
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

    icon_path = _ARTIFACTS_DIR / "icons" / name
    if not icon_path.exists():
        # Try without extension
        for ext in (".png", ".svg", ".ico", ".jpg"):
            candidate = icon_path.with_suffix(ext)
            if candidate.exists():
                icon_path = candidate
                break

    icon = QtGui.QIcon(icon_path) if os.path.exists(icon_path) else QtGui.QIcon()
    _ICON_CACHE[name] = icon
    return icon


def loadPixmap(name: str) -> QtGui.QPixmap | None:
    """Load a pixmap by name from the resources/icons directory.

    Args:
        name: Pixmap filename or path relative to the icons directory.

    Returns:
        QPixmap loaded from disk, or None if not found.

    """
    icon = loadIcon(name)
    return icon.pixmap(24, 24) if not icon.isNull() else None


def clearCache() -> None:
    """Clear the icon cache."""
    _ICON_CACHE.clear()
