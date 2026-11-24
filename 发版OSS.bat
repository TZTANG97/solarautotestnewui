@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title SolarAutoTest OSS publish

echo.
echo SolarAutoTest: package and upload to OSS
echo Do not close this window.
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0packaging\Build-ReleasePackage.ps1" -PublishEmkuOss
set "RC=%ERRORLEVEL%"

echo.
if not "%RC%"=="0" (
  echo [FAIL] package or upload failed. Exit code %RC%.
) else (
  echo [OK] packaged and uploaded. Benches can update from the OSS channel.
)
echo.
pause
exit /b %RC%
