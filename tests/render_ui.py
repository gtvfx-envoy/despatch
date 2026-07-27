"""Render a representative Despatch window for visual QA."""

from __future__ import annotations

import argparse
from pathlib import Path

from Qt import QtWidgets

from despatch import _main_window, _models, _theme


def makeApplication(
    application_id: str,
    name: str,
    description: str,
    group_id: str,
    order: int,
) -> _models.ApplicationEntry:
    return _models.ApplicationEntry(
        stable_id=f"gt:sample:{application_id}",
        application_id=application_id,
        bundle_id="gt:sample",
        name=name,
        command=application_id,
        args=(),
        description=description,
        icon_path=None,
        group_id=group_id,
        keywords=(),
        in_terminal=False,
        order=order,
        source_path=Path(".envoy/despatch.json"),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--theme", choices=["light", "dark"], default="dark")
    args = parser.parse_args()

    application = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    _theme.applyTheme(application, args.theme)
    window = _main_window.MainWindow()
    stacks = (
        _models.NamedStack("studio", "2026-07-26", Path("studio.estack")),
        _models.NamedStack("testing", "2026-07-24", Path("testing.estack")),
    )
    groups = (
        _models.CatalogGroup("gt:sample:creative", "Creative", 0, "gt:sample"),
        _models.CatalogGroup("gt:sample:automation", "Automation", 1, "gt:sample"),
    )
    applications = (
        makeApplication(
            "krita", "Krita", "Digital painting and illustration", groups[0].stable_id, 0
        ),
        makeApplication(
            "unreal", "Unreal Editor", "Open the current project", groups[0].stable_id, 1
        ),
        makeApplication("validate", "Validate", "Run project validation", groups[1].stable_id, 2),
        makeApplication(
            "branch_status",
            "Branch Status",
            "Review repository state",
            groups[1].stable_id,
            3,
        ),
        makeApplication("vscode", "Visual Studio Code", "Open the current workspace", "", 4),
    )
    stack_state = _models.StackState(
        _models.StackMode.EXPLICIT,
        _models.StackSelection("studio", "studio", Path("studio.estack"), "2026-07-26"),
    )
    snapshot = _models.CatalogSnapshot(stack_state, applications, groups, ())
    window.setStacks(stacks, stack_state)
    window.setCatalog(snapshot, frozenset({"gt:sample:krita"}), ("gt:sample:unreal",))
    window.setReady()
    window.show()
    application.processEvents()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    saved = window.grab().save(str(args.output))
    window.allowClose()
    window.close()
    return 0 if saved else 1


if __name__ == "__main__":
    raise SystemExit(main())
