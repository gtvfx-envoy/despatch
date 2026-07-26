"""despatch — System tray GUI frontend for the envoy runtime."""

__version__ = "0.1.0"

# Core components
from . import (
    _app_store,
    _cache_manager,
    _checkpoint_dialog,
    _config,
    _custom_stack_picker,
    _error_dialog,
    _features_browser,
    _main_window,
    _session,
    _stack,
    _tray_icon,
)

__all__ = [
    "__version__",
    "_app_store",
    "_cache_manager",
    "_checkpoint_dialog",
    "_config",
    "_custom_stack_picker",
    "_error_dialog",
    "_features_browser",
    "_main_window",
    "_session",
    "_stack",
    "_tray_icon",
]
