"""Windows-first operating-system integrations."""

from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
import sys
from collections.abc import Callable
from ctypes import wintypes
from pathlib import Path

from Qt import QtCore, QtWidgets

from . import _constants


class AutostartService:
    """Manage per-user Windows login startup."""

    def __init__(self, data_directory: Path):
        self._script_path = data_directory / "launch_despatch.vbs"

    @property
    def is_supported(self) -> bool:
        """Whether this platform supports the implementation."""
        return sys.platform == "win32"

    def isEnabled(self) -> bool:
        """Return whether the autostart registry value exists."""
        if not self.is_supported:
            return False
        import winreg

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self._registryPath()) as registry_key:
                winreg.QueryValueEx(registry_key, _constants.AUTOSTART_VALUE_NAME)
            return True
        except FileNotFoundError:
            return False

    def setEnabled(self, enabled: bool) -> None:
        """Enable or disable login startup.

        Args:
            enabled: Requested startup state.

        Raises:
            OSError: If registration cannot be changed.
            RuntimeError: If Envoy is unavailable or the platform is unsupported.

        """
        if not self.is_supported:
            if enabled:
                raise RuntimeError("Login startup is currently supported only on Windows")
            return
        if enabled:
            self._enableWindows()
        else:
            self._disableWindows()

    def _enableWindows(self) -> None:
        """Create a hidden launcher script and register it for the current user."""
        import winreg

        envoy_executable = shutil.which("envoy") or shutil.which("en")
        if not envoy_executable:
            raise RuntimeError("Envoy is not available on PATH")
        command_line = subprocess.list2cmdline([envoy_executable, "despatch"])
        vbs_command = command_line.replace('"', '""')
        script_content = (
            'Set despatchShell = CreateObject("WScript.Shell")\n'
            f'despatchShell.Run "{vbs_command}", 0, False\n'
        )
        self._script_path.parent.mkdir(parents=True, exist_ok=True)
        self._script_path.write_text(script_content, encoding="utf-8")
        registry_command = subprocess.list2cmdline(
            [
                str(Path(os.environ.get("WINDIR", "C:\\Windows")) / "System32" / "wscript.exe"),
                "//B",
                "//Nologo",
                str(self._script_path),
            ]
        )
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, self._registryPath()) as registry_key:
            winreg.SetValueEx(
                registry_key,
                _constants.AUTOSTART_VALUE_NAME,
                0,
                winreg.REG_SZ,
                registry_command,
            )

    def _disableWindows(self) -> None:
        """Remove the current user's login startup registration."""
        import winreg

        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self._registryPath(),
                0,
                winreg.KEY_SET_VALUE,
            ) as registry_key:
                winreg.DeleteValue(registry_key, _constants.AUTOSTART_VALUE_NAME)
        except FileNotFoundError:
            pass
        self._script_path.unlink(missing_ok=True)

    @staticmethod
    def _registryPath() -> str:
        """Return the Windows Run-key path."""
        return r"Software\Microsoft\Windows\CurrentVersion\Run"


class _NativeHotkeyFilter(QtCore.QAbstractNativeEventFilter):
    """Forward native Windows messages to a QObject-owned callback."""

    def __init__(self, callback: Callable[[int], None]):
        super().__init__()
        self._callback = callback

    def nativeEventFilter(self, event_type, message):
        """Forward the native message address and continue event processing."""
        self._callback(int(message))
        return False, 0


class WindowsGlobalShortcut(QtCore.QObject):
    """Register one Windows global shortcut without binding-specific imports."""

    activated = QtCore.Signal()

    _HOTKEY_ID = 0x4453
    _WM_HOTKEY = 0x0312
    _MODIFIERS = {
        "ALT": 0x0001,
        "CTRL": 0x0002,
        "SHIFT": 0x0004,
        "META": 0x0008,
        "WIN": 0x0008,
    }
    _SPECIAL_KEYS = {"SPACE": 0x20, "TAB": 0x09, "ESC": 0x1B}

    def __init__(self, application: QtWidgets.QApplication):
        super().__init__()
        self._application = application
        self._registered = False
        self._native_filter = _NativeHotkeyFilter(self._handleNativeMessage)
        self._user32 = (
            ctypes.WinDLL("user32", use_last_error=True) if sys.platform == "win32" else None
        )

    @property
    def is_registered(self) -> bool:
        """Whether a shortcut is currently registered."""
        return self._registered

    def register(self, shortcut: str) -> None:
        """Register a portable shortcut string.

        Args:
            shortcut: Combination such as Ctrl+Alt+Space.

        Raises:
            RuntimeError: If unsupported, invalid, or already owned.

        """
        self.unregister()
        if self._user32 is None:
            raise RuntimeError("Global shortcuts are currently supported only on Windows")
        modifiers, virtual_key = self._parseShortcut(shortcut)
        modifiers |= 0x4000
        if not self._user32.RegisterHotKey(None, self._HOTKEY_ID, modifiers, virtual_key):
            error_code = ctypes.get_last_error()
            raise RuntimeError(f"Shortcut '{shortcut}' is unavailable (Windows error {error_code})")
        self._application.installNativeEventFilter(self._native_filter)
        self._registered = True

    def unregister(self) -> None:
        """Release the current shortcut if registered."""
        if not self._registered:
            return
        self._application.removeNativeEventFilter(self._native_filter)
        if self._user32 is not None:
            self._user32.UnregisterHotKey(None, self._HOTKEY_ID)
        self._registered = False

    def _handleNativeMessage(self, message_address: int) -> None:
        """Emit activation for this instance's WM_HOTKEY message."""
        if sys.platform == "win32":
            native_message = wintypes.MSG.from_address(message_address)
            is_hotkey = native_message.message == self._WM_HOTKEY
            if is_hotkey and native_message.wParam == self._HOTKEY_ID:
                self.activated.emit()

    def _parseShortcut(self, shortcut: str) -> tuple[int, int]:
        """Parse the supported portable shortcut subset."""
        tokens = [token.strip().upper() for token in shortcut.split("+") if token.strip()]
        if len(tokens) < 2:
            raise RuntimeError("Global shortcuts require a modifier and a key")
        modifiers = 0
        for token in tokens[:-1]:
            if token not in self._MODIFIERS:
                raise RuntimeError(f"Unsupported shortcut modifier: {token}")
            modifiers |= self._MODIFIERS[token]
        key_token = tokens[-1]
        if len(key_token) == 1 and key_token.isalnum():
            virtual_key = ord(key_token)
        elif key_token.startswith("F") and key_token[1:].isdigit():
            function_number = int(key_token[1:])
            if not 1 <= function_number <= 24:
                raise RuntimeError(f"Unsupported shortcut key: {key_token}")
            virtual_key = 0x70 + function_number - 1
        elif key_token in self._SPECIAL_KEYS:
            virtual_key = self._SPECIAL_KEYS[key_token]
        else:
            raise RuntimeError(f"Unsupported shortcut key: {key_token}")
        return modifiers, virtual_key
