@echo off
setlocal EnableExtensions
chcp 65001 >nul
title SolarAutoTest Installer

cd /d "%~dp0"
echo ============================================================
echo  SolarAutoTest Installer
echo ============================================================
echo  You can choose App / Data / Runtime folders (not only C:).
echo  Tip: install.bat -InstallDir D:\SolarAutoTest -Quiet
echo.

set "PS_EXE=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%PS_EXE%" set "PS_EXE=powershell.exe"

"%PS_EXE%" -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-SolarAutoTest.ps1" %*
set "EC=%ERRORLEVEL%"
echo.
if not "%EC%"=="0" (
    echo [FAIL] Install failed, exit code %EC%
    pause
    exit /b %EC%
)
echo [OK] Install finished. Use desktop shortcut "SolarAutoTest" to start.
pause
exit /b 0
