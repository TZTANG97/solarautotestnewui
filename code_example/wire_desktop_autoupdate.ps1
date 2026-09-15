#Requires -Version 5.1
$ErrorActionPreference = 'Stop'

$install = Join-Path $env:LOCALAPPDATA 'SolarAutoTest'
$ini = Join-Path $install 'config_files\config.ini'
$packCheck = 'E:\solarautotestnewui\packaging\Check-And-Update.ps1'
$dstCheck = Join-Path $install 'Check-And-Update.ps1'
$launcher = Join-Path $install 'Start-SolarAutoTest.bat'
$desktop = [Environment]::GetFolderPath('Desktop')
$repoBat = 'E:\solarautotestnewui\start_SolarAutoTest.bat'

if (-not (Test-Path $install)) {
    throw "Install dir missing: $install  (run packaging install first)"
}

Copy-Item -Force $packCheck $dstCheck

# Rewrite [update] block in config.ini
$lines = @(Get-Content $ini -Encoding UTF8)
$out = New-Object System.Collections.Generic.List[string]
$inUp = $false
$written = $false
foreach ($line in $lines) {
    if ($line -match '^\[update\]\s*$') {
        $inUp = $true
        if (-not $written) {
            $out.Add('[update]')
            $out.Add('enabled = 1')
            $out.Add('auto_install = 1')
            $out.Add('channel = https://qgongye.oss-cn-shanghai.aliyuncs.com/solarautotest/updates')
            $written = $true
        }
        continue
    }
    if ($inUp -and $line -match '^\[') { $inUp = $false }
    if ($inUp) { continue }
    $out.Add($line)
}
if (-not $written) {
    $out.Add('')
    $out.Add('[update]')
    $out.Add('enabled = 1')
    $out.Add('auto_install = 1')
    $out.Add('channel = https://qgongye.oss-cn-shanghai.aliyuncs.com/solarautotest/updates')
}
Set-Content -Path $ini -Value $out -Encoding UTF8

$batLines = @'
@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul
pushd "%~dp0" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Cannot open install directory
    pause
    exit /b 1
)

if exist "%~dp0VERSION" (
    set /p VER=<"%~dp0VERSION"
    echo SolarAutoTest  version: !VER!
) else (
    echo SolarAutoTest
)

if exist "%~dp0Check-And-Update.ps1" (
    echo Checking for updates...
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Check-And-Update.ps1" -InstallDir "%CD%"
)

set "LOCAL_ROOT=%LOCALAPPDATA%\SolarAutoTestRuntime"
set "UV_PROJECT_ENVIRONMENT=%LOCAL_ROOT%\.venv"
set "UV_PYTHON_INSTALL_DIR=%LOCAL_ROOT%\python"
set "UV_CACHE_DIR=%LOCAL_ROOT%\uv-cache"
if not exist "%LOCAL_ROOT%" mkdir "%LOCAL_ROOT%" >nul 2>&1

set "UV_EXE=%~dp0tools\uv.exe"
if not exist "%UV_EXE%" (
    for /f "delims=" %%I in ('where uv.exe 2^>nul') do (
        if not defined UV_EXE set "UV_EXE=%%I"
    )
)
if not exist "%UV_EXE%" (
    echo [ERROR] uv.exe not found. Re-run installer.
    popd
    pause
    exit /b 1
)

echo Install: %CD%
echo Runtime: %UV_PROJECT_ENVIRONMENT%
echo.

if exist "%~dp0config\solar_agent.json" (
  echo [IOT] starting Solar Agent...
  start "SolarAgent" /MIN cmd /c "cd /d %~dp0 && %UV_EXE% run --frozen python -m agent"
)

"%UV_EXE%" run --frozen python SCPITestWave.py
set "EC=%ERRORLEVEL%"
popd
if not "%EC%"=="0" (
    echo [ERROR] Exit code %EC%
    pause
)
exit /b %EC%
'@
Set-Content -Path $launcher -Value $batLines -Encoding ASCII

$icon = Join-Path $install 'ui_files\logo.ico'
$shell = New-Object -ComObject WScript.Shell
$lnkPath = Join-Path $desktop 'SolarAutoTest.lnk'
$lnk = $shell.CreateShortcut($lnkPath)
$lnk.TargetPath = $launcher
$lnk.WorkingDirectory = $install
$lnk.WindowStyle = 1
$lnk.Description = 'SolarAutoTest (check update then launch)'
if (Test-Path $icon) { $lnk.IconLocation = "$icon,0" }
$lnk.Save()

$repoRedirect = @'
@echo off
REM Prefer installed copy (auto-update). Fallback to this repo for dev.
set "INSTALL=%LOCALAPPDATA%\SolarAutoTest\Start-SolarAutoTest.bat"
if exist "%INSTALL%" (
  call "%INSTALL%"
  exit /b %ERRORLEVEL%
)
cd /d "E:\solarautotestnewui"
title SolarAutoTest DEV
uv run python SCPITestWave.py
if errorlevel 1 pause
'@
Set-Content -Path $repoBat -Value $repoRedirect -Encoding ASCII

Write-Host "OK install=$install"
Write-Host "launcher=$launcher"
Write-Host "shortcut=$lnkPath"
Write-Host '--- [update] ---'
Select-String -Path $ini -Pattern '^\[update\]|^enabled|^auto_install|^channel' | ForEach-Object { $_.Line }
if (Test-Path (Join-Path $install 'VERSION')) {
    Write-Host ('VERSION=' + (Get-Content (Join-Path $install 'VERSION') -TotalCount 1))
}
