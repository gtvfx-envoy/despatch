import json

from despatch import _catalog, _models


class FakeGateway:
    def __init__(self, bundle, configuration_name="studio"):
        self.bundle = bundle
        self.configuration_name = configuration_name

    def loadBundles(self):
        return (self.bundle,)

    def getCurrentConfigurationName(self):
        return self.configuration_name


def makeBundle(tmp_path, commands=("krita",)):
    envoy_directory = tmp_path / ".envoy"
    envoy_directory.mkdir()
    return _models.BundleRecord(
        bundle_id="gt:creative",
        root=tmp_path,
        envoy_directory=envoy_directory,
        commands=commands,
    )


def writeManifest(bundle, applications, groups=None):
    manifest_data = {
        "schemaVersion": 1,
        "groups": groups or [],
        "applications": applications,
    }
    (bundle.envoy_directory / "despatch.json").write_text(
        json.dumps(manifest_data),
        encoding="utf-8",
    )


def testLoadsValidManifest(tmp_path):
    bundle = makeBundle(tmp_path)
    icon_path = bundle.root / "resources" / "icons" / "krita.svg"
    icon_path.parent.mkdir(parents=True)
    icon_path.write_text("<svg/>", encoding="utf-8")
    writeManifest(
        bundle,
        [
            {
                "id": "krita",
                "name": "Krita",
                "command": "krita",
                "description": "Paint",
                "icon": "krita.svg",
                "group": "creative",
                "keywords": ["image"],
                "platforms": ["windows"],
            }
        ],
        groups=[{"id": "creative", "name": "Creative", "order": 5}],
    )

    snapshot = _catalog.CatalogLoader(FakeGateway(bundle), "windows").loadCatalog()

    assert snapshot.configuration_name == "studio"
    assert snapshot.applications[0].stable_id == "gt:creative:krita"
    assert snapshot.applications[0].icon_path == icon_path
    assert snapshot.groups[0].stable_id == "gt:creative:creative"
    assert not snapshot.diagnostics


def testResolvesOrganizedIconBelowResourceRoot(tmp_path):
    bundle = makeBundle(tmp_path)
    icon_path = bundle.root / "resources" / "icons" / "creative" / "krita.svg"
    icon_path.parent.mkdir(parents=True)
    icon_path.write_text("<svg/>", encoding="utf-8")
    writeManifest(
        bundle,
        [
            {
                "id": "krita",
                "name": "Krita",
                "command": "krita",
                "icon": "creative/krita.svg",
            }
        ],
    )

    snapshot = _catalog.CatalogLoader(FakeGateway(bundle), "windows").loadCatalog()

    assert snapshot.applications[0].icon_path == icon_path
    assert not snapshot.diagnostics


def testSkipsUnknownCommandsAndWrongPlatform(tmp_path):
    bundle = makeBundle(tmp_path)
    writeManifest(
        bundle,
        [
            {"id": "missing", "name": "Missing", "command": "unknown"},
            {
                "id": "linux",
                "name": "Linux only",
                "command": "krita",
                "platforms": ["linux"],
            },
        ],
    )

    snapshot = _catalog.CatalogLoader(FakeGateway(bundle), "windows").loadCatalog()

    assert not snapshot.applications
    assert len(snapshot.diagnostics) == 1
    assert "not available" in snapshot.diagnostics[0].message


def testRejectsIconPathEscape(tmp_path):
    bundle = makeBundle(tmp_path)
    outside_icon = tmp_path / "outside.svg"
    outside_icon.write_text("<svg/>", encoding="utf-8")
    writeManifest(
        bundle,
        [{"id": "krita", "name": "Krita", "command": "krita", "icon": "../outside.svg"}],
    )

    snapshot = _catalog.CatalogLoader(FakeGateway(bundle), "windows").loadCatalog()

    assert snapshot.applications[0].icon_path is None
    assert "escapes the bundle resources/icons directory" in snapshot.diagnostics[0].message


def testInvalidSchemaIsRecoverable(tmp_path):
    bundle = makeBundle(tmp_path)
    manifest_path = bundle.envoy_directory / "despatch.json"
    manifest_path.write_text('{"schemaVersion": 99, "applications": []}', encoding="utf-8")

    snapshot = _catalog.CatalogLoader(FakeGateway(bundle), "windows").loadCatalog()

    assert not snapshot.applications
    assert "schemaVersion" in snapshot.diagnostics[0].message
