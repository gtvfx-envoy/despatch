[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$ReleaseTag,
    [string]$PythonExecutable = "python",
    [string]$EnvironmentDirectory = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if (Test-Path variable:PSNativeCommandUseErrorActionPreference) {
    $PSNativeCommandUseErrorActionPreference = $true
}

if ($ReleaseTag -notmatch '^v\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$') {
    throw "Envoy release tags must be v-prefixed semantic versions: '$ReleaseTag'."
}

$resolved_python = (Get-Command -Name $PythonExecutable -ErrorAction Stop).Source
$env:PYTHONHOME = $null
$env:PYTHONPATH = $null
$temporary_root = if ($env:RUNNER_TEMP) {
    $env:RUNNER_TEMP
} else {
    [IO.Path]::GetTempPath()
}
if (-not $EnvironmentDirectory) {
    $environment_name = "despatch-envoy-$([Guid]::NewGuid().ToString('N'))"
    $EnvironmentDirectory = Join-Path $temporary_root $environment_name
}
$environment_path = [IO.Path]::GetFullPath($EnvironmentDirectory)
if (Test-Path -LiteralPath $environment_path) {
    throw "Envoy environment already exists: '$environment_path'."
}

Write-Host "Creating an isolated Envoy installation at '$environment_path'."
New-Item -ItemType Directory -Path $environment_path | Out-Null
$site_packages_root = Join-Path $environment_path "site-packages"
$python_site_packages = Join-Path $site_packages_root "Python311\site-packages"
New-Item -ItemType Directory -Path $python_site_packages -Force | Out-Null

$headers = @{
    Accept = "application/vnd.github+json"
    "User-Agent" = "despatch-envoy-bootstrap"
    "X-GitHub-Api-Version" = "2022-11-28"
}
$github_token = if ($env:GH_TOKEN) {
    $env:GH_TOKEN
} elseif ($env:GITHUB_TOKEN) {
    $env:GITHUB_TOKEN
} else {
    ""
}
if ($github_token) {
    $headers.Authorization = "Bearer $github_token"
}

$escaped_release_tag = [Uri]::EscapeDataString($ReleaseTag)
$release_uri = "https://api.github.com/repos/gtvfx-envoy/envoy/releases/tags/$escaped_release_tag"
Write-Host "Resolving Envoy release '$ReleaseTag'."
$release = Invoke-RestMethod -Uri $release_uri -Headers $headers
$wheel_assets = @($release.assets | Where-Object {
    $_.name -match '^envoy-.+-cp310-abi3-win_amd64\.whl$'
})
if ($wheel_assets.Count -ne 1) {
    throw "Expected one Windows Envoy wheel in release '$ReleaseTag'; found $($wheel_assets.Count)."
}
$archive_name = "envoy-$ReleaseTag-windows-x86_64.zip"
$archive_assets = @($release.assets | Where-Object { $_.name -eq $archive_name })
if ($archive_assets.Count -ne 1) {
    throw "Expected one '$archive_name' asset in release '$ReleaseTag'; found $($archive_assets.Count)."
}
$checksum_assets = @($release.assets | Where-Object { $_.name -eq "SHA256SUMS" })
if ($checksum_assets.Count -ne 1) {
    throw "Expected one SHA256SUMS asset in release '$ReleaseTag'; found $($checksum_assets.Count)."
}

$download_directory = Join-Path $environment_path "downloads"
New-Item -ItemType Directory -Path $download_directory | Out-Null
$wheel_name = [string]$wheel_assets[0].name
$wheel_path = Join-Path $download_directory $wheel_name
$archive_path = Join-Path $download_directory $archive_name
$checksums_path = Join-Path $download_directory "SHA256SUMS"
Invoke-WebRequest -Uri $wheel_assets[0].browser_download_url -Headers $headers -OutFile $wheel_path
Invoke-WebRequest -Uri $archive_assets[0].browser_download_url -Headers $headers -OutFile $archive_path
Invoke-WebRequest `
    -Uri $checksum_assets[0].browser_download_url `
    -Headers $headers `
    -OutFile $checksums_path

foreach ($asset_path in ($wheel_path, $archive_path)) {
    $asset_name = Split-Path -Leaf $asset_path
    $escaped_asset_name = [Regex]::Escape($asset_name)
    $checksum_pattern = "^([0-9A-Fa-f]{64})\s+\*?$escaped_asset_name$"
    $checksum_matches = @(
        Get-Content -LiteralPath $checksums_path |
            Where-Object { $_ -match $checksum_pattern }
    )
    if ($checksum_matches.Count -ne 1) {
        throw "Expected one checksum for '$asset_name'; found $($checksum_matches.Count)."
    }
    $null = $checksum_matches[0] -match $checksum_pattern
    $expected_checksum = $Matches[1].ToUpperInvariant()
    $actual_checksum = (Get-FileHash -LiteralPath $asset_path -Algorithm SHA256).Hash
    if ($actual_checksum -ne $expected_checksum) {
        throw "Checksum validation failed for '$asset_name'."
    }
    Write-Host "Verified $asset_name ($actual_checksum)."
}

& $resolved_python -m pip install `
    --disable-pip-version-check `
    --no-deps `
    --target `
    $python_site_packages `
    $wheel_path
$env:PYTHONPATH = $python_site_packages
& $resolved_python -c "import envoy; print('Envoy Python API', envoy.__version__)"
$env:PYTHONPATH = $null

$release_directory = Join-Path $environment_path "release"
Expand-Archive -LiteralPath $archive_path -DestinationPath $release_directory
$envoy_directory = Join-Path $release_directory "gt\envoy\$ReleaseTag\bin"
$envoy_executable = Join-Path $envoy_directory "envoy.exe"
if (-not (Test-Path -LiteralPath $envoy_executable -PathType Leaf)) {
    throw "Extracting '$archive_name' did not create '$envoy_executable'."
}
& $envoy_executable --version

$config_root = Join-Path $environment_path "config"
New-Item -ItemType Directory -Path $config_root | Out-Null

if ($env:GITHUB_PATH) {
    Add-Content -LiteralPath $env:GITHUB_PATH -Value $envoy_directory
}
if ($env:GITHUB_ENV) {
    Add-Content -LiteralPath $env:GITHUB_ENV -Value "DESPATCH_CI_ENVOY=$envoy_executable"
    Add-Content -LiteralPath $env:GITHUB_ENV -Value "ENVOY_SITE_PACKAGES=$site_packages_root"
    Add-Content -LiteralPath $env:GITHUB_ENV -Value "ENVOY_CONFIG_ROOT=$config_root"
}

Write-Host "Envoy '$ReleaseTag' is available at '$envoy_executable'."
