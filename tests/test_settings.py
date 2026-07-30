import json

import pytest

from despatch import _settings, _settings_dialog


def testSettingsRoundTrip(tmp_path):
    settings_path = tmp_path / "settings.json"
    store = _settings.SettingsStore(settings_path)

    assert store.toggleFavorite("gt:test:app") is True
    store.recordLaunch("gt:test:app")
    store.updatePreferences(
        theme="dark",
        keep_open_after_launch=True,
        autostart=False,
        global_shortcut_enabled=True,
        global_shortcut="Ctrl+Alt+K",
        stack_refresh_interval_seconds=600,
    )

    reloaded = _settings.SettingsStore(settings_path)
    assert reloaded.favorites == frozenset({"gt:test:app"})
    assert reloaded.recent_applications == ("gt:test:app",)
    assert reloaded.theme == "dark"
    assert reloaded.keep_open_after_launch is True
    assert reloaded.global_shortcut == "Ctrl+Alt+K"
    assert reloaded.stack_refresh_interval_seconds == 600


def testInvalidSettingsFallBackToDefaults(tmp_path):
    settings_path = tmp_path / "settings.json"
    settings_path.write_text("{not json", encoding="utf-8")

    store = _settings.SettingsStore(settings_path)

    assert store.theme == "system"
    assert not store.favorites
    assert store.stack_refresh_interval_seconds == 300


def testLoadedListsAreDeduplicated(tmp_path):
    settings_path = tmp_path / "settings.json"
    settings_path.write_text(
        json.dumps(
            {
                "favorites": ["one", "one", "two"],
                "recentApplications": ["two", "two", "one"],
            }
        ),
        encoding="utf-8",
    )

    store = _settings.SettingsStore(settings_path)

    assert store.favorites == frozenset({"one", "two"})
    assert store.recent_applications == ("two", "one")


@pytest.mark.parametrize("interval_seconds", [30, 90, 3601, True])
def testInvalidStackRefreshIntervalsAreRejected(tmp_path, interval_seconds):
    store = _settings.SettingsStore(tmp_path / "settings.json")

    with pytest.raises(ValueError, match="whole number from 1 to 60 minutes"):
        store.updatePreferences(
            theme="system",
            keep_open_after_launch=False,
            autostart=False,
            global_shortcut_enabled=False,
            global_shortcut="Ctrl+Alt+Space",
            stack_refresh_interval_seconds=interval_seconds,
        )


def testSettingsDialogReturnsStackRefreshInterval(qapp, tmp_path):
    store = _settings.SettingsStore(tmp_path / "settings.json")
    dialog = _settings_dialog.SettingsDialog(store, True, True)

    dialog._stack_refresh_spin.setValue(15)

    assert dialog.values()["stack_refresh_interval_seconds"] == 900
    dialog.close()
