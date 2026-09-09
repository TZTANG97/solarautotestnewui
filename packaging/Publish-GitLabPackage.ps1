#Requires -Version 5.1
<#
.SYNOPSIS
  Upload SolarAutoTest release zip + latest.json to GitLab Generic Package Registry.

.DESCRIPTION
  Uploads:
    packages/generic/solarautotest/<version>/SolarAutoTest-Setup-<version>.zip
    packages/generic/solarautotest/channel/latest.json

  Auth (first hit):
    -CI_JOB_TOKEN / JOB-TOKEN   (recommended: run from GitLab CI — no personal token)
    -GITLAB_TOKEN / PRIVATE-TOKEN
    -SOLARAUTOTEST_GITLAB_TOKEN
    -Deploy Token (username+token via GITLAB_DEPLOY_USER + GITLAB_DEPLOY_TOKEN)

  Bench PCs should NOT need a token: in GitLab project settings enable
  "Allow anyone to pull from Package Registry".
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ZipPath,
    [string]$Version = "",
    [string]$GitLabUrl = "http://gitlab.wisecom-tech.com",
    [string]$ProjectPath = "solarapp/solarautotest/solarautotestnewui",
    [string]$PackageName = "solarautotest",
    [string]$Token = ""
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

$GitLabUrl = $GitLabUrl.TrimEnd('/')
$projectEnc = [uri]::EscapeDataString($ProjectPath)

function Resolve-Token {
    param([string]$Explicit)
    if ($Explicit) {
        $kind = "deploy"
        if ($env:CI_JOB_TOKEN -and ($Explicit.Trim() -eq $env:CI_JOB_TOKEN.Trim())) { $kind = "job" }
        elseif ($env:GITLAB_DEPLOY_USER) { $kind = "deploy" }
        else { $kind = "private" }
        return @{ Kind = $kind; Value = $Explicit.Trim() }
    }
    if ($env:CI_JOB_TOKEN) { return @{ Kind = "job"; Value = $env:CI_JOB_TOKEN.Trim() } }
    if ($env:SOLARAUTOTEST_GITLAB_TOKEN) {
        $kind = if ($env:GITLAB_DEPLOY_USER) { "deploy" } else { "private" }
        return @{ Kind = $kind; Value = $env:SOLARAUTOTEST_GITLAB_TOKEN.Trim() }
    }
    if ($env:GITLAB_DEPLOY_TOKEN) {
        return @{ Kind = "deploy"; Value = $env:GITLAB_DEPLOY_TOKEN.Trim() }
    }
    if ($env:GITLAB_TOKEN) { return @{ Kind = "private"; Value = $env:GITLAB_TOKEN.Trim() } }
    return $null
}

$auth = Resolve-Token $Token
if (-not $auth) {
    Write-Host ""
    Write-Host "[ERROR] No GitLab token for upload." -ForegroundColor Red
    Write-Host "Options (pick one):"
    Write-Host "  1) Preferred: push a tag / run CI job — uses CI_JOB_TOKEN automatically."
    Write-Host "  2) Deploy Token with scopes: write_package_registry + read_package_registry"
    Write-Host "       set GITLAB_DEPLOY_USER=gitlab+deploy-token-N"
    Write-Host "       set SOLARAUTOTEST_GITLAB_TOKEN=<token-password>"
    Write-Host "  3) Personal Access Token with api / write_registry scope."
    Write-Host ""
    Write-Host "Bench PCs still need NO token if Package Registry public pull is enabled."
    exit 1
}

function New-UploadHeaders($Auth) {
    $h = @{ }
    if ($Auth.Kind -eq "job") { $h["JOB-TOKEN"] = $Auth.Value }
    elseif ($Auth.Kind -eq "deploy") { $h["DEPLOY-TOKEN"] = $Auth.Value }
    else { $h["PRIVATE-TOKEN"] = $Auth.Value }
    return $h
}

function Publish-File([string]$PackageVersion, [string]$FilePath, [string]$RemoteName) {
    $url = "{0}/api/v4/projects/{1}/packages/generic/{2}/{3}/{4}" -f `
        $GitLabUrl, $projectEnc, $PackageName, $PackageVersion, $RemoteName
    Write-Host ("PUT " + $url)
    $headers = New-UploadHeaders $auth
    $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
    if ($curl) {
        $headerArgs = @()
        foreach ($k in $headers.Keys) {
            $headerArgs += @("-H", ($k + ": " + $headers[$k]))
        }
        # Prefer --upload-file (GitLab docs); also try Basic if deploy user set
        if ($auth.Kind -eq "deploy" -and $env:GITLAB_DEPLOY_USER) {
            & curl.exe -f -sS -u ($env:GITLAB_DEPLOY_USER + ":" + $auth.Value) --upload-file $FilePath $url
        } else {
            & curl.exe -f -sS @headerArgs --upload-file $FilePath $url
        }
        if ($LASTEXITCODE -ne 0) { throw ("curl upload failed: " + $RemoteName + " exit=" + $LASTEXITCODE) }
    } else {
        $bytes = [IO.File]::ReadAllBytes($FilePath)
        Invoke-RestMethod -Method Put -Uri $url -Headers $headers -Body $bytes -ContentType "application/octet-stream" -TimeoutSec 600
    }
    return $url
}

$sizeMb = [math]::Round((Get-Item $ZipPath).Length / 1MB, 1)
$zipName = "SolarAutoTest-Setup-" + $Version + ".zip"
# Ensure remote name matches versioned convention even if local filename differs
$tmpZip = $ZipPath
if ([IO.Path]::GetFileName($ZipPath) -ne $zipName) {
    $tmpZip = Join-Path $env:TEMP $zipName
    Copy-Item -Force $ZipPath $tmpZip
}

$zipUrl = Publish-File $Version $tmpZip $zipName
$zipBase = $zipUrl.Substring(0, $zipUrl.LastIndexOf('/'))

$manifest = [ordered]@{
    version      = $Version
    zip_name     = $zipName
    zip_url      = $zipUrl
    zip_base_url = $zipBase
    built        = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    size_mb      = $sizeMb
    project      = $ProjectPath
    package      = $PackageName
}
$jsonPath = Join-Path $env:TEMP ("solarautotest-latest-" + [guid]::NewGuid().ToString("N") + ".json")
($manifest | ConvertTo-Json) | Out-File -FilePath $jsonPath -Encoding ascii
$latestUrl = Publish-File "channel" $jsonPath "latest.json"

Write-Host ""
Write-Host "[OK] Published to GitLab Package Registry" -ForegroundColor Green
Write-Host ("  version:  " + $Version)
Write-Host ("  zip:      " + $zipUrl)
Write-Host ("  manifest: " + $latestUrl)
Write-Host ""
Write-Host "Client channel (config.ini):"
Write-Host ("  channel = " + $GitLabUrl + "/api/v4/projects/" + $projectEnc + "/packages/generic/" + $PackageName + "/channel")
Write-Host ""
Write-Host "One-time GitLab UI (so bench PCs need NO token):"
Write-Host "  Project → Settings → General → Visibility → Allow anyone to pull from Package Registry"
