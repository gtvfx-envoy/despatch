# -*- mode: python ; coding: utf-8 -*-
"""Build the standalone Windows Despatch executable."""

import os
from pathlib import Path


PROJECT_ROOT = Path(SPECPATH).resolve()
SOURCE_ROOT = PROJECT_ROOT / "py"
RESOURCE_ROOT = PROJECT_ROOT / "resources"
DOCUMENTATION_ROOT = PROJECT_ROOT / "site"
CONSOLE_BUILD = os.environ.get("DESPATCH_CONSOLE_BUILD") == "1"

if not (DOCUMENTATION_ROOT / "index.html").is_file():
    raise SystemExit("Build the ProperDocs site before running PyInstaller")

analysis = Analysis(
    [str(PROJECT_ROOT / "scripts" / "pyinstaller_entry.py")],
    pathex=[str(SOURCE_ROOT)],
    binaries=[],
    datas=[
        (str(RESOURCE_ROOT), "despatch/resources"),
        (str(DOCUMENTATION_ROOT), "despatch/docs"),
    ],
    hiddenimports=[
        "envoy",
        "envoy._envoy",
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtNetwork",
        "PySide6.QtWidgets",
        "Qt",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)

python_archive = PYZ(analysis.pure)

executable = EXE(
    python_archive,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="despatch",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=CONSOLE_BUILD,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(RESOURCE_ROOT / "icons" / "despatch.ico"),
)
