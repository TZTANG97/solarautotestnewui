#Requires -Version 5.1
<#
.SYNOPSIS
  Prepare (and optionally upload) an HTTP update channel for Aliyun OSS / ECS nginx.

.DESCRIPTION
  Writes:
    <OutDir>\latest.json
    <OutDir>\SolarAutoTest-Setup-<version>.zip

  latest.json includes zip_url = <HttpBaseUrl>/<zip_name> so clients can download
  via Check-And-Update.ps1 HTTP mode (no GitLab needed).

  Upload options:
    1) -OssBucket + ossutil.exe  (Aliyun OSS, recommended)
    2) Only prepare OutDir, then you scp/rsync to ECS nginx wwwroot

  Client config.ini:
    [update]
    enabled = 1
    auto_install = 1
    channel = https://your-bucket.oss-cn-hangzhou.aliyuncs.com/solarautotest/updates
    ; or https://update.your-domain.com/solarautotest
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ZipPath,
    [string]$HttpBaseUrl = "",
    [string]$OutDir = "",
    [string]$Version = "",
    [string]$OssBucket = "",
    [string]$OssPrefix = "solarautotest/updates",
    [string]$OssEndpoint = "",
    [string]$OssUtil = "",
    [switch]$UseEmkuOss,
    [string]$EmkuEnvFile = "",
    [string]$EmkuPython = "E:\EMKU\backend_fastapi\.venv\Scripts\python.exe"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

try {
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [Console]::OutputEncoding
} catch {}

if (-not (Test-Path $ZipPath)) { throw "Zip not found: $ZipPath" }
$ZipPath = [IO.Path]::GetFullPath($ZipPath)

if (-not $Version) {
    $leaf = [IO.Path]::GetFileNameWithoutExtension($ZipPath)
    if ($leaf -match '(\d{8}(?:\.\d+)?)') { $Version = $Matches[1] }
    else { $Version = Get-Date -Format "yyyyMMdd" }
}

if ($UseEmkuOss) {
    if (-not $OssBucket) { $OssBucket = "qgongye" }
    if (-not $OssEndpoint) { $OssEndpoint = "oss-cn-shanghai.aliyuncs.com" }
    if (-not $OssPrefix) { $OssPrefix = "solarautotest/updates" }
    if (-not $HttpBaseUrl) {
        $HttpBaseUrl = "https://$OssBucket.$OssEndpoint/$($OssPrefix.Trim().Trim('/'))"
    }
}

$HttpBaseUrl = $HttpBaseUrl.Trim().TrimEnd('/')
if ($HttpBaseUrl -notmatch '^https?://') {
    throw "HttpBaseUrl must start with http:// or https:// (or pass -UseEmkuOss)"
}

if (-not $OutDir) {
    $repoDist = Join-Path (Split-Path $PSScriptRoot -Parent) "dist\update-channel"
    $OutDir = $repoDist
}
$OutDir = [IO.Path]::GetFullPath($OutDir)
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$zipName = "SolarAutoTest-Setup-" + $Version + ".zip"
$destZip = Join-Path $OutDir $zipName
Copy-Item -Force $ZipPath $destZip

$sizeMb = [math]::Round((Get-Item $destZip).Length / 1MB, 1)
$zipUrl = $HttpBaseUrl + "/" + $zipName

$manifest = [ordered]@{
    version      = $Version
    zip_name     = $zipName
    zip_url      = $zipUrl
    zip_base_url = $HttpBaseUrl
    built        = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    size_mb      = $sizeMb
    channel      = "http"
}
$jsonPath = Join-Path $OutDir "latest.json"
# UTF-8 without BOM (PowerShell 5.1 Set-Content UTF8 writes BOM)
[IO.File]::WriteAllText(
    $jsonPath,
    ($manifest | ConvertTo-Json),
    (New-Object System.Text.UTF8Encoding $false)
)

