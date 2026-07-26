"""Entry point for envoy_despatch."""

import argparse
import os
import sys


def _parseArgs():
    """Parse command-line arguments.

    Returns:
        Parsed argument namespace.

    """
    parser = argparse.ArgumentParser(
        prog="despatch",
        description="System tray frontend for the envoy runtime.",
    )
    parser.add_argument(
        "-d", "--dev", action="store_true",
        help="Run in development mode (no auto-restart, suppress output suppression)",
    )
    parser.add_argument(
        "--popup", action="store_true",
        help="Show the main search window on startup",
    )
    parser.add_argument(
        "--config", default=None,
        help="Path to a custom configuration file",
    )
    parser.add_argument(
        "--log-directory", default=None,
        help="Write application logs to the specified directory",
    )
    parser.add_argument(
        "--log-level", default="ERROR", choices=["DEBUG", "INFO", "WARN", "ERROR"],
        help="Console log level (default: ERROR)",
    )
    return parser.parse_args()


def _setupApp():
    """Initialize the Qt application with despatch-specific settings.

    Returns:
        The QApplication instance.

    """
    from . import __version__, _icons, _log, _qt

    QtWidgets = _qt.QtWidgets
    log = _log.get_logger(__name__)

    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)

    app.setApplicationName("envoy_despatch")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("gtvfx-contrib")
    app.setOrganizationDomain("gtvfx-contrib.github.io")

    # Set high-DPI support
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    # Apply stylesheet
    style_path = os.path.join(_icons.get_resources_dir(), "style.qss")
    if os.path.exists(style_path):
        with open(style_path, "r") as f:
            app.setStyleSheet(f.read()) # type: ignore

    # Set application icon
    icon = _icons.load_icon("default.svg")
    if not icon.isNull():
        app.setWindowIcon(icon) # type: ignore

    log.debug("Application initialized (version %s)", __version__)
    return app


def main():
    """Main entry point for envoy_despatch."""
    from . import _config, _log, _session, _tray_icon

    args = _parseArgs()

    # Configure logging
    _log.setupLogging(level=args.log_level, log_directory=args.log_directory)
    log = _log.get_logger(__name__)

    log.info("Starting envoy_despatch")

    # Initialize Qt application
    app = _setupApp()
    log.debug("Qt application initialized")

    # Create and initialize session
    config_path = args.config
    if config_path:
        config = _config.Config(config_path)
    else:
        config = _config.Config()
    
    session = _session.Session(config=config)
    _session.Session.setInstance(session)
    log.debug("Session initialized")

    # Create and show tray icon
    tray_icon = _tray_icon.DespatchTrayIcon()
    session.tray_icon = tray_icon  # Store reference in session
    tray_icon.rebuildContextMenu()
    tray_icon.show()  # Explicitly show the tray icon
    log.info("Tray icon shown")

    # Show popup window if requested
    if args.popup:
        session.popupMainWindow()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
