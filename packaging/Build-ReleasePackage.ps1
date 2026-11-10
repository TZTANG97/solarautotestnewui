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
    [string]$Version = "",
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
# Same-day republish needs HHMM so clients do not skip update
if (-not $Version) {
    $Version = Get-Date -Format "yyyyMMdd.HHmm"
}
$pkgVersion = $Version.Trim()
$zipPath = Join-Path $OutDir ("SolarAutoTest-Setup-" + $pkgVersion + ".zip")

Write-Host "Repo:  $repoRoot"
Write-Host "Stage: $stage"
Write-Host "Zip:   $zipPath"

if (Test-Path $stage) { Remove-Item -Recurse -Force $stage }
New-Item -ItemType Directory -Path $stage -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $stage "app") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $stage "bundled") -Force | Out-Null

# Copy installer scripts to stage root (keep UTF-8 BOM — PS 5.1 misparses Chinese without it)
$ps1Files = @(
    "Install-SolarAutoTest.ps1",
    "Install-PathHelpers.ps1",
    "Check-And-Update.ps1",
    "Verify-Install.ps1"
)
Copy-Item -Force (Join-Path $PSScriptRoot "install.bat") (Join-Path $stage "install.bat")
Copy-Item -Force (Join-Path $PSScriptRoot "INSTALL.txt") (Join-Path $stage "INSTALL.txt")
foreach ($name in $ps1Files) {
    $src = Join-Path $PSScriptRoot $name
    $dst = Join-Path $stage $name
    $text = [System.IO.File]::ReadAllText($src)
    $utf8Bom = New-Object System.Text.UTF8Encoding $true
    [System.IO.File]::WriteAllText($dst, $text, $utf8Bom)
}
# Smoke-parse installer before zip (fail fast if quote/encoding breaks PS 5.1)
$installPs1 = Join-Path $stage "Install-SolarAutoTest.ps1"
$parseErrs = $null
$null = [System.Management.Automation.Language.Parser]::ParseFile($installPs1, [ref]$null, [ref]$parseErrs)
if ($parseErrs -and $parseErrs.Count -gt 0) {
    throw ("Install-SolarAutoTest.ps1 parse error: " + $parseErrs[0].ToString())
}
Write-Host "[OK] Install-SolarAutoTest.ps1 parse check passed"

