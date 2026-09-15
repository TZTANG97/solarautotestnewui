@echo off
REM 独立进程 Solar Agent：出站连 IOT，领任务 / 心跳 / 回传
cd /d "%~dp0"
title SolarAgent
if not exist "config\solar_agent.json" (
  echo [提示] 缺少 config\solar_agent.json，先进入配置向导…
  call "%~dp0setup_SolarAgentConfig.bat"
  if not exist "config\solar_agent.json" (
    echo [ERROR] 仍无配置文件，退出
    pause
    exit /b 1
  )
)
uv run python -c "import json;from pathlib import Path;p=Path('config/solar_agent.json');d=json.loads(p.read_text(encoding='utf-8'));t=(d.get('agent_token') or '').strip();raise SystemExit(0 if t and not t.startswith('请填写') else 1)"
if errorlevel 1 (
  echo [提示] agent_token 为空，请先配置令牌
  call "%~dp0setup_SolarAgentConfig.bat"
)
uv run python -m agent
if errorlevel 1 pause
