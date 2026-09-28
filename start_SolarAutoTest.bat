@echo off
REM 一个快捷方式启动桌面软件；IOT Agent 由软件启动后静默拉起（有 config\solar_agent.json 时）
cd /d "%~dp0"
title SolarAutoTest

REM Prefer installed copy (auto-update). Fallback to this repo for DEV.
set "INSTALL=%LOCALAPPDATA%\SolarAutoTest\Start-SolarAutoTest.bat"
if exist "%INSTALL%" (
  echo 正在打开已安装版本（含自动更新）…
  call "%INSTALL%"
  exit /b %ERRORLEVEL%
)
echo SolarAutoTest DEV 启动中，请稍候…
uv run python SCPITestWave.py
if errorlevel 1 pause
