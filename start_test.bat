@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

rem Shared-folder friendly DEV launcher (align with desktop: auto-install missing env):
rem - code stays on the share / git clone
rem - uv.exe copied to local AppData when needed (UNC exe often blocked)
rem - before start: auto install Python + deps into %%LOCALAPPDATA%%\SolarAutoTestDev
rem - share .venv only as last-resort fallback if auto-install fails

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

rem China-friendly mirrors (same as desktop Start-SolarAutoTest.bat)
if not defined UV_DEFAULT_INDEX set "UV_DEFAULT_INDEX=https://mirrors.aliyun.com/pypi/simple/"
if not defined UV_PYTHON_INSTALL_MIRROR set "UV_PYTHON_INSTALL_MIRROR=https://cdn.npmmirror.com/binaries/python-build-standalone"

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
    if not defined UV_EXE if exist "%LOCAL_ROOT%\uv.exe" set "UV_EXE=%LOCAL_ROOT%\uv.exe"
)

if not defined UV_EXE (
    echo.
    echo [ERROR] uv not found.
    echo Shared-folder tip: on the HOST PC keep tools\uv.exe in the share,
    echo then reopen start_test.bat on this PC - it will copy uv to local AppData.
    echo Or ensure this PC has network to download uv via tools\bootstrap_uv.ps1.
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

echo ============================================================
echo SolarAutoTest test launcher
echo Project: %CD%
echo Runtime: %UV_PROJECT_ENVIRONMENT%
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
    echo [INFO] Preparing runtime for --check ...
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\ensure_dev_runtime.ps1" -UvExe "%UV_EXE%" -ProjectDir "%CD%" -LocalRoot "%LOCAL_ROOT%"
    if errorlevel 1 (
        echo [WARN] ensure_dev_runtime failed; --check still reports uv path above.
    ) else (
        echo [OK] Launcher + runtime check passed.
    )
    popd
    exit /b 0
)

echo [INFO] Preparing Python packages (auto-install if missing, same as desktop)...
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\ensure_dev_runtime.ps1" -UvExe "%UV_EXE%" -ProjectDir "%CD%" -LocalRoot "%LOCAL_ROOT%"
set "SYNC_EC=!ERRORLEVEL!"
if not "!SYNC_EC!"=="0" (
    echo.
    echo [WARN] Auto-install into local runtime failed ^(exit !SYNC_EC!^).
    if exist "%CD%\.venv\Scripts\python.exe" (
        set "UV_PROJECT_ENVIRONMENT=%CD%\.venv"
        set "USE_SHARE_VENV=1"
        echo [WARN] Falling back to share/project .venv: !UV_PROJECT_ENVIRONMENT!
    ) else (
        echo [ERROR] No local runtime and no project .venv fallback.
        echo Checklist:
        echo   1. This PC can write %LOCALAPPDATA%\SolarAutoTestDev
        echo   2. First run needs network ^(China PyPI / Python mirrors^)
        echo   3. Host share has tools\uv.exe when using UNC
        popd
        pause
        exit /b 1
    )
)

if "%USE_SHARE_VENV%"=="1" echo Mode: share .venv fallback
echo [INFO] Starting...
echo.

"%UV_EXE%" run --frozen --offline python SCPITestWave.py
set "APP_EXIT_CODE=%ERRORLEVEL%"

rem If offline run failed ^(stale lock / missing wheel^), one online repair then retry.
if not "%APP_EXIT_CODE%"=="0" if "%USE_SHARE_VENV%"=="0" (
    echo.
    echo [WARN] Offline start failed. Repairing deps then retry ...
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\ensure_dev_runtime.ps1" -UvExe "%UV_EXE%" -ProjectDir "%CD%" -LocalRoot "%LOCAL_ROOT%"
    "%UV_EXE%" run --frozen --offline python SCPITestWave.py
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
