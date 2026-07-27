"""System-aware light and dark Qt styles."""

from __future__ import annotations

from Qt import QtGui, QtWidgets


def resolveTheme(application: QtWidgets.QApplication, preference: str) -> str:
    """Resolve a persisted preference to light or dark.

    Args:
        application: Active Qt application.
        preference: system, light, or dark.

    Returns:
        Resolved theme name.

    """
    if preference in {"light", "dark"}:
        return preference
    window_color = application.palette().color(QtGui.QPalette.Window)
    return "dark" if window_color.lightness() < 128 else "light"


def applyTheme(application: QtWidgets.QApplication, preference: str) -> str:
    """Apply the selected theme and return its resolved name.

    Args:
        application: Active Qt application.
        preference: system, light, or dark.

    Returns:
        Resolved theme name.

    """
    resolved_theme = resolveTheme(application, preference)
    application.setStyleSheet(_darkStyle() if resolved_theme == "dark" else _lightStyle())
    application.setProperty("despatchTheme", resolved_theme)
    return resolved_theme


def _lightStyle() -> str:
    """Return the light theme stylesheet."""
    return _baseStyle(
        window="#f3f4f6",
        surface="#ffffff",
        surface_alt="#f6f7f9",
        border="#e2e4e9",
        text="#202124",
        muted="#71757d",
        accent="#6d5bd0",
        accent_hover="#5e4bc3",
        selection="#eeeafd",
        danger="#c84b4b",
    )


def _darkStyle() -> str:
    """Return the dark theme stylesheet."""
    return _baseStyle(
        window="#171719",
        surface="#222225",
        surface_alt="#2a2a2e",
        border="#38383e",
        text="#f1f1f3",
        muted="#a4a4ad",
        accent="#a594ff",
        accent_hover="#b4a7ff",
        selection="#363149",
        danger="#ff8787",
    )


def _baseStyle(
    *,
    window: str,
    surface: str,
    surface_alt: str,
    border: str,
    text: str,
    muted: str,
    accent: str,
    accent_hover: str,
    selection: str,
    danger: str,
) -> str:
    """Build the common application stylesheet."""
    return f"""
    QWidget {{
        color: {text};
        font-family: "Segoe UI", "Inter", sans-serif;
        font-size: 10pt;
    }}
    QMainWindow, QDialog {{ background: transparent; }}
    QFrame#windowShell, QFrame#dialogShell {{
        background: {surface};
        border: 1px solid {border};
        border-radius: 16px;
    }}
    QLabel#productTitle {{ font-size: 11pt; font-weight: 600; }}
    QLabel#sectionHeader {{ color: {muted}; font-size: 8pt; font-weight: 600; }}
    QLabel#mutedLabel {{ color: {muted}; }}
    QLabel#errorLabel {{ color: {danger}; }}
    QLineEdit, QComboBox {{
        background: {surface_alt};
        border: 1px solid {border};
        border-radius: 9px;
        padding: 8px 10px;
        selection-background-color: {accent};
    }}
    QLineEdit:focus, QComboBox:focus {{ border-color: {accent}; }}
    QComboBox::drop-down {{ border: 0; width: 24px; }}
    QPushButton, QToolButton {{
        background: {surface_alt};
        border: 1px solid {border};
        border-radius: 8px;
        padding: 7px 11px;
    }}
    QPushButton:hover, QToolButton:hover {{ border-color: {accent}; color: {accent_hover}; }}
    QPushButton#primaryButton {{ background: {accent}; color: white; border-color: {accent}; }}
    QPushButton#primaryButton:hover {{ background: {accent_hover}; }}
    QToolButton#windowButton {{ background: transparent; border: 0; padding: 5px; }}
    QListWidget {{ background: transparent; border: 0; outline: 0; }}
    QListWidget::item {{ border-radius: 10px; padding: 10px 8px; margin: 1px 0; }}
    QListWidget::item:hover {{ background: {surface_alt}; }}
    QListWidget::item:selected {{ background: {selection}; color: {text}; }}
    QMenu {{
        background: {surface};
        border: 1px solid {border};
        border-radius: 9px;
        padding: 6px;
    }}
    QMenu::item {{ border-radius: 6px; padding: 7px 22px 7px 9px; }}
    QMenu::item:selected {{ background: {selection}; }}
    QScrollBar:vertical {{ background: transparent; width: 8px; margin: 3px; }}
    QScrollBar::handle:vertical {{ background: {border}; border-radius: 4px; min-height: 28px; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QCheckBox {{ spacing: 8px; }}
    QToolTip {{ background: {surface_alt}; color: {text}; border: 1px solid {border}; }}
    """
