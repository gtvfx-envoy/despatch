from pathlib import Path

from despatch import _models, _search


def makeApplication(stable_id, name, command, keywords=()):
    return _models.ApplicationEntry(
        stable_id=stable_id,
        application_id=stable_id.rsplit(":", 1)[-1],
        bundle_id="gt:test",
        name=name,
        command=command,
        args=(),
        description="",
        icon_path=None,
        group_id="",
        keywords=keywords,
        in_terminal=False,
        order=0,
        source_path=Path("despatch.json"),
    )


def testExactAndPrefixMatchesRankFirst():
    applications = (
        makeApplication("gt:test:maya-tools", "Maya Tools", "maya_tools"),
        makeApplication("gt:test:maya", "Maya", "maya"),
        makeApplication("gt:test:nuke", "Nuke", "nuke", ("maya",)),
    )

    ranked = _search.rankApplications(applications, "maya")

    assert [application.name for application in ranked] == ["Maya", "Maya Tools", "Nuke"]


def testFavoritesBreakEqualRelevanceTies():
    applications = (
        makeApplication("gt:test:alpha", "Alpha Tool", "alpha"),
        makeApplication("gt:test:alpine", "Alpine Tool", "alpine"),
    )

    ranked = _search.rankApplications(
        applications,
        "al",
        favorites=frozenset({"gt:test:alpine"}),
    )

    assert ranked[0].stable_id == "gt:test:alpine"


def testSubsequenceMatching():
    application = makeApplication("gt:test:turntable", "Model Turntable", "turntable")

    assert _search.rankApplications((application,), "mdlt") == (application,)
