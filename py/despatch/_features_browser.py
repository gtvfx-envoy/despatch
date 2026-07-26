"""Features browser for envoy_despatch development feature management."""


from . import _qt, _session

QtWidgets = _qt.QtWidgets
QtCore = _qt.QtCore
QtGui = _qt.QtGui


class FeatureEntry:
    """Represents a development feature that can be activated.

    Args:
        name: Display name of the feature.
        description: Human-readable description.
        packages: List of package names affected by this feature.
        active: Whether this feature is currently active.

    """

    def __init__(
        self,
        name: str,
        description: str = "",
        packages: list[str] | None = None,
        active: bool = False,
    ):
        self.name = name
        self.description = description
        self.packages = packages or []
        self.active = active


class FeaturesBrowserDialog(QtWidgets.QDialog):
    """Dialog for browsing and managing development features.

    Allows users to activate/deactivate features that overlay on top of the
    current stack, enabling testing of in-development software.

    Args:
        session: Session instance for context.
        parent: Parent QWidget. Defaults to None.

    """

    def __init__(self, session: _session.Session, parent=None):
        super().__init__(parent)
        self._session = session
        self.setWindowTitle("Features Browser")
        self.setMinimumSize(700, 500)
        self._setup_ui()
        self._load_features()

    def _setupUi(self) -> None:
        """Initialize the dialog UI."""
        layout = QtWidgets.QVBoxLayout(self)

        # Header
        header = QtWidgets.QWidget()
        header_layout = QtWidgets.QHBoxLayout(header)
        header_label = QtWidgets.QLabel("Development Features")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        layout.addWidget(header)

        # Feature list
        self._feature_list = QtWidgets.QListWidget()
        self._feature_list.itemDoubleClicked.connect(self._onFeatureToggled)
        layout.addWidget(self._feature_list, 1)

        # Feature details (shown when a feature is selected)
        self._details_label = QtWidgets.QLabel("")
        self._details_label.setWordWrap(True)
        self._details_label.setStyleSheet("padding: 8px; background: #f0f0f0;")
        layout.addWidget(self._details_label)

        # Bottom buttons
        btn_layout = QtWidgets.QHBoxLayout()
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn, 1)
        layout.addLayout(btn_layout)

        # Connect selection change to show details
        self._feature_list.currentItemChanged.connect(self._onItemChanged)

    def _loadFeatures(self) -> None:
        """Load available features into the list."""
        self._feature_list.clear()
        
        # In a full implementation, this would query the envoy backend for
        # available features. For now, show placeholder items.
        placeholder = QtWidgets.QListWidgetItem("[No features available]")
        placeholder.setEnabled(False)
        self._feature_list.addItem(placeholder)

    def _onFeatureToggled(self, item: QtWidgets.QListWidgetItem) -> None:
        """Handle feature activation/deactivation."""
        feature_name = item.text()
        
        # In a full implementation, this would toggle the feature state
        # and overlay the feature's packages on the current stack
        QtWidgets.QMessageBox.information(
            self,
            "Feature",
            "Feature '{}' {}.\n\n"
            "(This requires integration with the envoy backend.)".format(
                feature_name,
                "activated" if not item.data(QtCore.Qt.ItemDataRole.UserRole) else "deactivated",
            ),
        )

    def _onItemChanged(self, current: QtWidgets.QListWidgetItem | None, previous) -> None:
        """Handle list item selection change to show feature details."""
        if current:
            current.text()
            # In a full implementation, load and display feature details
            self._details_label.setText(
                "Select a feature to view its details.\n\n"
                "(Feature details require integration with the envoy backend.)"
            )
        else:
            self._details_label.clear()
