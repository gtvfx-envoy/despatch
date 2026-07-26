"""Despatch preference editor."""

from __future__ import annotations

from Qt import QtWidgets

from . import _settings


class SettingsDialog(QtWidgets.QDialog):
    """Edit user-facing launcher preferences.

    Args:
        settings: Current settings store.
        autostart_supported: Whether login startup can be enabled.
        shortcut_supported: Whether global shortcuts can be enabled.
        parent: Parent widget.

    """

    def __init__(
        self,
        settings: _settings.SettingsStore,
        autostart_supported: bool,
        shortcut_supported: bool,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Despatch settings")
        self.setModal(True)
        self.setMinimumWidth(440)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        heading = QtWidgets.QLabel("Settings")
        heading.setObjectName("productTitle")
        layout.addWidget(heading)

        form_layout = QtWidgets.QFormLayout()
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(14)

        self._theme_combo = QtWidgets.QComboBox()
        self._theme_combo.addItem("Follow system", "system")
        self._theme_combo.addItem("Light", "light")
        self._theme_combo.addItem("Dark", "dark")
        theme_index = self._theme_combo.findData(settings.theme)
        self._theme_combo.setCurrentIndex(max(theme_index, 0))
        form_layout.addRow("Appearance", self._theme_combo)

        self._keep_open_check = QtWidgets.QCheckBox("Keep launcher open after starting an app")
        self._keep_open_check.setChecked(settings.keep_open_after_launch)
        form_layout.addRow("", self._keep_open_check)

        self._autostart_check = QtWidgets.QCheckBox("Start when I sign in")
        self._autostart_check.setChecked(settings.autostart)
        self._autostart_check.setEnabled(autostart_supported)
        form_layout.addRow("", self._autostart_check)

        shortcut_widget = QtWidgets.QWidget()
        shortcut_layout = QtWidgets.QHBoxLayout(shortcut_widget)
        shortcut_layout.setContentsMargins(0, 0, 0, 0)
        shortcut_layout.setSpacing(8)
        self._shortcut_check = QtWidgets.QCheckBox("Enable")
        self._shortcut_check.setChecked(settings.global_shortcut_enabled)
        self._shortcut_check.setEnabled(shortcut_supported)
        self._shortcut_input = QtWidgets.QKeySequenceEdit()
        self._shortcut_input.setKeySequence(settings.global_shortcut)
        self._shortcut_input.setEnabled(shortcut_supported and settings.global_shortcut_enabled)
        self._shortcut_check.toggled.connect(self._shortcut_input.setEnabled)
        shortcut_layout.addWidget(self._shortcut_check)
        shortcut_layout.addWidget(self._shortcut_input, 1)
        form_layout.addRow("Global shortcut", shortcut_widget)

        layout.addLayout(form_layout)

        note = QtWidgets.QLabel(
            "Configuration changes affect Envoy globally. Application favorites and history "
            "are stored only by Despatch."
        )
        note.setObjectName("mutedLabel")
        note.setWordWrap(True)
        layout.addWidget(note)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self) -> dict[str, object]:
        """Return the current editor values.

        Returns:
            Keyword arguments accepted by SettingsStore.updatePreferences.

        """
        return {
            "theme": str(self._theme_combo.currentData()),
            "keep_open_after_launch": self._keep_open_check.isChecked(),
            "autostart": self._autostart_check.isChecked(),
            "global_shortcut_enabled": self._shortcut_check.isChecked(),
            "global_shortcut": self._shortcut_input.keySequence().toString(),
        }
