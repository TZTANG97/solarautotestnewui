@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"

REM Upload latest dist zip to EMKU OSS:
REM   bucket  qgongye
REM   prefix  solarautotest/updates
REM Credentials read from E:\EMKU\ENV_环境切换.env (not stored in this repo).

set "ZIP="
for %%F in ("%~dp0..\dist\SolarAutoTest-Setup-*.zip") do set "ZIP=%%~fF"
if not defined ZIP (
  echo [ERR] No dist\SolarAutoTest-Setup-*.zip found. Run build_release.bat first.
  pause
  exit /b 1
)

echo Using zip: %ZIP%
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Publish-HttpChannel.ps1" -ZipPath "%ZIP%" -UseEmkuOss
echo.
pause
