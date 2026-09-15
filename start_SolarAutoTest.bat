@echo off
REM 一个快捷方式启动桌面软件；IOT Agent 由软件启动后静默拉起（有 config\solar_agent.json 时）
cd /d "%~dp0"

REM Prefer installed copy (auto-update). Fallback to this repo for DEV.
set "INSTALL=%LOCALAPPDATA%\SolarAutoTest\Start-SolarAutoTest.bat"
if exist "%INSTALL%" (
  call "%INSTALL%"
  exit /b %ERRORLEVEL%
)
title SolarAutoTest DEV
uv run python SCPITestWave.py
if errorlevel 1 pause
