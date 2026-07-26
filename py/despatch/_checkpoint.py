"""Version rollback UI for envoy_despatch.

Provides a browser for stack version history, package diff viewing, and
version application (rollback).
"""

from datetime import datetime

from Qt import QtCore, QtWidgets


class VersionEntry:
    """Represents a single stack version snapshot.

    Args:
        name: Human-readable version identifier (e.g., "v2.3.1").
        timestamp: When this version was active.
        packages: List of package names included in this version.

    """

    def __init__(self, name: str, timestamp: datetime, packages: list[str] | None = None):
        self._name = name
        self._timestamp = timestamp
        self._packages = packages or []

    @property
    def name(self) -> str:
        """Version identifier."""
        return self._name

    @property
    def timestamp(self) -> datetime:
        """When this version was active."""
        return self._timestamp

    @property
    def packages(self) -> list[str]:
        """Packages included in this version."""
        return list(self._packages)

    def __repr__(self) -> str:
        return f"VersionEntry(name={self._name!r}, date={self._timestamp.isoformat()})"


class PackageDiff:
    """Represents the difference between two stack versions.

    Args:
        added: Packages present in the newer version but not the older.
        removed: Packages present in the older version but not the newer.
        changed: Packages present in both but with different versions.

    """

    def __init__(
        self,
        added: list[str] | None = None,
        removed: list[str] | None = None,
        changed: list[str] | None = None,
    ):
        self._added = added or []
        self._removed = removed or []
        self._changed = changed or []

    @property
    def added(self) -> list[str]:
        """Packages added in the newer version."""
        return list(self._added)

    @property
    def removed(self) -> list[str]:
        """Packages removed in the newer version."""
        return list(self._removed)

    @property
    def changed(self) -> list[str]:
        """Packages present in both versions but modified."""
        return list(self._changed)

    def __repr__(self) -> str:
        return f"PackageDiff(added={len(self._added)}, removed={len(self._removed)}, changed={len(self._changed)})"


class CheckpointDialog(QtWidgets.QDialog):
    """Version rollback dialog for stack history.

    Displays a list of available versions, allows selection and comparison,
    and provides an "apply" button to roll back to a chosen version.

    Args:
        parent: Parent widget. Defaults to None for top-level window.

    """

    version_selected = QtCore.Signal(str)  # version name

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("envoy_despatch — Checkpoint")
        self.setMinimumSize(700, 500)

        self._versions: list[VersionEntry] = []
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Build the time machine dialog widget hierarchy."""
        layout = QtWidgets.QVBoxLayout(self)

        # Header with title and apply button
        header_layout = QtWidgets.QHBoxLayout()
        self._title_label = QtWidgets.QLabel("Stack Checkpoint History")
        self._title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        header_layout.addWidget(self._title_label, stretch=1)

        self._apply_button = QtWidgets.QPushButton("Apply Selected Version")
        self._apply_button.setEnabled(False)
        self._apply_button.clicked.connect(self._on_apply)
        header_layout.addWidget(self._apply_button)
        layout.addLayout(header_layout)

        # Main splitter: version list | diff viewer
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal) # type: ignore

        # Left: version list
        version_layout = QtWidgets.QVBoxLayout()
        self._version_list = QtWidgets.QListWidget()
        version_layout.addWidget(self._version_list)
        version_widget = QtWidgets.QWidget()
        version_widget.setLayout(version_layout)
        splitter.addWidget(version_widget)

        # Right: diff viewer
        diff_layout = QtWidgets.QVBoxLayout()
        self._diff_text = QtWidgets.QTextEdit()
        self._diff_text.setReadOnly(True)
        self._diff_text.setFontFamily("Courier New")
        diff_layout.addWidget(self._diff_text)
        diff_widget = QtWidgets.QWidget()
        diff_widget.setLayout(diff_layout)
        splitter.addWidget(diff_widget)

        splitter.setSizes([250, 450])
        layout.addWidget(splitter)

    def _connect_signals(self) -> None:
        """Wire up signal/slot connections."""
        self._version_list.currentItemChanged.connect(self._on_version_selected)

    def populate_versions(self, versions: list[VersionEntry]) -> None:
        """Populate the version list.

        Args:
            versions: List of VersionEntry instances to display (newest first).

        """
        self._versions = sorted(versions, key=lambda v: v.timestamp, reverse=True)
        self._version_list.clear()
        for entry in self._versions:
            item_text = "{}  ({})".format(
                entry.name, entry.timestamp.strftime("%Y-%m-%d %H:%M")
            )
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, entry) # type: ignore
            self._version_list.addItem(item)

    def _on_version_selected(self, current, previous):
        """Handle version selection change.

        Args:
            current: The newly selected list item.
            previous: The previously selected item (may be None).

        """
        if current is not None:
            entry = current.data(QtCore.Qt.ItemDataRole.UserRole) # type: ignore
            if isinstance(entry, VersionEntry):
                self._show_version_info(entry)
                self._apply_button.setEnabled(True)
        else:
            self._diff_text.clear()
            self._apply_button.setEnabled(False)

    def _show_version_info(self, entry: VersionEntry) -> None:
        """Display information about a selected version.

        Args:
            entry: The selected VersionEntry.

        """
        lines = [
            f"Version: {entry.name}",
            "Date: {}".format(entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")),
            f"Packages ({len(entry.packages)}):",
        ]
        for pkg in entry.packages[:50]:  # Limit display
            lines.append(f"  - {pkg}")
        if len(entry.packages) > 50:
            lines.append(f"  ... and {len(entry.packages) - 50} more")

        self._diff_text.setPlainText("\n".join(lines))

    def _on_apply(self) -> None:
        """Handle apply button click."""
        current = self._version_list.currentItem()
        if current is not None:
            entry = current.data(QtCore.Qt.ItemDataRole.UserRole) # type: ignore
            if isinstance(entry, VersionEntry):
                self.version_selected.emit(entry.name)

    def show_diff(self, diff: PackageDiff) -> None:
        """Display a package diff in the viewer.

        Args:
            diff: PackageDiff instance showing added/removed/changed packages.

        """
        lines = []
        if diff.added:
            lines.append("Added:")
            for pkg in diff.added:
                lines.append(f"  + {pkg}")
        if diff.removed:
            lines.append("\nRemoved:")
            for pkg in diff.removed:
                lines.append(f"  - {pkg}")
        if diff.changed:
            lines.append("\nChanged:")
            for pkg in diff.changed:
                lines.append(f"  ~ {pkg}")

        self._diff_text.setPlainText("\n".join(lines) if lines else "No changes.")