# Version stamp for LAN upgrade detection (yyyyMMdd.HHmm)
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
    "uv-cache", "node_modules", "agent-transcripts", "command_save_files",
    # Keep release zip small: local DB / scratch / media never needed on bench PCs
    # 注意：dewetron_media 必须进包（接线图预览）；勿再排除
    "database", "code_example", "screenshots", "recordings", "mindmap",
    "iot_job_inbox", "wt_file_save_path"
)
# Never ship local IOT identity into the zip (would make every PC share one pythonid / localhost token)
$xf = @(
    "/XF", "*.pyc", "*.pyo", "*.log", "log.txt", "*.zip", "*.7z",
    "solar_agent.json", "solar_agent.sim.json", "solar_machine_id", "iot_bootstrap.json",
    "db.sqlite", "uv.exe"
)
$rcArgs = @($repoRoot, $appDest, "/E", "/NFL", "/NDL", "/NJH", "/NJS", "/NC", "/NS", "/NP", "/R:1", "/W:1") + $xd + $xf
& robocopy @rcArgs | Out-Null
if ($LASTEXITCODE -ge 8) { throw "robocopy failed: $LASTEXITCODE" }
# Ensure VERSION survives robocopy (repo may not have it)
Copy-Item -Force $versionFile (Join-Path $stage "app\VERSION")
# Defense in depth: delete if somehow still present under app/config
foreach ($bad in @("solar_agent.json", "solar_agent.sim.json", "solar_machine_id", "iot_bootstrap.json")) {
    $p = Join-Path $appDest ("config\" + $bad)
    if (Test-Path $p) { Remove-Item -Force $p }
}

# Bundle CEI headless analysis (结案自动出报告，不必另装分析软件)
$analysisDest = Join-Path $appDest "bundled_analysis"
$analysisCandidates = @(
    (Join-Path $repoRoot "..\SolarTestDataAnalysisApp"),
    (Join-Path $repoRoot "..\..\MyProject\SolarTestDataAnalysisApp"),
    "E:\MyProject\SolarTestDataAnalysisApp",
    "E:\SolarTestDataAnalysisApp"
)
$analysisSrc = $null
foreach ($c in $analysisCandidates) {
    $full = [System.IO.Path]::GetFullPath($c)
    $cei = Join-Path $full "CEI"
    if ((Test-Path (Join-Path $cei "run_headless.py")) -or (Test-Path (Join-Path $cei "src\mypkg"))) {
        $analysisSrc = $cei
        break
    }
}
if ($analysisSrc) {
    Write-Host "Bundling analysis CEI from $analysisSrc ..."
    New-Item -ItemType Directory -Path $analysisDest -Force | Out-Null
    # 勿打进 command_save_files / _unpack：只会撑大增量清单，逼工控机反复全量。
    $aXd = @(
        "/XD", ".venv", ".pytest_cache", "__pycache__", ".git", ".idea", ".vscode",
        "code_example", "media", "command_save_files", "_unpack"
    )
    $aXf = @("/XF", "*.pyc", "*.pyo", "*.log", "*.svn000.tmp.doc", "*.svn000.tmp.docx")
    $aArgs = @($analysisSrc, $analysisDest, "/E", "/NFL", "/NDL", "/NJH", "/NJS", "/NC", "/NS", "/NP", "/R:1", "/W:1") + $aXd + $aXf
    & robocopy @aArgs | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy analysis failed: $LASTEXITCODE" }
    if (-not (Test-Path (Join-Path $analysisDest "run_headless.py"))) {
        Write-Host "[WARN] bundled_analysis missing run_headless.py"
    } else {
        Write-Host "[OK] bundled_analysis ready"
    }
} else {
    Write-Host "[WARN] SolarTestDataAnalysisApp not found nearby; skip bundled_analysis"
}

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

# Prepare incremental file channel (blobs + files-*.json) before publish
$channelPrep = Join-Path $OutDir "update-channel"
$httpBaseForManifest = ""
if ($PublishEmkuOss) {
    $httpBaseForManifest = "https://qgongye.oss-cn-shanghai.aliyuncs.com/solarautotest/updates"
} elseif ($PublishHttpBaseUrl) {
    $httpBaseForManifest = $PublishHttpBaseUrl.Trim().TrimEnd('/')
}
$mfArgs = @(
    "-NoProfile", "-ExecutionPolicy", "Bypass",
    "-File", (Join-Path $PSScriptRoot "Build-FileManifest.ps1"),
    "-StageRoot", $stage,
    "-ChannelDir", $channelPrep,
    "-Version", $pkgVersion
)
if ($httpBaseForManifest) { $mfArgs += @("-HttpBaseUrl", $httpBaseForManifest) }
& powershell.exe @mfArgs
if ($LASTEXITCODE -ne 0) { throw "Build-FileManifest failed: $LASTEXITCODE" }

if ($PublishHttpBaseUrl -or $PublishEmkuOss) {
    $httpPub = Join-Path $PSScriptRoot "Publish-HttpChannel.ps1"
    $argList = @(
        "-NoProfile", "-ExecutionPolicy", "Bypass",
        "-File", $httpPub,
        "-ZipPath", $zipPath,
        "-Version", $pkgVersion,
        "-OutDir", $channelPrep,
        "-StageRoot", $stage
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

# LAN channel: also drop files manifest + blobs next to latest.json
if ($PublishDir) {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "Build-FileManifest.ps1") `
        -StageRoot $stage -ChannelDir $PublishDir -Version $pkgVersion
    if ($LASTEXITCODE -ne 0) { throw "LAN Build-FileManifest failed: $LASTEXITCODE" }
    $lanFiles = Join-Path $PublishDir "files-latest.json"
    if (Test-Path $lanFiles) {
        $jsonPath = Join-Path $PublishDir "latest.json"
        if (Test-Path $jsonPath) {
            $m = Get-Content -Raw -Encoding UTF8 $jsonPath | ConvertFrom-Json
            $o = [ordered]@{}
            $m.PSObject.Properties | ForEach-Object { $o[$_.Name] = $_.Value }
            $o["files_name"] = "files-latest.json"
            $o["files_url"] = ""
            $o["blobs_dir"] = "blobs"
            $o["update_mode"] = "incremental"
            [IO.File]::WriteAllText(
                $jsonPath,
                ($o | ConvertTo-Json -Depth 6),
                (New-Object System.Text.UTF8Encoding $false)
            )
        }
    }
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
