@echo off
setlocal EnableExtensions
chcp 65001 >nul

rem Shared-folder friendly launcher:
rem - code stays on the share
rem - uv.exe is copied to local AppData when needed (UNC exe often blocked)
rem - venv prefers local AppData; falls back to share .venv if local missing (old behavior)

pushd "%~dp0" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Cannot open project directory: %~dp0
    echo If this is a network share, map a drive letter or check permissions.
    pause
    exit /b 1
)

set "LOCAL_ROOT=%LOCALAPPDATA%\SolarAutoTestDev"
set "UV_PROJECT_ENVIRONMENT=%LOCAL_ROOT%\.venv"
set "UV_PYTHON_INSTALL_DIR=%LOCAL_ROOT%\python"
set "UV_CACHE_DIR=%LOCAL_ROOT%\uv-cache"
set "USE_SHARE_VENV=0"

if not exist "%LOCAL_ROOT%" mkdir "%LOCAL_ROOT%" >nul 2>&1
if not exist "%LOCAL_ROOT%" (
    echo [ERROR] Cannot create local directory: %LOCAL_ROOT%
    popd
    pause
    exit /b 1
)

set "PREP_JSON="
for /f "usebackq delims=" %%I in (`powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\prepare_share_launch.ps1" -ProjectRoot "%CD%" -LocalRoot "%LOCAL_ROOT%"`) do set "PREP_JSON=%%I"

set "UV_EXE="
if exist "%LOCAL_ROOT%\uv.exe" set "UV_EXE=%LOCAL_ROOT%\uv.exe"
if not defined UV_EXE if exist "%~dp0tools\uv.exe" set "UV_EXE=%~dp0tools\uv.exe"
if not defined UV_EXE (
    for /f "delims=" %%I in ('where uv.exe 2^>nul') do (
        if not defined UV_EXE set "UV_EXE=%%I"
    )
)

if not defined UV_EXE (
    echo [INFO] uv not found. Trying bootstrap download to local AppData ...
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\bootstrap_uv.ps1"
    if exist "%~dp0tools\uv.exe" (
        copy /Y "%~dp0tools\uv.exe" "%LOCAL_ROOT%\uv.exe" >nul
        set "UV_EXE=%LOCAL_ROOT%\uv.exe"
    )
)

if not defined UV_EXE (
    echo.
    echo [ERROR] uv not found.
    echo Shared-folder tip: on the HOST PC keep tools\uv.exe in the share,
    echo then reopen start_test.bat on this PC - it will copy uv to local AppData.
    echo See tools\README_uv.md
    echo.
    popd
    pause
    exit /b 1
)

if not exist "SCPITestWave.py" (
    echo [ERROR] Missing: %CD%\SCPITestWave.py
    popd
    pause
    exit /b 1
)
if not exist "pyproject.toml" (
    echo [ERROR] Missing: %CD%\pyproject.toml
    popd
    pause
    exit /b 1
)
if not exist "uv.lock" (
    echo [ERROR] Missing: %CD%\uv.lock
    popd
    pause
    exit /b 1
)

rem If this PC never built local venv, reuse share .venv when present (how it used to work).
if not exist "%UV_PROJECT_ENVIRONMENT%\Scripts\python.exe" (
    if exist "%CD%\.venv\Scripts\python.exe" (
        set "UV_PROJECT_ENVIRONMENT=%CD%\.venv"
        set "USE_SHARE_VENV=1"
        echo [WARN] Local venv missing. Using share .venv for compatibility.
        echo [WARN] Prefer one-time: uv sync into %LOCAL_ROOT%\.venv on this PC.
    )
)

echo ============================================================
echo SolarAutoTest test launcher
echo Project: %CD%
echo Runtime: %UV_PROJECT_ENVIRONMENT%
if "%USE_SHARE_VENV%"=="1" echo Mode: share .venv fallback
echo uv: %UV_EXE%
echo ============================================================
echo.

"%UV_EXE%" --version
if errorlevel 1 (
    echo.
    echo [ERROR] uv cannot run: %UV_EXE%
    echo If path is on a network share, Windows may block remote exe.
    echo Fix: ensure %LOCAL_ROOT%\uv.exe exists - launcher copies it automatically.
    popd
    pause
    exit /b 1
)

if /i "%~1"=="--check" (
    echo [OK] Launcher check passed.
    popd
    exit /b 0
)

echo [INFO] Starting...
echo.

"%UV_EXE%" run --frozen python SCPITestWave.py
set "APP_EXIT_CODE=%ERRORLEVEL%"

rem If frozen sync failed on a fresh PC, retry once without --frozen when using local venv.
if not "%APP_EXIT_CODE%"=="0" if "%USE_SHARE_VENV%"=="0" (
    echo.
    echo [WARN] uv run --frozen failed. Retrying uv sync then run ...
    "%UV_EXE%" sync --frozen
    if errorlevel 1 "%UV_EXE%" sync
    "%UV_EXE%" run --frozen python SCPITestWave.py
    set "APP_EXIT_CODE=%ERRORLEVEL%"
)

popd
if not "%APP_EXIT_CODE%"=="0" (
    echo.
    echo [ERROR] Application exited with code %APP_EXIT_CODE%.
    echo Shared-folder checklist:
    echo   1. Host share has tools\uv.exe
    echo   2. This PC can write %LOCALAPPDATA%\SolarAutoTestDev
    echo   3. First run needs network to install deps into local venv
    echo   4. Or keep a working .venv on the share for fallback
    pause
)

exit /b %APP_EXIT_CODE%