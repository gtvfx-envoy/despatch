"""Qt application coordinator for Despatch."""

from __future__ import annotations

import dataclasses
import logging
import sys
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from typing import Any

from Qt import QtCore, QtWidgets

from . import (
    _catalog,
    _envoy_gateway,
    _error_dialog,
    _main_window,
    _models,
    _platform,
    _settings,
    _settings_dialog,
    _single_instance,
    _theme,
    _tray_icon,
)

_LOG = logging.getLogger("despatch.application")


class DespatchApplication(QtCore.QObject):
    """Coordinate the window, tray, Envoy services, and background work."""

    def __init__(
        self,
        application: QtWidgets.QApplication,
        single_instance: _single_instance.SingleInstance,
        settings_path: Path | str | None = None,
        gateway: _envoy_gateway.EnvoyGateway | None = None,
    ):
        super().__init__()
        self._application = application
        self._single_instance = single_instance
        self._settings = _settings.SettingsStore(settings_path)
        self._gateway = gateway or _envoy_gateway.EnvoyGateway()
        self._catalog_loader = _catalog.CatalogLoader(self._gateway)
        self._window = _main_window.MainWindow()
        self._tray_icon = _tray_icon.DespatchTrayIcon(self)
        self._autostart = _platform.AutostartService(self._settings.settings_path.parent)
        self._global_shortcut = _platform.WindowsGlobalShortcut(application)
        self._executor = ThreadPoolExecutor(max_workers=8, thread_name_prefix="despatch")
        self._pending: list[
            tuple[Future, Callable[[Any], None], Callable[[BaseException], None]]
        ] = []
        self._poll_timer = QtCore.QTimer(self)
        self._poll_timer.setInterval(50)
        self._poll_timer.timeout.connect(self._pollFutures)
        self._poll_timer.start()
        self._snapshot = _models.CatalogSnapshot(None, (), (), ())
        self._applications: dict[str, _models.ApplicationEntry] = {}
        self._configurations: tuple[_models.NamedConfiguration, ...] = ()
        self._configuration_name: str | None = None
        self._launching: set[str] = set()
        self._error_dialogs: list[_error_dialog.ErrorDialog] = []
        self._quitting = False
        self._connectSignals()

    @property
    def window(self) -> _main_window.MainWindow:
        """Primary launcher window."""
        return self._window

    def start(self, popup: bool = False) -> None:
        """Start the tray application and load its first catalog.

        Args:
            popup: Show the main launcher immediately.

        """
        _theme.applyTheme(self._application, self._settings.theme)
        self._restoreGeometry()
        try:
            envoy_version = self._gateway.preflight()
            _LOG.info("Using Envoy %s with Python %s", envoy_version, sys.version.split()[0])
        except _envoy_gateway.EnvoyUnavailableError as error:
            self._window.setError(str(error))
            _LOG.error("Envoy preflight failed: %s", error)
        self._configureGlobalShortcut(
            self._settings.global_shortcut_enabled,
            self._settings.global_shortcut,
            report_error=False,
        )
        self._tray_icon.show()
        self.refreshCatalog()
        if popup:
            self.showWindow()

    def showWindow(self) -> None:
        """Show and focus the main launcher."""
        self._window.showLauncher()

    def refreshCatalog(self) -> None:
        """Refresh configurations and application manifests asynchronously."""
        self._window.setLoading("Refreshing Envoy catalog…")
        self._submit(self._loadState, self._onStateLoaded, self._onCatalogError)

    def quit(self) -> None:
        """Persist window state and stop the tray process."""
        if self._quitting:
            return
        self._quitting = True
        try:
            geometry = bytes(self._window.saveGeometry().toBase64()).decode("ascii")
            self._settings.setWindowGeometry(geometry)
        except (OSError, TypeError, ValueError) as error:
            _LOG.warning("Unable to save window geometry: %s", error)
        self._global_shortcut.unregister()
        self._single_instance.close()
        self._tray_icon.hide()
        self._window.allowClose()
        self._window.close()
        self._poll_timer.stop()
        self._executor.shutdown(wait=False, cancel_futures=True)
        self._application.quit()

    def _connectSignals(self) -> None:
        """Connect view requests to coordinator operations."""
        self._single_instance.activationRequested.connect(self.showWindow)
        self._global_shortcut.activated.connect(self.showWindow)

        self._window.launchRequested.connect(self._launchApplication)
        self._window.favoriteToggleRequested.connect(self._toggleFavorite)
        self._window.copyRequested.connect(self._copyCommand)
        self._window.configurationRequested.connect(self._switchConfiguration)
        self._window.refreshRequested.connect(self.refreshCatalog)
        self._window.settingsRequested.connect(self._showSettings)

        self._tray_icon.showRequested.connect(self.showWindow)
        self._tray_icon.launchRequested.connect(self._launchApplication)
        self._tray_icon.configurationRequested.connect(self._switchConfiguration)
        self._tray_icon.refreshRequested.connect(self.refreshCatalog)
        self._tray_icon.settingsRequested.connect(self._showSettings)
        self._tray_icon.quitRequested.connect(self.quit)

    def _loadState(
        self,
    ) -> tuple[
        tuple[_models.NamedConfiguration, ...],
        str | None,
        _models.CatalogSnapshot,
    ]:
        """Load all state required for an atomic UI refresh."""
        configurations = self._gateway.listConfigurations()
        configuration_name = self._gateway.getCurrentConfigurationName()
        snapshot = self._catalog_loader.loadCatalog()
        return configurations, configuration_name, snapshot

    def _onStateLoaded(
        self,
        state: tuple[
            tuple[_models.NamedConfiguration, ...],
            str | None,
            _models.CatalogSnapshot,
        ],
    ) -> None:
        """Atomically apply refreshed Envoy state."""
        self._configurations, self._configuration_name, self._snapshot = state
        self._applications = self._snapshot.applicationMap()
        self._window.setConfigurations(self._configurations, self._configuration_name)
        self._refreshViews()
        diagnostic_count = len(self._snapshot.diagnostics)
        if diagnostic_count:
            suffix = "issue" if diagnostic_count == 1 else "issues"
            self._window.setReady(f"Loaded with {diagnostic_count} manifest {suffix}")
            for diagnostic in self._snapshot.diagnostics:
                _LOG.warning("%s: %s", diagnostic.source_path or "catalog", diagnostic.message)
        else:
            self._window.setReady()

    def _onCatalogError(self, error: BaseException) -> None:
        """Preserve prior state and surface a refresh failure."""
        message = str(error) or error.__class__.__name__
        self._window.setError(message)
        self._tray_icon.showMessage("Despatch could not refresh", message)
        _LOG.error("Catalog refresh failed", exc_info=(type(error), error, error.__traceback__))

    def _switchConfiguration(self, configuration_name: str | None) -> None:
        """Persist a selected Envoy configuration in the background."""
        if configuration_name == self._configuration_name:
            return
        label = configuration_name or "automatic discovery"
        self._window.setLoading(f"Switching to {label}…")

        def on_success(unused_result: Any) -> None:
            self.refreshCatalog()

        self._submit(
            lambda: self._gateway.switchConfiguration(configuration_name),
            on_success,
            self._onCatalogError,
        )

    def _launchApplication(self, stable_id: str, force_terminal: bool) -> None:
        """Prepare and spawn a catalog application asynchronously."""
        application = self._applications.get(stable_id)
        if application is None or stable_id in self._launching:
            return
        if force_terminal and not application.in_terminal:
            application = dataclasses.replace(application, in_terminal=True)
        self._launching.add(stable_id)
        self._window.setReady(f"Starting {application.name}…")

        def on_spawned(unused_process: Any) -> None:
            self._launching.discard(stable_id)
            self._settings.recordLaunch(stable_id)
            self._refreshViews()
            self._window.setReady(f"Started {application.name}")
            if not self._settings.keep_open_after_launch:
                self._window.hide()

        def on_error(error: BaseException) -> None:
            self._launching.discard(stable_id)
            self._window.setError(f"Could not start {application.name}: {error}")
            self.showWindow()
            self._showErrorDialog(
                f"Could not start {application.name}",
                str(error) or error.__class__.__name__,
            )

        self._submit(lambda: self._gateway.spawnApplication(application), on_spawned, on_error)

    def _toggleFavorite(self, stable_id: str) -> None:
        """Toggle a favorite and refresh both launch surfaces."""
        if stable_id not in self._applications:
            return
        self._settings.toggleFavorite(stable_id)
        self._refreshViews()

    def _copyCommand(self, stable_id: str) -> None:
        """Copy a platform-quoted Envoy command to the clipboard."""
        application = self._applications.get(stable_id)
        if application is None:
            return
        self._application.clipboard().setText(self._gateway.formatCommand(application))
        self._window.setReady("Envoy command copied")

    def _showSettings(self) -> None:
        """Show settings and apply accepted changes transactionally."""
        dialog = _settings_dialog.SettingsDialog(
            self._settings,
            autostart_supported=self._autostart.is_supported,
            shortcut_supported=sys.platform == "win32",
            parent=self._window,
        )
        if dialog.exec_() != QtWidgets.QDialog.Accepted:
            return
        values = dialog.values()
        old_autostart = self._settings.autostart
        old_shortcut_enabled = self._settings.global_shortcut_enabled
        old_shortcut = self._settings.global_shortcut
        try:
            requested_autostart = bool(values["autostart"])
            if requested_autostart != old_autostart:
                self._autostart.setEnabled(requested_autostart)
            self._configureGlobalShortcut(
                bool(values["global_shortcut_enabled"]),
                str(values["global_shortcut"]),
                report_error=True,
            )
            self._settings.updatePreferences(**values)
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            if bool(values["autostart"]) != old_autostart:
                try:
                    self._autostart.setEnabled(old_autostart)
                except (OSError, RuntimeError):
                    _LOG.exception("Unable to roll back autostart state")
            self._configureGlobalShortcut(
                old_shortcut_enabled,
                old_shortcut,
                report_error=False,
            )
            self._showErrorDialog("Settings could not be saved", str(error))
            return
        _theme.applyTheme(self._application, self._settings.theme)
        self._refreshViews()

    def _configureGlobalShortcut(
        self,
        enabled: bool,
        shortcut: str,
        *,
        report_error: bool,
    ) -> bool:
        """Apply the requested global shortcut registration."""
        try:
            self._global_shortcut.unregister()
            if enabled:
                self._global_shortcut.register(shortcut)
            return True
        except RuntimeError as error:
            if report_error:
                raise
            _LOG.warning("Global shortcut unavailable: %s", error)
            return False

    def _refreshViews(self) -> None:
        """Refresh main and tray views from one state snapshot."""
        self._window.setCatalog(
            self._snapshot,
            self._settings.favorites,
            self._settings.recent_applications,
        )
        self._tray_icon.setState(
            self._snapshot,
            self._configurations,
            self._configuration_name,
            self._settings.favorites,
        )

    def _showErrorDialog(self, title: str, message: str, output: str = "") -> None:
        """Create a retained non-modal error dialog."""
        dialog = _error_dialog.ErrorDialog(title, message, output, self._window)
        self._error_dialogs.append(dialog)
        dialog.destroyed.connect(
            lambda unused=None, error_dialog=dialog: self._forgetDialog(error_dialog)
        )
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

    def _forgetDialog(self, dialog: _error_dialog.ErrorDialog) -> None:
        """Release a deleted non-modal error dialog."""
        if dialog in self._error_dialogs:
            self._error_dialogs.remove(dialog)

    def _restoreGeometry(self) -> None:
        """Restore persisted Qt geometry when it is valid."""
        if not self._settings.window_geometry:
            return
        try:
            encoded = self._settings.window_geometry.encode("ascii")
            geometry = QtCore.QByteArray.fromBase64(encoded)
            self._window.restoreGeometry(geometry)
        except (TypeError, ValueError):
            _LOG.warning("Ignoring invalid persisted window geometry")

    def _submit(
        self,
        function: Callable[[], Any],
        on_success: Callable[[Any], None],
        on_error: Callable[[BaseException], None],
    ) -> None:
        """Submit background work for polling on the Qt thread."""
        future = self._executor.submit(function)
        self._pending.append((future, on_success, on_error))

    def _pollFutures(self) -> None:
        """Dispatch completed future callbacks on the Qt main thread."""
        for pending in tuple(self._pending):
            future, on_success, on_error = pending
            if not future.done():
                continue
            self._pending.remove(pending)
            try:
                result = future.result()
            except BaseException as error:
                on_error(error)
            else:
                on_success(result)
