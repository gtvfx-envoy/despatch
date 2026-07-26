import pytest
from Qt import QtWidgets


@pytest.fixture(name="qapp", scope="session")
def qtApplication():
    application = QtWidgets.QApplication.instance()
    if application is None:
        application = QtWidgets.QApplication(["despatch-tests"])
    application.setQuitOnLastWindowClosed(False)
    return application
