"""Qt binding resolver for envoy despatch.

Uses envoy's existing Qt.py shim at gt/ext/qtshim to resolve the appropriate
Qt binding (PySide6, PyQt5/6, etc.) at runtime. Do NOT ship a custom version;
use this existing one from the envoy environment.

This module provides convenient access to Qt modules through the resolved binding.
"""

import os
import sys

# Add envoy's qtshim to path if not already present
_qtshim_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "ext", "qtshim", "prebuilt"
)
if _qtshim_path not in sys.path:
    sys.path.insert(0, _qtshim_path)

# Import Qt.py which resolves the binding
import Qt  # type: ignore

# Re-export commonly used modules for convenience
QtWidgets = Qt.QtWidgets
QtCore = Qt.QtCore
QtGui = Qt.QtGui
QtNetwork = Qt.QtNetwork

__all__ = ["QtWidgets", "QtCore", "QtGui", "QtNetwork"]
