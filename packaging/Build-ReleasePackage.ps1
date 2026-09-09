#Requires -Version 5.1
<#
.SYNOPSIS
  Build a distributable SolarAutoTest setup zip for other PCs.
#>
[CmdletBinding()]
param(
    [string]$OutDir = "",
    [string]$PublishDir = "",
    [string]$PublishHttpBaseUrl = "",
    [string]$OssBucket = "",
    [string]$OssPrefix = "solarautotest/updates",
    [string]$OssEndpoint = "",
    [switch]$PublishEmkuOss,
    [switch]$PublishGitLab,
    [switch]$SkipBundleUv
)

$ErrorActionPreference = "Stop"
# UTF-8 console so Chinese prints correctly under Windows PowerShell 5.1
try {
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [Console]::OutputEncoding
    if ($Host.Name -eq 'ConsoleHost') {
        try { chcp 65001 | Out-Null } catch {}
    }
} catch {}

$ProgressPreference = "SilentlyContinue"

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
if (-not $OutDir) {
    $OutDir = Join-Path $repoRoot "dist"
}
$OutDir = [System.IO.Path]::GetFullPath($OutDir)
$stage = Join-Path $OutDir "SolarAutoTest-Setup"
$zipPath = Join-Path $OutDir ("SolarAutoTest-Setup-" + (Get-Date -Format "yyyyMMdd") + ".zip")

Write-Host "Repo:  $repoRoot"
Write-Host "Stage: $stage"
Write-Host "Zip:   $zipPath"

if (Test-Path $stage) { Remove-Item -Recurse -Force $stage }
New-Item -ItemType Directory -Path $stage -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $stage "app") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $stage "bundled") -Force | Out-Null

# Copy installer scripts to stage root
Copy-Item -Force (Join-Path $PSScriptRoot "install.bat") (Join-Path $stage "install.bat")
Copy-Item -Force (Join-Path $PSScriptRoot "Install-SolarAutoTest.ps1") (Join-Path $stage "Install-SolarAutoTest.ps1")
Copy-Item -Force (Join-Path $PSScriptRoot "Check-And-Update.ps1") (Join-Path $stage "Check-And-Update.ps1")
Copy-Item -Force (Join-Path $PSScriptRoot "Verify-Install.ps1") (Join-Path $stage "Verify-Install.ps1")
Copy-Item -Force (Join-Path $PSScriptRoot "INSTALL.txt") (Join-Path $stage "INSTALL.txt")

# Version stamp for LAN upgrade detection (YYYYMMDD.build)
$pkgVersion = Get-Date -Format "yyyyMMdd"
$versionFile = Join-Path $stage "VERSION"
$versionText = @(
    $pkgVersion
    ("built=" + (Get-Date -Format "yyyy-MM-dd HH:mm:ss"))
    ("repo=" + $repoRoot)
) -join "`r`n"
Set-Content -Path $versionFile -Value $versionText -Encoding UTF8
Copy-Item -Force $versionFile (Join-Path $stage "app\VERSION")
Write-Host ("Package version: " + $pkgVersion)

# Copy app (exclude heavy/local noise)
$appDest = Join-Path $stage "app"
$xd = @(
    "/XD", ".git", ".venv", ".idea", ".vscode", ".cursor", ".claude",
    "__pycache__", ".pytest_cache", "packaging", "dist", "data_logs",
    "uv-cache", "node_modules", "agent-transcripts", "command_save_files"
)
$xf = @("/XF", "*.pyc", "*.pyo", "*.log", "log.txt", "*.zip", "*.7z")
$rcArgs = @($repoRoot, $appDest, "/E", "/NFL", "/NDL", "/NJH", "/NJS", "/NC", "/NS", "/NP", "/R:1", "/W:1") + $xd + $xf
& robocopy @rcArgs | Out-Null
if ($LASTEXITCODE -ge 8) { throw "robocopy failed: $LASTEXITCODE" }
# Ensure VERSION survives robocopy (repo may not have it)
Copy-Item -Force $versionFile (Join-Path $stage "app\VERSION")

# Bundle uv.exe for offline-friendly install
$bundleUv = Join-Path $stage "bundled\uv.exe"
if (-not $SkipBundleUv) {
    Write-Host "Bundling uv.exe ..."
    $localUv = $null
    foreach ($c in @(
        (Join-Path $env:USERPROFILE ".local\bin\uv.exe"),
        (Get-Command uv.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source)
    )) {
        if ($c -and (Test-Path $c)) { $localUv = $c; break }
    }
    if ($localUv) {
        Copy-Item -Force $localUv $bundleUv
        Write-Host "[OK] bundled from $localUv"
    } else {
        $tmpZip = Join-Path $env:TEMP ("uv-bundle-" + [guid]::NewGuid() + ".zip")
        $tmpDir = Join-Path $env:TEMP ("uv-bundle-ex-" + [guid]::NewGuid())
        Invoke-WebRequest -Uri "https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip" -OutFile $tmpZip -UseBasicParsing
        Expand-Archive $tmpZip $tmpDir -Force
        $found = Get-ChildItem $tmpDir -Filter uv.exe -Recurse | Select-Object -First 1
        if (-not $found) { throw "cannot bundle uv.exe" }
        Copy-Item -Force $found.FullName $bundleUv
        Remove-Item -Force $tmpZip -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force $tmpDir -ErrorAction SilentlyContinue
        Write-Host "[OK] downloaded uv.exe"
    }
}

