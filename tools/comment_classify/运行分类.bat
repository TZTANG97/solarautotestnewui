@echo off
chcp 65001 >nul
title 评论采集数据分类工具
cd /d "%~dp0"

echo ========================================
echo   评论采集数据分类工具
echo ========================================
echo.

REM ---- 查找 Python ----
set "PY="
where py >nul 2>&1 && set "PY=py -3"
if not defined PY where python >nul 2>&1 && set "PY=python"
if not defined PY where python3 >nul 2>&1 && set "PY=python3"

if not defined PY (
    echo [错误] 未检测到 Python。
    echo 请先安装 Python 3.10+ ：https://www.python.org/downloads/
    echo 安装时勾选 "Add python.exe to PATH"
    echo.
    pause
    exit /b 1
)

echo [环境] 使用: %PY%
%PY% --version
echo.

REM ---- 自动安装依赖（已安装则很快跳过）----
echo [依赖] 检查 pandas / openpyxl ...
%PY% -c "import pandas, openpyxl" >nul 2>&1
if errorlevel 1 (
    echo [依赖] 首次运行，正在安装依赖，请稍候...
    %PY% -m pip install --upgrade pip -q
    %PY% -m pip install pandas openpyxl -q
    if errorlevel 1 (
        echo [错误] 依赖安装失败，请检查网络后重试。
        pause
        exit /b 1
    )
    echo [依赖] 安装完成
) else (
    echo [依赖] 已就绪
)
echo.

REM ---- 运行：支持拖拽文件到 bat 上 ----
if "%~1"=="" (
    echo 未拖入文件，将弹出选择框...
    echo.
    %PY% "%~dp0classify_comments.py"
) else (
    echo 输入文件: %~1
    echo.
    %PY% "%~dp0classify_comments.py" "%~1"
)

echo.
if errorlevel 1 (
    echo 运行失败，请查看上方报错。
) else (
    echo 可直接打开同目录下的「*_分类结果.xlsx」查看。
)
echo.
pause
