"""Main application window for envoy_despatch."""


from . import _app_store, _constants, _icons, _qt, _session, _stack

QtWidgets = _qt.QtWidgets
QtCore = _qt.QtCore
QtGui = _qt.QtGui


class MainWindow(QtWidgets.QMainWindow):
    """Main application window for envoy_despatch.

    Provides the primary interface for browsing and launching applications,
    switching stacks, and accessing advanced features.

    Args:
        session: Session instance managing state.

    """

    def __init__(self, session: _session.Session):
        super().__init__()
        self._session = session
        self._setupUi()
        self._connectSignals()
        self._refreshUi()

    def _setupUi(self) -> None:
        """Initialize the user interface components."""
        self.setWindowTitle(
            f"{_constants.PRODUCT_NAME} [{self._session.stack_type.display_name}]"
        )
        self.setMinimumSize(_constants.DEFAULT_WINDOW_WIDTH, _constants.DEFAULT_WINDOW_HEIGHT)
        self.resize(800, 600)

        # Central widget with vertical layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(4)

        # Top bar with stack chooser and search
        top_bar = QtWidgets.QWidget()
        top_layout = QtWidgets.QHBoxLayout(top_bar)
        top_layout.setContentsMargins(0, 0, 0, 4)

        # stack combobox
        self._stack_combo = QtWidgets.QComboBox()
        self._stack_combo.setMinimumWidth(200)
        top_layout.addWidget(self._stack_combo, 0)

        # Search field
        self._search_input = QtWidgets.QLineEdit()
        self._search_input.setPlaceholderText("Search applications...")
        self._search_input.setMaximumWidth(300)
        top_layout.addWidget(self._search_input, 1)

        # Time Machine button
        self._time_machine_btn = QtWidgets.QPushButton("Time Machine")
        self._time_machine_btn.setToolTip("Browse stack history")
        top_layout.addWidget(self._time_machine_btn)

        # Features button (only for production stacks)
        self._features_btn = QtWidgets.QPushButton("Features")
        self._features_btn.setToolTip("Manage development features")
        if not isinstance(self._session.stack_type, _stack.ProductionStack):
            self._features_btn.setEnabled(False)
        top_layout.addWidget(self._features_btn)

        main_layout.addWidget(top_bar)

        # Application list
        self._app_list = QtWidgets.QListWidget()
        self._app_list.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self._app_list.itemDoubleClicked.connect(self._onAppDoubleClicked)
        main_layout.addWidget(self._app_list, 1)

        # Status bar
        self._status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_label = QtWidgets.QLabel("")
        self._status_bar.addPermanentWidget(self._status_label)

    def _connectSignals(self) -> None:
        """Connect UI signals to slots."""
        self._stack_combo.currentTextChanged.connect(self._onStackChanged)
        self._search_input.textChanged.connect(self._onSearchChanged)
        self._time_machine_btn.clicked.connect(self._showTimeMachine)
        self._features_btn.clicked.connect(self._showFeaturesBrowser)

    def _refreshUi(self) -> None:
        """Refresh the UI with current session state."""
        # Update window title
        stack_name = self._session.stack_type.display_name
        self.setWindowTitle(f"{_constants.PRODUCT_NAME} [{stack_name}]")

        # Populate stack combobox
        self._stack_combo.clear()
        for stack in self._session.all_stacks:
            icon = _icons.loadIcon(stack.icon) if stack.icon else QtGui.QIcon()
            self._stack_combo.addItem(icon, stack.name)

        # Set current stack
        current_idx = self._stack_combo.findText(self._session.active_stack_name or "")
        if current_idx >= 0:
            self._stack_combo.setCurrentIndex(current_idx)

        # Refresh application list
        self._refreshAppList()

    def _refreshAppList(self) -> None:
        """Refresh the application list based on current search query."""
        self._app_list.clear()
        store = self._session.app_store
        query = self._search_input.text().strip()

        if query:
            apps = store.search(query)
        else:
            # Show all apps, sorted by favorites then used then alphabetical
            apps = sorted(
                store.entries,
                key=lambda e: (not e.favorite, not e.used, e.name.lower()),
            )

        for app in apps:
            item = QtWidgets.QListWidgetItem()
            icon = _icons.loadIcon(app.icon) if app.icon else QtGui.QIcon()
            item.setIcon(icon)
            item.setText(app.name)
            tooltip_parts = [app.command]
            if app.description:
                tooltip_parts.append(app.description)
            item.setToolTip(" | ".join(tooltip_parts))
            item.setData(QtCore.Qt.ItemDataRole.UserRole, app)
            self._app_list.addItem(item)

    def _onStackChanged(self, stack_name: str) -> None:
        """Handle stack selection change."""
        if stack_name != self._session.active_stack_name:
            self._session.setStack(stack_name, explicit=True)
            self._refreshUi()

    def _onSearchChanged(self, query: str) -> None:
        """Handle search text change."""
        self._refreshAppList()

    def _onAppDoubleClicked(self, item: QtWidgets.QListWidgetItem) -> None:
        """Handle application double-click to launch."""
        app = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if app:
            self._session.launch(app.command, app.args, label=app.name)
            if not self._session.config.keep_window_open_on_launch:
                self.hide()

    def _showTimeMachine(self) -> None:
        """Show the Time Machine dialog."""
        from . import _checkpoint_dialog
        dlg = _checkpoint_dialog.CheckpointDialog(self._session, parent=self)
        dlg.exec_()

    def _showFeaturesBrowser(self) -> None:
        """Show the Features browser dialog."""
        from . import _features_browser
        dlg = _features_browser.FeaturesBrowserDialog(self._session, parent=self)
        dlg.exec_()

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        """Handle right-click context menu on application list."""
        menu = QtWidgets.QMenu(self)

        # Get the app under cursor
        item = self._app_list.itemAt(event.pos())
        if item:
            app = item.data(QtCore.Qt.ItemDataRole.UserRole)
            if app:
                # Favorite/unfavorite action
                if app.favorite:
                    unfav_action = menu.addAction("Remove from favorites")
                    unfav_action.triggered.connect(
                        lambda: self._toggleFavorite(app, False)
                    )
                else:
                    fav_action = menu.addAction("Add to favorites")
                    fav_action.triggered.connect(
                        lambda: self._toggleFavorite(app, True)
                    )

                menu.addSeparator()

                # Run in terminal action
                term_action = menu.addAction("Run in terminal")
                term_action.triggered.connect(
                    lambda: self._session.launch(
                        app.command, app.args, label=app.name, in_terminal=True
                    )
                )

                # Copy command action
                copy_action = menu.addAction("Copy command")
                copy_action.triggered.connect(
                    lambda: self._copyCommand(app)
                )

        menu.exec_(event.globalPos())

    def _toggleFavorite(self, app: _app_store.ApplicationEntry, is_favorite: bool) -> None:
        """Toggle favorite status for an application."""
        app.favorite = is_favorite
        # In a full implementation, save to config
        self._refreshAppList()

    def _copyCommand(self, app: _app_store.ApplicationEntry) -> None:
        """Copy the launch command to clipboard."""
        clipboard = QtWidgets.QApplication.clipboard()
        cmd = "envoy {} {}".format(app.command, " ".join(app.args))
        clipboard.setText(cmd)