Write-Host ""
Write-Host "[OK] HTTP channel prepared" -ForegroundColor Green
Write-Host ("  OutDir:   " + $OutDir)
Write-Host ("  version:  " + $Version)
Write-Host ("  latest:   " + $jsonPath)
Write-Host ("  zip:      " + $destZip)
Write-Host ("  zip_url:  " + $zipUrl)
Write-Host ""
Write-Host "Client config.ini:"
Write-Host ("  channel = " + $HttpBaseUrl)
Write-Host ""

# Optional: EMKU shared bucket via Python oss2 (no ossutil needed)
if ($UseEmkuOss) {
    if (-not (Test-Path $EmkuPython)) {
        throw "EMKU python not found: $EmkuPython (need oss2)"
    }
    $uploader = Join-Path $PSScriptRoot "upload_oss_channel.py"
    $pyArgs = @($uploader, "--dir", $OutDir, "--prefix", $OssPrefix, "--public-read")
    if ($EmkuEnvFile) { $pyArgs += @("--emku-env", $EmkuEnvFile) }
    & $EmkuPython @pyArgs
    if ($LASTEXITCODE -ne 0) { throw "EMKU OSS upload failed: $LASTEXITCODE" }
    Write-Host ""
    Write-Host "User first-install download link (zip):" -ForegroundColor Cyan
    Write-Host ("  " + ($HttpBaseUrl.TrimEnd('/') + "/" + $zipName))
    Write-Host "Auto-update channel (put in config.ini):" -ForegroundColor Cyan
    Write-Host ("  channel = " + $HttpBaseUrl.TrimEnd('/'))
    return
}

# Optional: upload with Aliyun ossutil
if ($OssBucket) {
    if (-not $OssUtil) {
        $cand = @(
            "ossutil",
            "ossutil64",
            (Join-Path $env:USERPROFILE "ossutil\ossutil64.exe"),
            (Join-Path $env:LOCALAPPDATA "ossutil\ossutil64.exe")
        )
        foreach ($c in $cand) {
            $cmd = Get-Command $c -ErrorAction SilentlyContinue
            if ($cmd) { $OssUtil = $cmd.Source; break }
            if (Test-Path $c) { $OssUtil = $c; break }
        }
    }
    if (-not $OssUtil -or -not (Test-Path $OssUtil)) {
        throw "ossutil not found. Install: https://help.aliyun.com/document_detail/120075.html  then re-run with -OssUtil path"
    }

    $prefix = $OssPrefix.Trim().Trim('/')
    $ossJson = "oss://$OssBucket/$prefix/latest.json"
    $ossZip = "oss://$OssBucket/$prefix/$zipName"

    $extra = @()
    if ($OssEndpoint) { $extra += @("-e", $OssEndpoint) }

    Write-Host ("Uploading to OSS bucket=" + $OssBucket + " prefix=" + $prefix)
    & $OssUtil cp $jsonPath $ossJson -f @extra
    if ($LASTEXITCODE -ne 0) { throw "ossutil upload latest.json failed: $LASTEXITCODE" }
    & $OssUtil cp $destZip $ossZip -f @extra
    if ($LASTEXITCODE -ne 0) { throw "ossutil upload zip failed: $LASTEXITCODE" }

    Write-Host "[OK] Uploaded to Aliyun OSS" -ForegroundColor Green
    Write-Host ("  " + $ossJson)
    Write-Host ("  " + $ossZip)
    Write-Host ""
    Write-Host "Make objects public-read (or bind CDN). Bench PCs need no token."
} else {
    Write-Host "Next (pick one):"
    Write-Host "  A) Aliyun OSS:  packaging\Publish-HttpChannel.ps1 ... -OssBucket your-bucket -OssEndpoint oss-cn-hangzhou.aliyuncs.com"
    Write-Host "  B) Aliyun ECS:  scp/rsync OutDir to nginx, e.g. /var/www/solarautotest/updates/"
}
