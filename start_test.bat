@echo off
setlocal EnableExtensions
chcp 65001 >nul

rem Enter the project directory. pushd also supports UNC network paths.
pushd "%~dp0" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Cannot open project directory: %~dp0
    pause
    exit /b 1
)

rem Keep Python, the virtual environment, and the uv cache on this computer.
rem This prevents multiple computers from sharing the repository .venv.
set "LOCAL_ROOT=%LOCALAPPDATA%\SolarAutoTestDev"
set "UV_PROJECT_ENVIRONMENT=%LOCAL_ROOT%\.venv"
set "UV_PYTHON_INSTALL_DIR=%LOCAL_ROOT%\python"
set "UV_CACHE_DIR=%LOCAL_ROOT%\uv-cache"

if not exist "%LOCAL_ROOT%" mkdir "%LOCAL_ROOT%" >nul 2>&1
if not exist "%LOCAL_ROOT%" (
    echo [ERROR] Cannot create local directory: %LOCAL_ROOT%
    popd
    pause
    exit /b 1
)

rem Prefer a portable uv.exe stored with the project, then try uv from PATH.
set "UV_EXE="
if exist "%~dp0tools\uv.exe" set "UV_EXE=%~dp0tools\uv.exe"
if not defined UV_EXE (
    for /f "delims=" %%I in ('where uv.exe 2^>nul') do (
        if not defined UV_EXE set "UV_EXE=%%I"
    )
)

if not defined UV_EXE (
    echo [ERROR] uv was not found.
    echo.
    echo Install uv once and add it to PATH, or copy uv.exe to:
    echo %~dp0tools\uv.exe
    echo.
    popd
    pause
    exit /b 1
)

if not exist "SCPITestWave.py" (
    echo [ERROR] Missing project entry: %CD%\SCPITestWave.py
    popd
    pause
    exit /b 1
)
if not exist "pyproject.toml" (
    echo [ERROR] Missing project file: %CD%\pyproject.toml
    popd
    pause
    exit /b 1
)
if not exist "uv.lock" (
    echo [ERROR] Missing lock file: %CD%\uv.lock
    popd
    pause
    exit /b 1
)

echo ============================================================
echo SolarAutoTest test launcher
echo Project: %CD%
echo Local environment: %UV_PROJECT_ENVIRONMENT%
echo uv: %UV_EXE%
echo ============================================================
echo.

"%UV_EXE%" --version
if errorlevel 1 (
    echo.
    echo [ERROR] uv cannot run: %UV_EXE%
    popd
    pause
    exit /b 1
)

rem Self-check mode validates the launcher without creating the environment.
if /i "%~1"=="--check" (
    echo [OK] Launcher check passed.
    popd
    exit /b 0
)

echo [INFO] Starting with uv. The first run prepares the local environment.
echo [INFO] Later runs reuse the same environment unless uv.lock changes.
echo.

rem Always launch through uv and use the repository lock file without rewriting it.
"%UV_EXE%" run --frozen python SCPITestWave.py
set "APP_EXIT_CODE=%ERRORLEVEL%"

popd
if not "%APP_EXIT_CODE%"=="0" (
    echo.
    echo [ERROR] The application exited with code %APP_EXIT_CODE%.
    echo Review the messages above and the data_logs directory.
    pause
)

exit /b %APP_EXIT_CODE%