# Zip via tar (avoids Compress-Archive file-lock issues with freshly copied exe)
if (Test-Path $zipPath) { Remove-Item -Force $zipPath }
Push-Location $stage
try {
    & tar.exe -a -c -f $zipPath *
    if ($LASTEXITCODE -ne 0) { throw "tar zip failed: $LASTEXITCODE" }
}
finally {
    Pop-Location
}

$sizeMb = [math]::Round((Get-Item $zipPath).Length / 1MB, 1)

# Optional: publish to LAN update channel (latest.json + zip)
if (-not $PublishDir -and $env:SOLARAUTOTEST_PUBLISH_DIR) {
    $PublishDir = $env:SOLARAUTOTEST_PUBLISH_DIR.Trim()
}
if ($PublishDir) {
    if (-not (Test-Path $PublishDir)) {
        New-Item -ItemType Directory -Path $PublishDir -Force | Out-Null
    }
    $destZip = Join-Path $PublishDir ("SolarAutoTest-Setup-" + $pkgVersion + ".zip")
    Copy-Item -Force $zipPath $destZip
    $manifest = [ordered]@{
        version  = $pkgVersion
        zip_name = [IO.Path]::GetFileName($destZip)
        built    = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
        size_mb  = $sizeMb
    }
    $jsonPath = Join-Path $PublishDir "latest.json"
    ($manifest | ConvertTo-Json) | Set-Content -Path $jsonPath -Encoding UTF8
    Write-Host ("[OK] Published to LAN channel: " + $PublishDir) -ForegroundColor Green
    Write-Host ("     latest.json + " + [IO.Path]::GetFileName($destZip))
}

Write-Host ""
Write-Host ("[OK] Release package ready  version=" + $pkgVersion) -ForegroundColor Green
Write-Host "  Folder: $stage"
Write-Host "  ZIP:    $zipPath  ($sizeMb MB)"
if ($PublishGitLab -or ($env:SOLARAUTOTEST_GITLAB_PUBLISH -eq "1")) {
    $pub = Join-Path $PSScriptRoot "Publish-GitLabPackage.ps1"
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $pub -ZipPath $zipPath
    if ($LASTEXITCODE -ne 0) { throw "GitLab publish failed: $LASTEXITCODE" }
}

if (-not $PublishHttpBaseUrl -and $env:SOLARAUTOTEST_HTTP_BASE_URL) {
    $PublishHttpBaseUrl = $env:SOLARAUTOTEST_HTTP_BASE_URL
}
if (-not $OssBucket -and $env:SOLARAUTOTEST_OSS_BUCKET) {
    $OssBucket = $env:SOLARAUTOTEST_OSS_BUCKET
}
if ($env:SOLARAUTOTEST_OSS_PREFIX) { $OssPrefix = $env:SOLARAUTOTEST_OSS_PREFIX }
if (-not $OssEndpoint -and $env:SOLARAUTOTEST_OSS_ENDPOINT) {
    $OssEndpoint = $env:SOLARAUTOTEST_OSS_ENDPOINT
}
if ($env:SOLARAUTOTEST_PUBLISH_EMKU_OSS -eq "1") { $PublishEmkuOss = $true }

if ($PublishEmkuOss -and -not $PublishHttpBaseUrl) {
    $PublishHttpBaseUrl = "https://qgongye.oss-cn-shanghai.aliyuncs.com/solarautotest/updates"
    if (-not $OssBucket) { $OssBucket = "qgongye" }
    if (-not $OssEndpoint) { $OssEndpoint = "oss-cn-shanghai.aliyuncs.com" }
    if (-not $OssPrefix) { $OssPrefix = "solarautotest/updates" }
}

if ($PublishHttpBaseUrl -or $PublishEmkuOss) {
    $httpPub = Join-Path $PSScriptRoot "Publish-HttpChannel.ps1"
    $argList = @(
        "-NoProfile", "-ExecutionPolicy", "Bypass",
        "-File", $httpPub,
        "-ZipPath", $zipPath,
        "-Version", $pkgVersion
    )
    if ($PublishHttpBaseUrl) { $argList += @("-HttpBaseUrl", $PublishHttpBaseUrl) }
    if ($PublishEmkuOss) {
        $argList += @("-UseEmkuOss")
        $argList += @("-OssPrefix", $OssPrefix)
    } elseif ($OssBucket) {
        $argList += @("-OssBucket", $OssBucket, "-OssPrefix", $OssPrefix)
        if ($OssEndpoint) { $argList += @("-OssEndpoint", $OssEndpoint) }
    }
    & powershell.exe @argList
    if ($LASTEXITCODE -ne 0) { throw "HTTP/OSS publish failed: $LASTEXITCODE" }
}

if ($PublishDir) {
    Write-Host ("  Channel clients check: " + $PublishDir)
} elseif ($PublishEmkuOss -or $PublishHttpBaseUrl) {
    $ch = if ($PublishHttpBaseUrl) { $PublishHttpBaseUrl.TrimEnd('/') } else { "https://qgongye.oss-cn-shanghai.aliyuncs.com/solarautotest/updates" }
    Write-Host ("  Channel: HTTP " + $ch)
} elseif ($PublishGitLab -or ($env:SOLARAUTOTEST_GITLAB_PUBLISH -eq "1")) {
    Write-Host "  Channel: GitLab Package Registry (see Publish-GitLabPackage output)"
} else {
    Write-Host "Tip: EMKU OSS -> packaging\build_release.bat -PublishEmkuOss"
    Write-Host "Tip: LAN     -> packaging\build_release.bat -PublishDir \\server\share\SolarAutoTest\updates"
}
Write-Host "Colleagues: unzip then run install.bat (also upgrades)."
