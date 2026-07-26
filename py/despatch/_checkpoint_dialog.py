"""Time Machine dialog for envoy_despatch stack version rollback."""

import datetime

from Qt import QtWidgets

from . import _session


class CheckpointDialog(QtWidgets.QDialog):
    """Dialog for browsing and selecting stack versions via Time Machine.

    Allows users to select past versions of the active stack for temporary
    use (24-hour expiration), with option to browse full history.

    Args:
        session: Session instance for context.
        parent: Parent QWidget. Defaults to None.

    """

    def __init__(self, session: _session.Session, parent=None):
        super().__init__(parent)
        self._session = session
        self.setWindowTitle("Time Machine")
        self.setMinimumSize(600, 400)
        self._setupUi()
        self._loadRecentVersions()

    def _setupUi(self) -> None:
        """Initialize the dialog UI."""
        layout = QtWidgets.QVBoxLayout(self)

        # Header with current stack info
        header = QtWidgets.QWidget()
        header_layout = QtWidgets.QHBoxLayout(header)
        header_label = QtWidgets.QLabel("Time Machine")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        layout.addWidget(header)

        # Recent versions list
        self._version_list = QtWidgets.QListWidget()
        self._version_list.itemDoubleClicked.connect(self._onVersionSelected)
        layout.addWidget(self._version_list, 1)

        # Browse all button
        browse_btn = QtWidgets.QPushButton("Browse All Versions...")
        browse_btn.clicked.connect(self._showFullHistory)
        layout.addWidget(browse_btn)

        # Bottom buttons
        btn_layout = QtWidgets.QHBoxLayout()
        reset_btn = QtWidgets.QPushButton("Reset to Latest")
        reset_btn.clicked.connect(self._resetToLatest)
        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def _loadRecentVersions(self) -> None:
        """Load recent stack versions into the list."""
        self._version_list.clear()
        
        # In a full implementation, this would query the envoy backend for
        # recent stack versions. For now, show placeholder items.
        placeholder = QtWidgets.QListWidgetItem(
            "No version history available (placeholder)"
        )
        # placeholder.setEnabled(False)  # type: ignore
        self._version_list.addItem(placeholder)

    def _onVersionSelected(self, item: QtWidgets.QListWidgetItem) -> None:
        """Handle version selection from the list."""
        version_name = item.text()
        
        # Set Time Machine expiration to 24 hours from now
        expiration = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=24)
        self._session.config.time_machine_expiration = expiration.isoformat()
        
        # In a full implementation, this would switch the stack to the selected version
        QtWidgets.QMessageBox.information(
            self,
            "Time Machine",
            "Switched to version: {}\nExpires at: {}".format(
                version_name,
                expiration.strftime("%Y-%m-%d %H:%M"),
            ),
        )
        self.close()

    def _showFullHistory(self) -> None:
        """Show the full version history with package diffs."""
        # In a full implementation, this would open a detailed dialog showing
        # all versions and their package changes. For now, show a message.
        QtWidgets.QMessageBox.information(
            self,
            "Full History",
            "Full version history with package diffs would be displayed here.\n\n"
            "(This feature requires integration with the envoy backend.)",
        )

    def _resetToLatest(self) -> None:
        """Reset to the latest stack version."""
        self._session.config.time_machine_expiration = None
        
        # In a full implementation, this would switch back to the latest version
        QtWidgets.QMessageBox.information(
            self,
            "Time Machine",
            "Reset to latest version.",
        )
        self.close()
