param([string]$InstallDir = "", [switch]$SkipVerify, [switch]$SkipSync)
$ErrorActionPreference = "Stop"
$packageRoot = $PSScriptRoot
if (-not $InstallDir) { throw "InstallDir required" }
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
$app = Join-Path $packageRoot "app"
if (Test-Path $app) {
  Copy-Item -Recurse -Force (Join-Path $app "*") $InstallDir
}
Copy-Item -Force (Join-Path $packageRoot "VERSION") (Join-Path $InstallDir "VERSION")
Copy-Item -Force (Join-Path $packageRoot "Check-And-Update.ps1") (Join-Path $InstallDir "Check-And-Update.ps1") -ErrorAction SilentlyContinue
Write-Host ("[E2E] Installed into " + $InstallDir)
exit 0
