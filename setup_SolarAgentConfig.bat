@echo off
REM 本机 / 其他电脑：生成 config\solar_agent.json（含令牌，不进 Git）
cd /d "%~dp0"
title SolarAgent Setup
echo.
echo 其他电脑下载本仓库后，也在本机运行一次本脚本，填写该台架自己的令牌即可。
echo.
uv run python -m agent.setup_config --interactive
echo.
pause
