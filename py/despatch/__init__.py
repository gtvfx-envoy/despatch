"""envoy_despatch — System tray GUI frontend for the envoy runtime."""

__version__ = "0.1.0"

# Core components
from . import _session, _tray_icon, _main_window
from . import _config, _app_store, _stack
from . import _cache_manager, _checkpoint_dialog
from . import _features_browser, _error_dialog, _custom_stack_picker

__all__ = [
    "__version__",
    "_session",
    "_tray_icon",
    "_main_window",
    "_config",
    "_app_store",
    "_stack",
    "_cache_manager",
    "_checkpoint_dialog",
    "_features_browser",
    "_error_dialog",
    "_custom_stack_picker",
]

