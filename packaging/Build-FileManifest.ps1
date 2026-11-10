#Requires -Version 5.1
<#
.SYNOPSIS
  Build content-addressed file manifest + blobs for incremental OSS/LAN updates.

.DESCRIPTION
  Manifest paths are relative to the installed app root (stage\app\* plus a few
  package-root scripts and tools\uv.exe from bundled\uv.exe).
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$StageRoot,
    [Parameter(Mandatory = $true)][string]$ChannelDir,
    [Parameter(Mandatory = $true)][string]$Version,
    [string]$HttpBaseUrl = ""
)

$ErrorActionPreference = "Stop"

function Get-Sha256Lower([string]$Path) {
    $h = Get-FileHash -Algorithm SHA256 -Path $Path
    return $h.Hash.ToLowerInvariant()
}

function Add-ManifestEntry {
    param(
        [System.Collections.ArrayList]$List,
        [hashtable]$BlobMap,
        [string]$AbsPath,
        [string]$RelPath
    )
    if (-not (Test-Path -LiteralPath $AbsPath)) { return }
    $item = Get-Item -LiteralPath $AbsPath -Force
    if ($item.PSIsContainer) { return }
    $sha = Get-Sha256Lower $AbsPath
    $rel = ($RelPath -replace '\\', '/').TrimStart('/')
    [void]$List.Add(@{
        path   = $rel
        sha256 = $sha
        size   = [long]$item.Length
    })
    if (-not $BlobMap.ContainsKey($sha)) {
        $BlobMap[$sha] = $AbsPath
    }
}

$StageRoot = [IO.Path]::GetFullPath($StageRoot)
$ChannelDir = [IO.Path]::GetFullPath($ChannelDir)
$appRoot = Join-Path $StageRoot "app"
if (-not (Test-Path (Join-Path $appRoot "SCPITestWave.py"))) {
    throw "Stage app root missing SCPITestWave.py: $appRoot"
}

$blobsDir = Join-Path $ChannelDir "blobs"
New-Item -ItemType Directory -Force -Path $ChannelDir | Out-Null
New-Item -ItemType Directory -Force -Path $blobsDir | Out-Null

$entries = New-Object System.Collections.ArrayList
$blobMap = @{}

# App tree -> install root
$appRootFull = [IO.Path]::GetFullPath($appRoot).TrimEnd('\', '/')
Get-ChildItem -LiteralPath $appRootFull -Recurse -File -Force -ErrorAction SilentlyContinue | ForEach-Object {
    if (-not $_ -or -not $_.FullName) { return }
    $full = [string]$_.FullName
    if ($full.Length -le $appRootFull.Length) { return }
    $rel = $full.Substring($appRootFull.Length).TrimStart('\', '/')
    if ([string]::IsNullOrWhiteSpace($rel)) { return }
    try {
        Add-ManifestEntry -List $entries -BlobMap $blobMap -AbsPath $full -RelPath $rel
    } catch {
        Write-Host ("[WARN] skip manifest entry: " + $full + " :: " + $_)
    }
}

# Package scripts that live in install root
foreach ($name in @(
    "VERSION",
    "INSTALL.txt",
    "Check-And-Update.ps1",
    "Verify-Install.ps1",
    "Install-SolarAutoTest.ps1",
    "Install-PathHelpers.ps1"
)) {
    $p = Join-Path $StageRoot $name
    Add-ManifestEntry -List $entries -BlobMap $blobMap -AbsPath $p -RelPath $name
}

# bundled uv -> tools/uv.exe
$bundledUv = Join-Path $StageRoot "bundled\uv.exe"
Add-ManifestEntry -List $entries -BlobMap $blobMap -AbsPath $bundledUv -RelPath "tools/uv.exe"

# Materialize blobs (skip copy if already present with same size).
# Use .NET FileInfo: Get-Item -LiteralPath can throw ItemNotFound on some
# existing blob paths under long worktree roots (cmd/[IO.File] still see them).
$copied = 0
$skipped = 0
foreach ($sha in $blobMap.Keys) {
    $src = [string]$blobMap[$sha]
    $dst = Join-Path $blobsDir $sha
    if ([IO.File]::Exists($dst) -and [IO.File]::Exists($src)) {
        $dstLen = (New-Object IO.FileInfo $dst).Length
        $srcLen = (New-Object IO.FileInfo $src).Length
        if ($dstLen -eq $srcLen) {
            $skipped++
            continue
        }
    }
    [IO.File]::Copy($src, $dst, $true)
    $copied++
}

$totalBytes = [long]0
foreach ($e in $entries) { $totalBytes += [long]$e.size }

$manifest = [ordered]@{
    version     = $Version
    built       = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    file_count  = [int]$entries.Count
    total_bytes = $totalBytes
    files       = @($entries.ToArray())
}

$filesName = "files-$Version.json"
$filesLatest = "files-latest.json"
$filesPath = Join-Path $ChannelDir $filesName
$filesLatestPath = Join-Path $ChannelDir $filesLatest
$json = ($manifest | ConvertTo-Json -Depth 6 -Compress)
$utf8 = New-Object System.Text.UTF8Encoding $false
[IO.File]::WriteAllText($filesPath, $json, $utf8)
[IO.File]::WriteAllText($filesLatestPath, $json, $utf8)

$meta = [ordered]@{
    files_name      = $filesLatest
    files_versioned = $filesName
    blobs_dir       = "blobs"
    file_count      = $entries.Count
    total_bytes     = $totalBytes
    blobs_copied    = $copied
    blobs_skipped   = $skipped
}
if ($HttpBaseUrl) {
    $base = $HttpBaseUrl.TrimEnd('/')
    $meta.files_url = "$base/$filesLatest"
    $meta.blobs_base_url = "$base/blobs"
}

Write-Host ("[OK] File manifest: {0} files, {1:N1} MB payload, blobs +{2} / skip {3}" -f `
    $entries.Count, ($totalBytes / 1MB), $copied, $skipped)
if ($meta.files_url) {
    Write-Host ("  files_url: " + $meta.files_url)
    Write-Host ("  blobs:     " + $meta.blobs_base_url)
}
exit 0
