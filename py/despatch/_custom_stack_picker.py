"""Custom stack picker for envoy_despatch."""

import os

from . import _qt, _session

QtWidgets = _qt.QtWidgets
QtCore = _qt.QtCore
QtGui = _qt.QtGui


class CustomStackPickerDialog(QtWidgets.QDialog):
    """Dialog for selecting and managing custom stack configuration files.

    Allows users to browse and select .json stack config files, with a list
    of recently used custom stacks for quick access.

    Args:
        session: Session instance for context.
        parent: Parent QWidget. Defaults to None.

    """

    def __init__(self, session: _session.Session, parent=None):
        super().__init__(parent)
        self._session = session
        self.setWindowTitle("Custom stack")
        self.setMinimumSize(500, 400)
        self._setupUi()
        self._loadRecentStacks()

    def _setupUi(self) -> None:
        """Initialize the dialog UI."""
        layout = QtWidgets.QVBoxLayout(self)

        # Header
        header = QtWidgets.QWidget()
        header_layout = QtWidgets.QHBoxLayout(header)
        header_label = QtWidgets.QLabel("Custom stack")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        layout.addWidget(header)

        # Recent stacks list
        self._recent_list = QtWidgets.QListWidget()
        self._recent_list.itemDoubleClicked.connect(self._onStackSelected)
        layout.addWidget(self._recent_list, 1)

        # Browse button
        browse_btn = QtWidgets.QPushButton("Browse...")
        browse_btn.clicked.connect(self._browseFile)
        layout.addWidget(browse_btn)

        # Bottom buttons
        btn_layout = QtWidgets.QHBoxLayout()
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn, 1)
        layout.addLayout(btn_layout)

    def _loadRecentStacks(self) -> None:
        """Load recent custom stacks into the list."""
        self._recent_list.clear()
        
        recent = self._session.config.recent_custom_stacks
        
        if not recent:
            placeholder = QtWidgets.QListWidgetItem("[No recent custom stacks]")
            placeholder.setEnabled(False) # type: ignore
            self._recent_list.addItem(placeholder)
        else:
            for path in recent:
                filename = os.path.basename(path)
                item = QtWidgets.QListWidgetItem(filename)
                item.setToolTip(path)
                item.setData(QtCore.Qt.ItemDataRole.UserRole, path)
                self._recent_list.addItem(item)

    def _onStackSelected(self, item: QtWidgets.QListWidgetItem) -> None:
        """Handle stack selection from the recent list."""
        path = item.data(QtCore.Qt.ItemDataRole.UserRole)
        
        if path and os.path.exists(path):
            # In a full implementation, this would load and activate the custom stack
            QtWidgets.QMessageBox.information(
                self,
                "Custom stack",
                f"Loaded custom stack: {path}\n\n"
                "(This requires integration with the envoy backend.)",
            )
            self.close()
        else:
            QtWidgets.QMessageBox.warning(
                self,
                "Error",
                f"File not found: {path}",
            )

    def _browseFile(self) -> None:
        """Open a file browser to select a custom stack config."""
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select Custom stack",
            "",
            "stack Config (*.json);;All Files (*)",
        )
        
        if filepath:
            # Add to recent list
            self._session.config.addRecentCustomStack(filepath)
            
            # In a full implementation, this would load and activate the custom stack
            QtWidgets.QMessageBox.information(
                self,
                "Custom stack",
                f"Loaded custom stack: {filepath}\n\n"
                "(This requires integration with the envoy backend.)",
            )
            self.close()
