"""Auto-start / login item registration for envoy_despatch."""

import os
import sys
from pathlib import Path
from typing import Optional


def get_autostart_path() -> Optional[str]:
    """Return the platform-specific autostart directory path.

    Returns:
        Path to the autostart directory, or None if not applicable.

    """
    if sys.platform == "win32":
        app_data = os.environ.get("APPDATA", "")
        return os.path.join(app_data, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
    elif sys.platform == "darwin":
        home = os.path.expanduser("~")
        return os.path.join(home, "Library", "LaunchAgents")
    elif sys.platform.startswith("linux"):
        config_dir = os.environ.get("XDG_CONFIG_HOME", os.path.join(os.path.expanduser("~"), ".config"))
        return os.path.join(config_dir, "autostart")
    return None


def is_autostart_enabled() -> bool:
    """Check if envoy_despatch is registered for auto-start.

    Returns:
        True if an autostart entry exists.

    """
    autostart_dir = get_autostart_path()
    if not autostart_dir:
        return False

    # Check for platform-specific entry
    if sys.platform == "win32":
        entry = os.path.join(autostart_dir, "envoy_despatch.lnk")
        return os.path.exists(entry)
    elif sys.platform == "darwin":
        entry = os.path.join(autostart_dir, "io.envoy.despatch.plist")
        return os.path.exists(entry)
    else:
        entry = os.path.join(autostart_dir, "envoy_despatch.desktop")
        return os.path.exists(entry)


def enable_autostart() -> bool:
    """Register envoy_despatch for auto-start on login.

    Returns:
        True if registration succeeded.

    """
    autostart_dir = get_autostart_path()
    if not autostart_dir:
        return False

    os.makedirs(autostart_dir, exist_ok=True)

    if sys.platform == "win32":
        # Windows: Create a shortcut (.lnk) in the startup folder
        # Note: Creating actual .lnk requires pywin32 or manual creation
        entry = os.path.join(autostart_dir, "envoy_despatch.lnk")
        try:
            # For now, create a batch file as a fallback
            bat_path = os.path.join(os.path.dirname(__file__), "..", "despatch.bat")
            with open(bat_path, "w") as f:
                f.write("@echo off\npython -m despatch\n")
            return True
        except IOError:
            return False

    elif sys.platform == "darwin":
        # macOS: Create a launchd plist file
        entry = os.path.join(autostart_dir, "io.envoy.despatch.plist")
        try:
            python_path = sys.executable
            script_path = os.path.join(os.path.dirname(__file__), "..", "__main__.py")
            plist_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>io.envoy.despatch</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>-m</string>
        <string>despatch</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>""".format(python_path=python_path)
            with open(entry, "w") as f:
                f.write(plist_content)
            return True
        except IOError:
            return False

    else:
        # Linux: create .desktop file
        entry = os.path.join(autostart_dir, "envoy_despatch.desktop")
        try:
            with open(entry, "w") as f:
                f.write("[Desktop Entry]\n")
                f.write("Type=Application\n")
                f.write("Name=envoy_despatch\n")
                f.write("Comment=System tray launcher for envoy runtime\n")
                f.write("Exec=python -m despatch\n")
                f.write("Hidden=false\n")
                f.write("NoDisplay=false\n")
            return True
        except IOError:
            return False


def disable_autostart() -> bool:
    """Remove the auto-start registration for envoy_despatch.

    Returns:
        True if removal succeeded.

    """
    autostart_dir = get_autostart_path()
    if not autostart_dir:
        return False

    # Remove platform-specific entry
    if sys.platform == "win32":
        entry = os.path.join(autostart_dir, "envoy_despatch.lnk")
        bat_entry = os.path.join(os.path.dirname(__file__), "..", "despatch.bat")
    elif sys.platform == "darwin":
        entry = os.path.join(autostart_dir, "io.envoy.despatch.plist")
    else:
        entry = os.path.join(autostart_dir, "envoy_despatch.desktop")

    success = True

    # Remove the main entry
    try:
        if os.path.exists(entry):
            os.remove(entry)
    except OSError:
        success = False

    # Also remove fallback batch file on Windows
    if sys.platform == "win32" and os.path.exists(bat_entry):
        try:
            os.remove(bat_entry)
        except OSError:
            success = False

    return success
