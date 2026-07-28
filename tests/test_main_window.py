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
        group_id="tools",
        keywords=(),
        in_terminal=False,
        order=0,
        source_path=Path("despatch.json"),
    )
    group = _models.CatalogGroup("tools", "Tools", 0, "gt:test")
    stack_state = _models.StackState(
        _models.StackMode.EXPLICIT,
        _models.StackSelection("studio", "studio", Path("studio.estack")),
    )
    return _models.CatalogSnapshot(stack_state, (application,), (group,), ())


def testCustomStackSelectorShowsFilenameAndPath(qapp, tmp_path):
    window = _main_window.MainWindow()
    stack_path = (tmp_path / "my_stack.estack").resolve()
    stack_state = _models.StackState(
        _models.StackMode.EXPLICIT,
        _models.StackSelection(
            str(stack_path),
            stack_path.name,
            stack_path,
            is_custom=True,
        ),
    )

    window.setStacks((), stack_state)

    assert window._stack_combo.currentText() == "my_stack.estack"
    assert window._stack_combo.toolTip() == str(stack_path)
    assert window._stack_combo.property("customStack") is True
    window.allowClose()
    window.close()


def testAutomaticStackSelectionIsRequestable(qapp):
    window = _main_window.MainWindow()
    stack_state = _models.StackState(_models.StackMode.PROMPT)
    received = []
    window.stackRequested.connect(received.append)
    window.setStacks((), stack_state)

    window._stack_combo.setCurrentIndex(1)
    qapp.processEvents()

    assert received == [None]
    window.allowClose()
    window.close()


def testCustomStackPickerRestoresActiveSelection(qapp):
    window = _main_window.MainWindow()
    stack = _models.NamedStack("studio", "2026-01-01", Path("studio.estack"))
    stack_state = _models.StackState(
        _models.StackMode.EXPLICIT,
        _models.StackSelection("studio", "studio", stack.path),
    )
    received = []
    window.customStackRequested.connect(lambda: received.append(True))
    window.setStacks((stack,), stack_state)
    active_index = window._stack_combo.currentIndex()

    window._stack_combo.setCurrentIndex(window._custom_picker_index)
    qapp.processEvents()

    assert received == [True]
    assert window._stack_combo.currentIndex() == active_index
    window.allowClose()
    window.close()


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


def testDocumentationButtonRequestsHelp(qapp):
    window = _main_window.MainWindow()
    received = []
    window.documentationRequested.connect(lambda: received.append(True))

    window._documentation_button.click()
    qapp.processEvents()

    assert received == [True]
    assert window._documentation_button.accessibleName() == "Documentation"
    window.allowClose()
    window.close()


def testLauncherDoesNotExposeRefreshControl(qapp):
    window = _main_window.MainWindow()

    tooltips = {
        button.toolTip() for button in window.findChildren(_main_window.QtWidgets.QToolButton)
    }

    assert "Refresh catalog" not in tooltips
    assert not hasattr(window, "_refresh_button")
    window.allowClose()
    window.close()
