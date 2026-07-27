from types import SimpleNamespace

from despatch import _application, _models


def testDevModeRequiresExactTrimmedOne(monkeypatch):
    monkeypatch.delenv("ENVOY_DEV_MODE", raising=False)
    assert _application._isDevModeEnabled() is False

    monkeypatch.setenv("ENVOY_DEV_MODE", " 1 ")
    assert _application._isDevModeEnabled() is True

    monkeypatch.setenv("ENVOY_DEV_MODE", "true")
    assert _application._isDevModeEnabled() is False


def testManualAutomaticSelectionLastsForCurrentSession():
    operations = []
    refreshes = []
    gateway = SimpleNamespace(clearStack=lambda: operations.append("clear"))
    coordinator = SimpleNamespace(
        _stack_state=_models.StackState(_models.StackMode.PROMPT),
        _window=SimpleNamespace(setLoading=lambda message: None),
        _gateway=gateway,
        _dev_mode=False,
        _automatic_resolution_requested=False,
        _onStackSwitchError=lambda error: None,
        refreshCatalog=lambda: refreshes.append(True),
    )
    coordinator._submit = lambda operation, on_success, on_error: on_success(operation())

    _application.DespatchApplication._switchStack(coordinator, None)

    assert operations == ["clear"]
    assert coordinator._automatic_resolution_requested is True
    assert refreshes == [True]


def testExplicitSelectionRestoresConfiguredDefault():
    operations = []
    gateway = SimpleNamespace(switchStack=lambda value: operations.append(value))
    coordinator = SimpleNamespace(
        _stack_state=_models.StackState(_models.StackMode.AUTOMATIC),
        _window=SimpleNamespace(setLoading=lambda message: None),
        _gateway=gateway,
        _dev_mode=False,
        _automatic_resolution_requested=True,
        _onStackSwitchError=lambda error: None,
        refreshCatalog=lambda: None,
    )
    coordinator._submit = lambda operation, on_success, on_error: on_success(operation())

    _application.DespatchApplication._switchStack(coordinator, "studio")

    assert operations == ["studio"]
    assert coordinator._automatic_resolution_requested is False


def testCancelingCustomStackPickerPreservesSelection(monkeypatch):
    switch_requests = []
    coordinator = SimpleNamespace(
        _stack_state=_models.StackState(_models.StackMode.PROMPT),
        _window=None,
        _switchStack=switch_requests.append,
    )
    monkeypatch.setattr(
        _application.QtWidgets.QFileDialog,
        "getOpenFileName",
        lambda *args: ("", "Envoy Stack (*.estack)"),
    )

    _application.DespatchApplication._chooseCustomStack(coordinator)

    assert switch_requests == []
