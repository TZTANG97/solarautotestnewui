#Requires -Version 5.1
$ErrorActionPreference = "Stop"
$repo = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
if (-not (Test-Path (Join-Path $repo "packaging\Check-And-Update.ps1"))) {
    $repo = "E:\solarautotestnewui"
}
$src = Join-Path $repo "packaging\Check-And-Update.ps1"
$tok = $null
$err = $null
[void][System.Management.Automation.Language.Parser]::ParseFile($src, [ref]$tok, [ref]$err)
if ($err -and $err.Count) {
    $err | ForEach-Object { $_.ToString() }
    exit 1
}
Write-Host "OK parse Check-And-Update.ps1"

$install = Join-Path $env:LOCALAPPDATA "SolarAutoTest"
if (-not (Test-Path $install)) {
    Write-Host "no local install at $install"
    exit 0
}
Copy-Item -Force $src (Join-Path $install "Check-And-Update.ps1")
Write-Host "copied Check-And-Update.ps1 -> $install"

$bat = Join-Path $install "Start-SolarAutoTest.bat"
if (Test-Path $bat) {
    $c = Get-Content $bat -Raw
    $c2 = $c -replace "-WindowStyle Hidden ", ""
    if ($c -ne $c2) {
        Set-Content -Path $bat -Value $c2 -Encoding ASCII
        Write-Host "patched Start-SolarAutoTest.bat: removed Hidden"
    } else {
        Write-Host "Start-SolarAutoTest.bat already visible (no Hidden)"
    }
}
Write-Host "done"
