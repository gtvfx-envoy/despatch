"""Command-line entry point for the Despatch tray application."""

from __future__ import annotations

import argparse
import sys

from Qt import QtCore, QtWidgets

from . import (
    __version__,
    _application,
    _constants,
    _documentation,
    _icons,
    _launch_worker,
    _log,
    _single_instance,
)


def _parseArgs(arguments: list[str] | None = None) -> argparse.Namespace:
    """Parse Despatch command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="despatch",
        description=_constants.PRODUCT_DESCRIPTION,
    )
    parser.add_argument("--popup", action="store_true", help="Show the launcher on startup")
    parser.add_argument("--docs", action="store_true", help="Open the Despatch documentation")
    parser.add_argument("--settings", help="Use an alternate settings JSON file")
    parser.add_argument("--log-directory", help="Write rotating logs to this directory")
    parser.add_argument(
        "--log-level",
        default="ERROR",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Console and file logging threshold",
    )
    parser.add_argument(
        "--launch-worker",
        nargs=2,
        metavar=("REQUEST_PATH", "RESULT_PATH"),
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--docs-server",
        metavar="READY_PATH",
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--version", action="version", version=__version__)
    return parser.parse_args(arguments)


def _createApplication() -> QtWidgets.QApplication:
    """Create and configure the shared Qt application."""
    if int(QtCore.qVersion().partition(".")[0]) < 6:
        high_dpi_attribute = getattr(QtCore.Qt, "AA_EnableHighDpiScaling", None)
        if high_dpi_attribute is not None:
            QtWidgets.QApplication.setAttribute(high_dpi_attribute, True)
    application = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    application.setApplicationName(_constants.PRODUCT_NAME)
    application.setApplicationVersion(__version__)
    application.setOrganizationName(_constants.ORGANIZATION_NAME)
    application.setOrganizationDomain(_constants.ORGANIZATION_DOMAIN)
    application.setWindowIcon(_icons.loadProductIcon())  # type: ignore
    application.setQuitOnLastWindowClosed(False)  # type: ignore
    return application  # type: ignore


def main(arguments: list[str] | None = None) -> int:
    """Run Despatch or its internal packaged launch worker."""
    args = _parseArgs(arguments)
    if args.launch_worker is not None:
        return _launch_worker.main(args.launch_worker)
    if args.docs_server is not None:
        return _documentation.serveDocumentation(args.docs_server)
    _log.setupLogging(args.log_level, args.log_directory)
    if args.docs:
        try:
            _documentation.openDocumentation()
        except _documentation.DocumentationError as error:
            print(f"Unable to open Despatch documentation: {error}", file=sys.stderr)
            return 1
        return 0
    application = _createApplication()
    single_instance = _single_instance.SingleInstance()
    if not single_instance.acquireOrNotify():
        return 0
    coordinator = _application.DespatchApplication(
        application,
        single_instance,
        settings_path=args.settings,
    )
    application.aboutToQuit.connect(coordinator.quit)
    coordinator.start(popup=args.popup)
    return int(application.exec())


if __name__ == "__main__":
    raise SystemExit(main())
