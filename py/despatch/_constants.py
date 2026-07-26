"""Constants and branding configuration for envoy_despatch."""

import os

# Product identity
PRODUCT_NAME = "envoy_despatch"
PRODUCT_VERSION = "0.1.0"
PRODUCT_DESCRIPTION = "System tray launcher for the envoy runtime"

# Icon states for the system tray icon
ICON_STATES = {
    "default": "default.svg",
    "refreshing": "refreshing.svg",
    "caching": "caching.svg",
    "checkpoint": "checkpoint.svg",
}

# Default window size
DEFAULT_WINDOW_WIDTH = 600
DEFAULT_WINDOW_HEIGHT = 500

# Search panel height when expanded
SEARCH_PANEL_HEIGHT = 300

# Time machine expiration duration (24 hours in seconds)
TIME_MACHINE_EXPIRATION_SECONDS = 86400

# Cache directory for despatch data
if "APPDATA" in os.environ:
    DEFAULT_DATA_DIR = os.path.join(os.environ["APPDATA"], "envoy_despatch")
else:
    DEFAULT_DATA_DIR = os.path.join(os.path.expanduser("~"), ".envoy_despatch")

DEFAULT_CONFIG_PATH = os.path.join(DEFAULT_DATA_DIR, "config.json")
DEFAULT_LOG_DIR = os.path.join(DEFAULT_DATA_DIR, "logs")

# Supported operating systems (matching bl convention)
SUPPORTED_OPERATING_SYSTEMS = ["windows", "macos", "linux"]

# Default stack mode
STACK_MODE_CLASSIC = "classic"
STACK_MODE_HIDDEN = "hidden"

# Keyboard shortcuts
KEYBOARD_SHORTCUTS = {
    "quick_set_stack": "Ctrl+P",
    "search_focus": "Ctrl+F",
    "launch_selected": "Return",
    "cancel_operation": "Escape",
}
