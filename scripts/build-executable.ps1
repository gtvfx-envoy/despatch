[CmdletBinding()]
param(
    [string]$PythonExecutable = "",
    [switch]$SkipToolInstall,
    [switch]$Console
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$pyinstaller_version = "6.21.0"
$script_directory = Split-Path -Parent $PSCommandPath
$repository_root = (Resolve-Path -LiteralPath (Join-Path $script_directory "..")).Path
$spec_path = Join-Path $repository_root "pyinstaller.spec"
$dist_directory = Join-Path $repository_root "dist"
$work_directory = Join-Path $repository_root "build\pyinstaller"
$tool_directory = Join-Path $repository_root "build\pyinstaller-tools"
$executable_path = Join-Path $dist_directory "despatch.exe"
$original_python_path = $env:PYTHONPATH
$original_console_build = $env:DESPATCH_CONSOLE_BUILD

function Invoke-BuildPython {
    param(
        [Parameter(Mandatory)]
        [string[]]$PythonArguments
    )

    if ($PythonExecutable) {
        & $PythonExecutable @PythonArguments
    } else {
        & envoy python @PythonArguments
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed with exit code $LASTEXITCODE."
    }
}

function Test-PyInstallerVersion {
    $version_check = @(
        "-c",
        "import PyInstaller, sys; sys.exit(PyInstaller.__version__ != '$pyinstaller_version')"
    )
    if ($PythonExecutable) {
        & $PythonExecutable @version_check *> $null
    } else {
        & envoy python @version_check *> $null
    }
    return $LASTEXITCODE -eq 0
}

try {
    $env:DESPATCH_CONSOLE_BUILD = if ($Console) { "1" } else { "0" }
    if ($PythonExecutable) {
        $resolved_python = Get-Command -Name $PythonExecutable -ErrorAction Stop
        $PythonExecutable = $resolved_python.Source
    } else {
        Get-Command -Name "envoy" -ErrorAction Stop | Out-Null
    }

    if (Test-Path -LiteralPath $tool_directory) {
        $env:PYTHONPATH = if ($original_python_path) {
            "$tool_directory$([IO.Path]::PathSeparator)$original_python_path"
        } else {
            $tool_directory
        }
    }

    if (-not (Test-PyInstallerVersion)) {
        if ($SkipToolInstall) {
            throw "PyInstaller $pyinstaller_version is not available."
        }
        New-Item -ItemType Directory -Path $tool_directory -Force | Out-Null
        Invoke-BuildPython @(
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--upgrade",
            "--target",
            $tool_directory,
            "PyInstaller==$pyinstaller_version"
        )
        $env:PYTHONPATH = if ($original_python_path) {
            "$tool_directory$([IO.Path]::PathSeparator)$original_python_path"
        } else {
            $tool_directory
        }
    }

    Invoke-BuildPython @(
        "-c",
        "import PyInstaller, PySide6, Qt, envoy, despatch; " +
            "print('Freezing with', PyInstaller.__version__, Qt.__binding__)"
    )

    New-Item -ItemType Directory -Path $dist_directory -Force | Out-Null
    New-Item -ItemType Directory -Path $work_directory -Force | Out-Null

    Push-Location $repository_root
    try {
        Invoke-BuildPython @(
            "-m",
            "PyInstaller",
            "--clean",
            "--noconfirm",
            "--distpath",
            $dist_directory,
            "--workpath",
            $work_directory,
            $spec_path
        )
    } finally {
        Pop-Location
    }

    if (-not (Test-Path -LiteralPath $executable_path -PathType Leaf)) {
        throw "PyInstaller completed without creating '$executable_path'."
    }
    $built_executable = Get-Item -LiteralPath $executable_path
    Write-Host "Built $($built_executable.FullName) ($($built_executable.Length) bytes)"
} finally {
    $env:PYTHONPATH = $original_python_path
    $env:DESPATCH_CONSOLE_BUILD = $original_console_build
}
