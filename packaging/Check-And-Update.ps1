#Requires -Version 5.1
<#
.SYNOPSIS
  Check update channel (LAN folder or HTTP/GitLab Package) and upgrade before launch.

.DESCRIPTION
  Reads channel from (first hit wins):
    1) env SOLARAUTOTEST_UPDATE_CHANNEL
    2) <InstallDir>\config_files\config.ini  [update] channel=
    3) <InstallDir>\update_channel.txt

  LAN channel: folder with latest.json + zip.
  HTTP channel: URL to latest.json, or a directory URL that contains latest.json
    (GitLab Generic Package "channel" package version recommended).

  Optional auth (only if Package Registry is private):
    env SOLARAUTOTEST_UPDATE_TOKEN / GITLAB_TOKEN / CI_JOB_TOKEN
    or config.ini [update] token=
  Prefer enabling "Allow anyone to pull from Package Registry" so bench PCs need no token.
#>
[CmdletBinding()]
param(
    [string]$InstallDir = "",
    [switch]$AutoYes,
    [switch]$Quiet
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

try {
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [Console]::OutputEncoding
    chcp 65001 | Out-Null
} catch {}

function Info([string]$m) { if (-not $Quiet) { Write-Host $m } }
function Warn([string]$m) { Write-Host ("[WARN] " + $m) -ForegroundColor Yellow }
function Ok([string]$m) { Write-Host ("[OK] " + $m) -ForegroundColor Green }

function Get-IniValue([string]$Path, [string]$Section, [string]$Key) {
    if (-not (Test-Path $Path)) { return $null }
    $inSection = $false
    foreach ($raw in Get-Content -Path $Path -Encoding UTF8 -ErrorAction SilentlyContinue) {
        $line = $raw.Trim()
        if (-not $line -or $line.StartsWith("#") -or $line.StartsWith(";")) { continue }
        if ($line -match '^\[(.+)\]$') {
            $inSection = ($Matches[1].Trim().ToLowerInvariant() -eq $Section.ToLowerInvariant())
            continue
        }
        if (-not $inSection) { continue }
        $parts = $line.Split("=", 2)
        if ($parts.Count -lt 2) { continue }
        if ($parts[0].Trim().ToLowerInvariant() -eq $Key.ToLowerInvariant()) {
            return $parts[1].Trim()
        }
    }
    return $null
}

function Read-LocalVersion([string]$Root) {
    $p = Join-Path $Root "VERSION"
    if (-not (Test-Path $p)) { return "" }
    $line = (Get-Content -Path $p -TotalCount 1 -ErrorAction SilentlyContinue)
    if ($line) { return $line.Trim() }
    return ""
}

function Resolve-Channel([string]$Root) {
    if ($env:SOLARAUTOTEST_UPDATE_CHANNEL) {
        return $env:SOLARAUTOTEST_UPDATE_CHANNEL.Trim()
    }
    $ini = Join-Path $Root "config_files\config.ini"
    $ch = Get-IniValue $ini "update" "channel"
    if ($ch) { return $ch }
    $txt = Join-Path $Root "update_channel.txt"
    if (Test-Path $txt) {
        $line = (Get-Content -Path $txt -TotalCount 1 -ErrorAction SilentlyContinue)
        if ($line) { return $line.Trim() }
    }
    return ""
}

function Resolve-UpdateToken([string]$Root) {
    foreach ($k in @(
        $env:SOLARAUTOTEST_UPDATE_TOKEN,
        $env:GITLAB_TOKEN,
        $env:GITLAB_DEPLOY_TOKEN,
        $env:CI_JOB_TOKEN
    )) {
        if ($k -and $k.Trim()) { return $k.Trim() }
    }
    $ini = Join-Path $Root "config_files\config.ini"
    $t = Get-IniValue $ini "update" "token"
    if ($t) { return $t.Trim() }
    return ""
}

function New-HttpHeaders([string]$Token) {
    $h = @{
        "Accept" = "application/json, application/octet-stream, */*"
    }
    if (-not $Token) { return $h }
    # Deploy Token / Personal / Project Access → PRIVATE-TOKEN
    # CI Job Token → JOB-TOKEN
    if ($env:CI_JOB_TOKEN -and ($Token -eq $env:CI_JOB_TOKEN)) {
        $h["JOB-TOKEN"] = $Token
    } else {
        $h["PRIVATE-TOKEN"] = $Token
    }
    return $h
}

function Is-HttpChannel([string]$Channel) {
    return $Channel -match '^https?://'
}

function Get-ManifestUrl([string]$Channel) {
    $c = $Channel.TrimEnd('/')
    if ($c.ToLowerInvariant().EndsWith("latest.json")) { return $c }
    return ($c + "/latest.json")
}

function Is-UpdateEnabled([string]$Root) {
    if ($env:SOLARAUTOTEST_UPDATE_DISABLE -eq "1") { return $false }
    $ini = Join-Path $Root "config_files\config.ini"
    $v = Get-IniValue $ini "update" "enabled"
    if ($null -eq $v -or $v -eq "") { return $true }
    $v = $v.Trim().ToLowerInvariant()
    return @("1", "true", "yes", "on") -contains $v
}

function Is-AutoInstall([string]$Root) {
    if ($AutoYes) { return $true }
    if ($env:SOLARAUTOTEST_UPDATE_AUTO -eq "1") { return $true }
    $ini = Join-Path $Root "config_files\config.ini"
    $v = Get-IniValue $ini "update" "auto_install"
    if (-not $v) { return $false }
    $v = $v.Trim().ToLowerInvariant()
    return @("1", "true", "yes", "on") -contains $v
}

function Compare-VersionTag([string]$A, [string]$B) {
    $na = 0L; $nb = 0L
    $pa = ($A -replace '[^\d]', '')
    $pb = ($B -replace '[^\d]', '')
    [void][long]::TryParse($pa, [ref]$na)
    [void][long]::TryParse($pb, [ref]$nb)
    if ($na -eq $nb) { return 0 }
    if ($na -gt $nb) { return 1 }
    return -1
}

function Get-RemoteManifest([string]$Channel, [string]$Token) {
    if (Is-HttpChannel $Channel) {
        $url = Get-ManifestUrl $Channel
        Info ("Fetching manifest: " + $url)
        $headers = New-HttpHeaders $Token
        try {
            $resp = Invoke-WebRequest -Uri $url -Headers $headers -UseBasicParsing -TimeoutSec 60
        } catch {
            throw ("Cannot download latest.json: " + $_.Exception.Message)
        }
        $raw = [string]$resp.Content
        if ($raw.Length -gt 0 -and [int][char]$raw[0] -eq 0xFEFF) {
            $raw = $raw.Substring(1)
        }
        $raw = $raw.TrimStart([char]0xFEFF)
        return ($raw | ConvertFrom-Json)
    }

    if (-not (Test-Path $Channel)) {
        throw ("Update channel not reachable: " + $Channel)
    }
    $manifestPath = Join-Path $Channel "latest.json"
    if (-not (Test-Path $manifestPath)) {
        throw ("latest.json missing in channel: " + $Channel)
    }
    $raw = Get-Content -Path $manifestPath -Raw -Encoding UTF8
    if ($raw.Length -gt 0 -and [int][char]$raw[0] -eq 0xFEFF) {
        $raw = $raw.Substring(1)
    }
    return ($raw | ConvertFrom-Json)
}

function Resolve-ZipSource([string]$Channel, $Manifest) {
    $zipName = [string]$Manifest.zip_name
    $zipUrl = [string]$Manifest.zip_url
    if ($zipUrl) {
        return @{ Mode = "http"; Uri = $zipUrl; Name = $(if ($zipName) { $zipName } else { [IO.Path]::GetFileName(($zipUrl -split '\?')[0]) }) }
    }
    if (-not $zipName) {
        throw "latest.json missing zip_name/zip_url"
    }
    if (Is-HttpChannel $Channel) {
        # Prefer zip_base_url from manifest (package version folder for the build)
        $base = [string]$Manifest.zip_base_url
        if (-not $base) {
            # Same directory as latest.json
            $murl = Get-ManifestUrl $Channel
            $base = $murl.Substring(0, $murl.LastIndexOf('/'))
        }
        $base = $base.TrimEnd('/')
        return @{ Mode = "http"; Uri = ($base + "/" + $zipName); Name = $zipName }
    }
    $path = Join-Path $Channel $zipName
    return @{ Mode = "file"; Path = $path; Name = $zipName }
}

function Get-ZipToTemp($Source, [string]$Token, [string]$WorkDir) {
    $localZip = Join-Path $WorkDir $Source.Name
    if ($Source.Mode -eq "file") {
        if (-not (Test-Path $Source.Path)) {
            throw ("Zip not found: " + $Source.Path)
        }
        Info ("Copying package (" + $Source.Name + ") ...")
        Copy-Item -Force $Source.Path $localZip
        return $localZip
    }
    Info ("Downloading package (" + $Source.Name + ") ...")
    Info ("  " + $Source.Uri)
    $headers = New-HttpHeaders $Token
    Invoke-WebRequest -Uri $Source.Uri -Headers $headers -OutFile $localZip -UseBasicParsing -TimeoutSec 600
    if (-not (Test-Path $localZip) -or ((Get-Item $localZip).Length -lt 1000)) {
        throw "Downloaded zip looks empty/invalid"
    }
    return $localZip
}

if (-not $InstallDir) {
    $InstallDir = $PSScriptRoot
}
$InstallDir = [System.IO.Path]::GetFullPath($InstallDir)

if (-not (Is-UpdateEnabled $InstallDir)) {
    Info "Update check disabled."
    exit 0
}

$channel = Resolve-Channel $InstallDir
if (-not $channel) {
    Info "No update channel configured; skip."
    exit 0
}
if ($channel -match 'YOUR-SERVER|CHANGE_ME|example\.com|YOUR-GITLAB') {
    Info "Update channel is placeholder; skip."
    exit 0
}

$token = Resolve-UpdateToken $InstallDir

try {
    $manifest = Get-RemoteManifest $channel $token
} catch {
    Warn $_.Exception.Message
    exit 0
}

$remoteVer = [string]$manifest.version
if (-not $remoteVer) {
    Warn "latest.json missing version"
    exit 0
}

$localVer = Read-LocalVersion $InstallDir
if (-not $localVer) { $localVer = "0" }

if ((Compare-VersionTag $remoteVer $localVer) -le 0) {
    Info ("Up to date. local=" + $localVer + " remote=" + $remoteVer)
    exit 0
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ("  New version available: " + $localVer + "  ->  " + $remoteVer) -ForegroundColor Cyan
Write-Host ("  Channel: " + $channel) -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$doInstall = Is-AutoInstall $InstallDir
if (-not $doInstall) {
    $ans = Read-Host "Upgrade now? [Y/n]"
    if ($ans -and $ans.Trim().ToLowerInvariant().StartsWith("n")) {
        Info "Skipped upgrade."
        exit 0
    }
}

$work = Join-Path $env:TEMP ("SolarAutoTest-update-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $work -Force | Out-Null

try {
    $src = Resolve-ZipSource $channel $manifest
    $localZip = Get-ZipToTemp $src $token $work

    Info "Extracting ..."
    Expand-Archive -Path $localZip -DestinationPath $work -Force

    $setupRoot = $work
    $installPs1 = Join-Path $setupRoot "Install-SolarAutoTest.ps1"
    if (-not (Test-Path $installPs1)) {
        $hit = Get-ChildItem $work -Filter "Install-SolarAutoTest.ps1" -Recurse -ErrorAction SilentlyContinue |
            Select-Object -First 1
        if ($hit) {
            $setupRoot = $hit.Directory.FullName
            $installPs1 = $hit.FullName
        }
    }
    if (-not (Test-Path $installPs1)) {
        throw "Install-SolarAutoTest.ps1 not found inside zip"
    }

    Info ("Installing into " + $InstallDir + " ...")
    $args = @(
        "-NoProfile", "-ExecutionPolicy", "Bypass",
        "-File", $installPs1,
        "-InstallDir", $InstallDir,
        "-SkipVerify"
    )
    $p = Start-Process -FilePath "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" `
        -ArgumentList $args -Wait -PassThru -NoNewWindow
    if ($p.ExitCode -ne 0) {
        throw ("Installer exit code " + $p.ExitCode)
    }

    Ok ("Upgraded to " + $remoteVer)
    exit 0
}
catch {
    Warn ("Upgrade failed: " + $_.Exception.Message)
    if (Is-HttpChannel $channel -and -not $token) {
        Warn "If the project is private, enable Package Registry public pull in GitLab,"
        Warn "or set [update] token= (Deploy Token read_package_registry) on this PC."
    }
    exit 1
}
finally {
    try { Remove-Item -Recurse -Force $work -ErrorAction SilentlyContinue } catch {}
}
