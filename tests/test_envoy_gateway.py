import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from despatch import _envoy_gateway, _launch_worker, _models


class FakeUserConfig:
    def __init__(self, values=None):
        self.values = values or {}
        self.saved = False

    def get(self, key):
        return self.values.get(key)

    def set(self, key, value):
        self.values[key] = value

    def unset(self, key):
        return self.values.pop(key, None) is not None

    def save(self):
        self.saved = True


def makeEnvoyModule(tmp_path, user_values=None):
    values = {"stack": "studio"} if user_values is None else user_values
    user_config = FakeUserConfig(values)
    stack_path = tmp_path / "studio.estack"
    stack_path.write_text("name: studio\nbundles: []\n", encoding="utf-8")

    class FakeStack:
        def __init__(self, path):
            self.path = Path(path)
            self.bundles = []

    return SimpleNamespace(
        __version__="test",
        Stack=FakeStack,
        discoverBundlesAuto=lambda: [],
        isStackName=lambda value: (
            "/" not in value
            and "\\" not in value
            and ":" not in value
            and not value.startswith(".")
            and not value.endswith(".estack")
        ),
        listNamedStacks=lambda: [
            SimpleNamespace(name="studio", version="2026-01-01", path=stack_path)
        ],
        loadUserConfig=lambda: user_config,
        proc=SimpleNamespace(),
        resolveNamedStack=lambda name: stack_path if name == "studio" else None,
        stack_path=stack_path,
        user_config=user_config,
    )


def makeApplication(in_terminal=False):
    return _models.ApplicationEntry(
        stable_id="gt:test:app",
        application_id="app",
        bundle_id="gt:test",
        name="Test App",
        command="test_app",
        args=("--example",),
        description="",
        icon_path=None,
        group_id="",
        keywords=(),
        in_terminal=in_terminal,
        order=0,
        source_path=Path("despatch.json"),
    )


def explicitState(stack_path, persisted_value="studio", is_custom=False):
    selection = _models.StackSelection(
        persisted_value,
        stack_path.name if is_custom else persisted_value,
        stack_path,
        is_custom=is_custom,
    )
    return _models.StackState(_models.StackMode.EXPLICIT, selection)


def testPreflightRequiresStackApi(tmp_path):
    envoy_module = makeEnvoyModule(tmp_path)
    gateway = _envoy_gateway.EnvoyGateway(envoy_module)

    assert gateway.preflight() == "test"

    del envoy_module.Stack
    with pytest.raises(_envoy_gateway.EnvoyUnavailableError, match="Stack"):
        gateway.preflight()


def testListsAndSwitchesNamedStack(tmp_path):
    envoy_module = makeEnvoyModule(tmp_path)
    gateway = _envoy_gateway.EnvoyGateway(envoy_module)

    stacks = gateway.listStacks()
    selection = gateway.switchStack("studio")

    assert stacks[0].name == "studio"
    assert selection.path == envoy_module.stack_path.resolve()
    assert envoy_module.user_config.saved is True
    assert envoy_module.user_config.values["stack"] == "studio"


def testAutomaticResolutionUnsetsStack(tmp_path):
    envoy_module = makeEnvoyModule(tmp_path)
    gateway = _envoy_gateway.EnvoyGateway(envoy_module)

    gateway.clearStack()

    assert "stack" not in envoy_module.user_config.values
    assert envoy_module.user_config.saved is True


