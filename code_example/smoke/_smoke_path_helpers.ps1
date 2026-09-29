# -*- coding: utf-8 -*-
# quick smoke for Install-PathHelpers (run via powershell)
$ErrorActionPreference = "Stop"
. "E:\solarautotestnewui\packaging\Install-PathHelpers.ps1"
Set-UvDownloadMirrors
Write-Host ("index=" + $env:UV_DEFAULT_INDEX)
Write-Host ("py=" + $env:UV_PYTHON_INSTALL_MIRROR)
$r = Find-ReusableUvRuntime ""
Write-Host ("donor=" + $r)
Write-Host ("ready_preferred=" + (Test-UvRuntimeReady $r))
