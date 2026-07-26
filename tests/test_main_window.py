from pathlib import Path

from despatch import _main_window, _models


def makeSnapshot():
    application = _models.ApplicationEntry(
        stable_id="gt:test:app",
        application_id="app",
        bundle_id="gt:test",
        name="Test App",
        command="test_app",
        args=(),
        description="A test application",
        icon_path=None,
        group_id="gt:test:tools",
        keywords=(),
        in_terminal=False,
        order=0,
        source_path=Path("despatch.json"),
    )
    group = _models.CatalogGroup("gt:test:tools", "Tools", 0, "gt:test")
    return _models.CatalogSnapshot("studio", (application,), (group,), ())


def testSingleClickRequestsLaunch(qapp):
    window = _main_window.MainWindow()
    window.setCatalog(makeSnapshot(), frozenset(), ())
    application_item = window._application_list.item(1)
    received = []
    window.launchRequested.connect(
        lambda stable_id, in_terminal: received.append((stable_id, in_terminal))
    )

    window._onItemClicked(application_item)
    qapp.processEvents()

    assert received == [("gt:test:app", False)]
    window.allowClose()
    window.close()


def testCloseHidesToTray(qapp):
    window = _main_window.MainWindow()
    window.show()
    qapp.processEvents()

    window.close()
    qapp.processEvents()

    assert not window.isVisible()
    window.allowClose()
    window.close()


def testSearchEnterLaunchesFirstMatch(qapp):
    window = _main_window.MainWindow()
    window.setCatalog(makeSnapshot(), frozenset(), ())
    window._search_input.setText("test")
    received = []
    window.launchRequested.connect(
        lambda stable_id, in_terminal: received.append((stable_id, in_terminal))
    )

    window._search_input.returnPressed.emit()
    qapp.processEvents()

    assert received == [("gt:test:app", False)]
    window.allowClose()
    window.close()