def testSavedStackWinsOverAutomaticDefault(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STACK", str(tmp_path / "ambient.estack"))
    gateway = _envoy_gateway.EnvoyGateway(makeEnvoyModule(tmp_path))

    stack_state = gateway.getStackState(automatic_requested=True)

    assert stack_state.mode == _models.StackMode.EXPLICIT
    assert stack_state.selection is not None
    assert stack_state.selection.persisted_value == "studio"


def testMissingStackUsesRequestedFallbackMode(tmp_path):
    gateway = _envoy_gateway.EnvoyGateway(makeEnvoyModule(tmp_path, {}))

    prompt_state = gateway.getStackState(automatic_requested=False)
    automatic_state = gateway.getStackState(automatic_requested=True)

    assert prompt_state.mode == _models.StackMode.PROMPT
    assert automatic_state.mode == _models.StackMode.AUTOMATIC


def testCustomStackPersistsCanonicalPath(tmp_path):
    envoy_module = makeEnvoyModule(tmp_path, {})
    custom_path = tmp_path / "custom.estack"
    custom_path.write_text("name: custom\nbundles: []\n", encoding="utf-8")
    gateway = _envoy_gateway.EnvoyGateway(envoy_module)

    selection = gateway.switchStack(str(custom_path))

    assert selection.is_custom is True
    assert selection.display_name == "custom.estack"
    assert envoy_module.user_config.values["stack"] == str(custom_path.resolve())


def testRegisteredStackPathNormalizesToName(tmp_path):
    envoy_module = makeEnvoyModule(tmp_path, {})
    gateway = _envoy_gateway.EnvoyGateway(envoy_module)

    selection = gateway.switchStack(str(envoy_module.stack_path))

    assert selection.is_custom is False
    assert selection.persisted_value == "studio"
    assert envoy_module.user_config.values["stack"] == "studio"


def testRejectsCustomStackWithoutEstackExtension(tmp_path):
    envoy_module = makeEnvoyModule(tmp_path, {})
    invalid_path = tmp_path / "invalid.yaml"
    invalid_path.write_text("name: invalid\nbundles: []\n", encoding="utf-8")
    gateway = _envoy_gateway.EnvoyGateway(envoy_module)

    with pytest.raises(_envoy_gateway.StackSwitchError, match=r"\.estack"):
        gateway.switchStack(str(invalid_path))


def testAutomaticModeUsesFullEnvoyDiscovery(tmp_path):
    envoy_module = makeEnvoyModule(tmp_path, {})
    discovery_calls = []

    def discoverBundles():
        discovery_calls.append(True)
        return []

    envoy_module.discoverBundlesAuto = discoverBundles
    gateway = _envoy_gateway.EnvoyGateway(envoy_module)

    bundles = gateway.loadBundles(_models.StackState(_models.StackMode.AUTOMATIC))

    assert bundles == ()
    assert discovery_calls == [True]


def testPromptModeDoesNotDiscoverBundles(tmp_path):
    envoy_module = makeEnvoyModule(tmp_path, {})
    envoy_module.discoverBundlesAuto = lambda: pytest.fail("Discovery should not run")
    gateway = _envoy_gateway.EnvoyGateway(envoy_module)

    bundles = gateway.loadBundles(_models.StackState(_models.StackMode.PROMPT))

    assert bundles == ()


def testLaunchWorkerUsesEnvoyProcSubprocess(tmp_path):
    envoy_module = makeEnvoyModule(tmp_path)
    process = SimpleNamespace(pid=987)
    spawn_calls = []

    def spawnApplication(command_line, **options):
        spawn_calls.append((command_line, options))
        return process

    envoy_module.proc = SimpleNamespace(spawn=spawnApplication)

    gui_process_id = _launch_worker.launchApplication(
        {
            "commandLine": ["test_app", "--example"],
            "inTerminal": False,
            "stackPath": None,
        },
        envoy_module,
    )
    terminal_process_id = _launch_worker.launchApplication(
        {
            "commandLine": ["test_app", "--example"],
            "inTerminal": True,
            "stackPath": None,
        },
        envoy_module,
    )
    explicit_process_id = _launch_worker.launchApplication(
        {
            "commandLine": ["test_app", "--example"],
            "inTerminal": False,
            "stackPath": str(envoy_module.stack_path.resolve()),
        },
        envoy_module,
    )

    assert gui_process_id == 987
    assert terminal_process_id == 987
    assert explicit_process_id == 987
    assert spawn_calls[0] == (
        ["test_app", "--example"],
        {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0)},
    )
    assert spawn_calls[1] == (
        ["test_app", "--example"],
        {"creationflags": getattr(subprocess, "CREATE_NEW_CONSOLE", 0)},
    )
    assert spawn_calls[2] == (
        ["--stack", str(envoy_module.stack_path.resolve()), "test_app", "--example"],
        {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0)},
    )


def testGatewayUsesIsolatedLaunchWorker(tmp_path, monkeypatch):
    envoy_module = makeEnvoyModule(tmp_path)
    gateway = _envoy_gateway.EnvoyGateway(envoy_module)
    invocation = {}

    def runWorker(command_line, **options):
        invocation["commandLine"] = command_line
        invocation["options"] = options
        request_path = Path(command_line[-2])
        result_path = Path(command_line[-1])
        invocation["request"] = json.loads(request_path.read_text(encoding="utf-8"))
        result_path.write_text('{"processId": 654}', encoding="utf-8")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(_envoy_gateway.subprocess, "run", runWorker)

    stack_state = explicitState(envoy_module.stack_path.resolve())
    process_id = gateway.spawnApplication(makeApplication(), stack_state)

    assert process_id == 654
    assert invocation["commandLine"][1:3] == ["-m", "despatch._launch_worker"]
    assert invocation["request"] == {
        "commandLine": ["test_app", "--example"],
        "inTerminal": False,
        "stackPath": str(envoy_module.stack_path.resolve()),
    }
    assert invocation["options"]["check"] is False
