import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

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


def makeEnvoyModule(tmp_path):
    user_config = FakeUserConfig({"bundles_config": "studio"})
    config_path = tmp_path / "studio.json"
    config_path.write_text("{}", encoding="utf-8")

    class FakeBundleConfig:
        def __init__(self, path):
            self.path = path
            self.bundles = []

    return SimpleNamespace(
        __version__="test",
        BundleConfig=FakeBundleConfig,
        discoverBundlesAuto=lambda: [],
        getCurrentBundleConfig=lambda: None,
        isConfigName=lambda value: "/" not in value and "\\" not in value,
        listNamedConfigs=lambda: [
            SimpleNamespace(name="studio", version="2026-01-01", path=config_path)
        ],
        loadUserConfig=lambda: user_config,
        proc=SimpleNamespace(),
        resolveNamedConfig=lambda name: config_path if name == "studio" else None,
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


def testListsAndSwitchesNamedConfiguration(tmp_path):
    envoy_module = makeEnvoyModule(tmp_path)
    gateway = _envoy_gateway.EnvoyGateway(envoy_module)

    configurations = gateway.listConfigurations()
    gateway.switchConfiguration("studio")

    assert configurations[0].name == "studio"
    assert envoy_module.user_config.saved is True
    assert envoy_module.user_config.values["bundles_config"] == "studio"


def testSwitchToAutomaticDiscoveryUnsetsConfig(tmp_path):
    envoy_module = makeEnvoyModule(tmp_path)
    gateway = _envoy_gateway.EnvoyGateway(envoy_module)

    gateway.switchConfiguration(None)

    assert "bundles_config" not in envoy_module.user_config.values


def testLaunchWorkerUsesEnvoyProcSubprocess(tmp_path):
    envoy_module = makeEnvoyModule(tmp_path)
    process = SimpleNamespace(pid=987)
    spawn_calls = []

    def spawnApplication(command_line, **options):
        spawn_calls.append((command_line, options))
        return process

    envoy_module.proc = SimpleNamespace(spawn=spawnApplication)

    gui_process_id = _launch_worker.launchApplication(
        {"commandLine": ["test_app", "--example"], "inTerminal": False},
        envoy_module,
    )
    terminal_process_id = _launch_worker.launchApplication(
        {"commandLine": ["test_app", "--example"], "inTerminal": True},
        envoy_module,
    )

    assert gui_process_id == 987
    assert terminal_process_id == 987
    assert spawn_calls[0] == (
        ["test_app", "--example"],
        {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0)},
    )
    assert spawn_calls[1] == (
        ["test_app", "--example"],
        {"creationflags": getattr(subprocess, "CREATE_NEW_CONSOLE", 0)},
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

    process_id = gateway.spawnApplication(makeApplication())

    assert process_id == 654
    assert invocation["commandLine"][1:3] == ["-m", "despatch._launch_worker"]
    assert invocation["request"] == {
        "commandLine": ["test_app", "--example"],
        "inTerminal": False,
    }
    assert invocation["options"]["check"] is False
