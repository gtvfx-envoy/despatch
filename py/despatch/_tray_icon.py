"""System tray entry point and compact quick-access menu."""

from __future__ import annotations

from Qt import QtCore, QtWidgets

from . import _constants
from . import _icons
from . import _models


def _activationReason(reason_name: str):
    """Return a tray activation enum across Qt versions."""
    direct_value = getattr(QtWidgets.QSystemTrayIcon, reason_name, None)
    if direct_value is not None:
        return direct_value
    return getattr(QtWidgets.QSystemTrayIcon.ActivationReason, reason_name)


class DespatchTrayIcon(QtWidgets.QSystemTrayIcon):
    """Expose Despatch through asymmetric left- and right-click behavior."""

    showRequested = QtCore.Signal()
    launchRequested = QtCore.Signal(str, bool)
    configurationRequested = QtCore.Signal(object)
    refreshRequested = QtCore.Signal()
    settingsRequested = QtCore.Signal()
    quitRequested = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(_icons.loadProductIcon(), parent)
        self._snapshot = _models.CatalogSnapshot(None, (), (), ())
        self._configuration_name: str | None = None
        self._configurations: tuple[_models.NamedConfiguration, ...] = ()
        self._favorites: frozenset[str] = frozenset()
        self.activated.connect(self._onActivated)
        self.setToolTip(_constants.PRODUCT_DESCRIPTION)
        self.rebuildMenu()

    def setState(
        self,
        snapshot: _models.CatalogSnapshot,
        configurations: tuple[_models.NamedConfiguration, ...],
        configuration_name: str | None,
        favorites: frozenset[str],
    ) -> None:
        """Update tray favorites and configuration actions."""
        self._snapshot = snapshot
        self._configurations = configurations
        self._configuration_name = configuration_name
        self._favorites = favorites
        config_label = configuration_name or "Automatic discovery"
        self.setToolTip(f"{_constants.PRODUCT_NAME} · {config_label}")
        self.rebuildMenu()

    def rebuildMenu(self) -> None:
        """Rebuild the compact native context menu from current state."""
        existing_menu = self.contextMenu()
        if existing_menu is not None:
            existing_menu.deleteLater()
        menu = QtWidgets.QMenu()

        show_action = menu.addAction("Show Despatch")
        show_action.setIcon(_icons.loadProductIcon())
        show_action.triggered.connect(self.showRequested)

        favorite_applications = [
            application
            for application in self._snapshot.applications
            if application.stable_id in self._favorites
        ]
        if favorite_applications:
            menu.addSeparator()
            for application in favorite_applications:
                action = menu.addAction(
                    _icons.loadPathIcon(application.icon_path),
                    application.name,
                )
                action.triggered.connect(
                    lambda checked=False, stable_id=application.stable_id: (
                        self.launchRequested.emit(stable_id, False)
                    )
                )

        menu.addSeparator()
        configuration_menu = menu.addMenu(self._configuration_name or "Automatic discovery")
        automatic_action = configuration_menu.addAction("Automatic discovery")
        automatic_action.setCheckable(True)
        automatic_action.setChecked(self._configuration_name is None)
        automatic_action.triggered.connect(
            lambda checked=False: self.configurationRequested.emit(None)
        )
        if self._configurations:
            configuration_menu.addSeparator()
        for configuration in self._configurations:
            action = configuration_menu.addAction(configuration.name)
            action.setCheckable(True)
            action.setChecked(configuration.name == self._configuration_name)
            action.triggered.connect(
                lambda checked=False, config_name=configuration.name: (
                    self.configurationRequested.emit(config_name)
                )
            )

        refresh_action = menu.addAction("Refresh")
        refresh_action.triggered.connect(self.refreshRequested)
        settings_action = menu.addAction("Settings")
        settings_action.triggered.connect(self.settingsRequested)
        menu.addSeparator()
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(self.quitRequested)
        self.setContextMenu(menu)

    def _onActivated(self, reason) -> None:
        """Show the main UI only for a left-click activation."""
        if reason == _activationReason("Trigger"):
            self.showRequested.emit()
