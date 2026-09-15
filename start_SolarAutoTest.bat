@echo off
REM 一个快捷方式：有 IOT Agent 配置则后台拉起 Agent，再启动桌面软件
cd /d "%~dp0"

if exist "%~dp0config\solar_agent.json" (
  echo [IOT] 后台启动 Solar Agent...
  start "SolarAgent" /MIN cmd /c "cd /d %~dp0 && uv run python -m agent"
) else (
  echo [IOT] 未找到 config\solar_agent.json，跳过 Agent（需要时运行 setup_SolarAgentConfig.bat）
)

REM Prefer installed copy (auto-update). Fallback to this repo for DEV.
set "INSTALL=%LOCALAPPDATA%\SolarAutoTest\Start-SolarAutoTest.bat"
if exist "%INSTALL%" (
  call "%INSTALL%"
  exit /b %ERRORLEVEL%
)
title SolarAutoTest DEV
uv run python SCPITestWave.py
if errorlevel 1 pause
