@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"

REM Usage:
REM   build_release.bat -PublishEmkuOss
REM   build_release.bat -PublishDir \\server\share\SolarAutoTest\updates
REM   build_release.bat -PublishGitLab
REM Or set env once:
REM   set SOLARAUTOTEST_PUBLISH_EMKU_OSS=1
REM   set SOLARAUTOTEST_PUBLISH_DIR=\\server\share\SolarAutoTest\updates

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Build-ReleasePackage.ps1" %*
echo.
pause
