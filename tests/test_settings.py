import json

from despatch import _settings


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
    )

    reloaded = _settings.SettingsStore(settings_path)
    assert reloaded.favorites == frozenset({"gt:test:app"})
    assert reloaded.recent_applications == ("gt:test:app",)
    assert reloaded.theme == "dark"
    assert reloaded.keep_open_after_launch is True
    assert reloaded.global_shortcut == "Ctrl+Alt+K"


def testInvalidSettingsFallBackToDefaults(tmp_path):
    settings_path = tmp_path / "settings.json"
    settings_path.write_text("{not json", encoding="utf-8")

    store = _settings.SettingsStore(settings_path)

    assert store.theme == "system"
    assert not store.favorites


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
