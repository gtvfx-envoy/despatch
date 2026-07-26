"""System tray icon and context menu for envoy_despatch."""

import datetime
from typing import Optional

from . import _qt
from . import _session, _config, _icons, _constants, _app_store

QtWidgets = _qt.QtWidgets
QtCore = _qt.QtCore
QtGui = _qt.QtGui


class DespatchTrayIcon(QtWidgets.QSystemTrayIcon):
    """System tray icon for envoy_despatch.

    Manages the system tray icon with dynamic context menu, four icon states,
    and integration with the session orchestrator.

    Args:
        parent: Parent QWidget. Defaults to None.

    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._session = _session.getSession()
        self.setIcon(_icons.loadIcon(_constants.ICON_STATES["default"]))
        self.activated.connect(self._onActivated)

    def rebuildContextMenu(self) -> None:
        """Rebuild the context menu from current session state."""
        existing = self.contextMenu()
        if existing:
            existing.hide()
            existing.deleteLater()

        context_menu = QtWidgets.QMenu()

        # stack switcher submenu
        self._stack_menu = context_menu.addMenu(
            self._session.stack_type.display_name
        )
        self._stack_menu.setIcon(_icons.loadIcon("default"))
        self._stack_menu.aboutToShow.connect(self._populateStackMenu)

        # Show menu action
        show_action = context_menu.addAction("Show menu")
        show_action.triggered.connect(self._session.popupMainWindow)

        # Favorites section
        if self._session.config.active_stack:
            store = _app_store.ApplicationStore.fromStack(
                self._session.stack_type
            )
        else:
            store = _app_store.ApplicationStore([])

        favorites = [a for a in store.applications if a.favorite]
        context_menu.addSeparator()

        for fav_app in favorites:
            action = context_menu.addAction(fav_app.name)
            # Use lambda to capture the command and args at connection time
            cmd = fav_app.command
            args = fav_app.args
            action.triggered.connect(
                lambda c=cmd, a=args: self._session.launch(c, a)
            )

        if not favorites:
            add_fav_action = context_menu.addAction("Add favorites")
            add_fav_action.setEnabled(False)

        # Control actions
        context_menu.addSeparator()

        refresh_action = context_menu.addAction("Refresh")
        refresh_action.triggered.connect(self._session.refresh)

        restart_action = context_menu.addAction("Restart")
        restart_action.triggered.connect(self._session.restart)

        about_action = context_menu.addAction("About")
        about_action.triggered.connect(self._showAbout)

        exit_action = context_menu.addAction("Exit")
        exit_action.triggered.connect(self._session.quit)

        self.setContextMenu(context_menu)

    def _populateStackMenu(self) -> None:
        """Populate the stack submenu with available stacks."""
        if self._stack_menu.actions():
            return  # Already populated

        session = self._session
        current_stack = session.config.active_stack

        # Show favorite stacks first
        fav_stacks = [
            p for p in session.all_stacks
            if p.name in session.config.favorite_stacks
            and p.name != current_stack
        ]

        for stack in fav_stacks:
            action = self._stack_menu.addAction(
                "{} {}".format(_icons.HEART_ICON, stack.name)
            )
            action.triggered.connect(
                session.setStack(stack.name, explicit=False)
            )

        if fav_stacks:
            self._stack_menu.addSeparator()

        # Show all stacks grouped by attribute
        for group_name, stacks in session.groupedStacks():
            if group_name and any(p.name != current_stack for p in stacks):
                if self._stack_menu.actions():
                    self._stack_menu.addSeparator()
                header = QtWidgets.QWidgetAction(self._stack_menu)
                label = QtWidgets.QLabel(group_name, self._stack_menu)
                label.setStyleSheet("font-weight: bold; padding: 4px;")
                header.setDefaultWidget(label)
                self._stack_menu.addAction(header)

            for stack in stacks:
                if stack.name != current_stack:
                    action = self._stack_menu.addAction(stack.name)
                    if stack.is_inactive:
                        action.setText("{} {}".format(_icons.PADLOCK_ICON, stack.name))
                    action.triggered.connect(
                        session.setStack(stack.name, explicit=False)
                    )

    def setIconState(self, state: str) -> None:
        """Update the tray icon and tooltip based on current state.

        Args:
            state: One of "default", "refreshing", "caching", "checkpoint".

        """
        icon_path = _constants.ICON_STATES.get(state, _constants.ICON_STATES["default"])
        self.setIcon(_icons.loadIcon(icon_path))
        self.updateTooltip(state)

    def updateTooltip(self, state: Optional[str] = None) -> None:
        """Update the tray icon tooltip.

        Args:
            state: Icon state to format tooltip for. Defaults to current state.

        """
        if state is None:
            icon = self.icon()
            for key, path in _constants.ICON_STATES.items():
                if icon.pixmap(24, 24).isNull() or str(icon) == str(_icons.loadIcon(path)):
                    state = key
                    break

        session = self._session
        if state == "checkpoint" and session.config.time_machine_expiration:
            dt = datetime.datetime.fromisoformat(session.config.time_machine_expiration)
            tooltip = "Time Machine until {}".format(
                dt.strftime("%Y-%m-%d %H:%M")
            )
        else:
            stack_name = session.stack_type.display_name
            tooltip = "{} [{}]".format(_constants.PRODUCT_NAME, stack_name)

        self.setToolTip(tooltip)

    def _onActivated(self, reason: QtWidgets.QSystemTrayIcon.ActivationReason) -> None:
        """Handle tray icon activation (left click)."""
        if reason == QtWidgets.QSystemTrayIcon.ActivationReason.Trigger:
            self._session.popupMainWindow()

    def _showAbout(self) -> None:
        """Show the about dialog."""
        msg = (
            "<b>{}</b><br/>"
            "Version: {}<br/>"
            "{}"
        ).format(
            _constants.PRODUCT_NAME,
            _constants.PRODUCT_VERSION,
            self._session.stack_type.display_name,
        )
        QtWidgets.QMessageBox.about(self, "About {}".format(_constants.PRODUCT_NAME), msg)


# Icon constants for UI elements
HEART_ICON = "\u2665"  # Heart symbol
PADLOCK_ICON = "\U0001F512"  # Padlock emoji

