#Requires -Version 5.1
<#
.SYNOPSIS
  Install SolarAutoTest to this PC (local copy + uv + venv).
#>
[CmdletBinding()]
param(
    [string]$InstallDir = "",
    [switch]$SkipShortcut,
    [switch]$SkipSync,
    [switch]$SkipVerify,
    [switch]$Quiet
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Write-Step([string]$Message) {
    Write-Host ""
    Write-Host ("==> " + $Message) -ForegroundColor Cyan
}

function Write-Ok([string]$Message) {
    Write-Host ("[OK] " + $Message) -ForegroundColor Green
}

function Write-WarnLine([string]$Message) {
    Write-Host ("[WARN] " + $Message) -ForegroundColor Yellow
}

function Get-PackageRoot {
    return [System.IO.Path]::GetFullPath($PSScriptRoot)
}

function Get-SourceAppDir {
    $root = Get-PackageRoot
    $bundled = Join-Path $root "app"
    if (Test-Path (Join-Path $bundled "SCPITestWave.py")) {
        return $bundled
    }
    $repo = [System.IO.Path]::GetFullPath((Join-Path $root ".."))
    if (Test-Path (Join-Path $repo "SCPITestWave.py")) {
        return $repo
    }
    throw "App source not found. Run from the release package, or from repo packaging/."
}

function Ensure-Directory([string]$Path) {
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Copy-AppFiles([string]$Source, [string]$Destination) {
    Ensure-Directory $Destination
    $excludeDirNames = @(
        ".git", ".venv", ".idea", ".vscode", ".cursor", ".claude",
        "__pycache__", ".pytest_cache", "packaging", "dist",
        "data_logs", "uv-cache", "node_modules", "command_save_files"
    )
    $excludeFileGlobs = @(
        "*.pyc", "*.pyo", "*.log", "log.txt", "status.json",
        "*.zip", "*.7z"
    )

    Write-Step ("Copying app files to " + $Destination)
    $xd = @()
    foreach ($n in $excludeDirNames) { $xd += @("/XD", $n) }
    $xf = @()
    foreach ($g in $excludeFileGlobs) { $xf += @("/XF", $g) }

    $rcArgs = @(
        $Source, $Destination, "/E", "/NFL", "/NDL", "/NJH", "/NJS", "/NC", "/NS", "/NP",
        "/R:1", "/W:1"
    ) + $xd + $xf

    & robocopy @rcArgs | Out-Null
    $code = $LASTEXITCODE
    if ($code -ge 8) {
        throw ("Copy failed, robocopy exit code " + $code)
    }
    if (-not (Test-Path (Join-Path $Destination "SCPITestWave.py"))) {
        throw "Missing SCPITestWave.py after copy"
    }
    if (-not (Test-Path (Join-Path $Destination "uv.lock"))) {
        throw "Missing uv.lock after copy"
    }
    Write-Ok "App files copied"
}

function Find-UvExe([string]$InstallRoot) {
    $candidates = @(
        (Join-Path $InstallRoot "tools\uv.exe"),
        (Join-Path (Get-PackageRoot) "bundled\uv.exe"),
        (Join-Path (Get-PackageRoot) "tools\uv.exe")
    )
    foreach ($c in $candidates) {
        if ($c -and (Test-Path $c)) { return $c }
    }
    $cmd = Get-Command uv.exe -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    return $null
}

function Install-PortableUv([string]$InstallRoot) {
    $tools = Join-Path $InstallRoot "tools"
    Ensure-Directory $tools
    $target = Join-Path $tools "uv.exe"

    $bundled = Join-Path (Get-PackageRoot) "bundled\uv.exe"
    if (Test-Path $bundled) {
        Write-Step "Using bundled uv from package"
        Copy-Item -Force $bundled $target
        return $target
    }

    Write-Step "Downloading portable uv (network required)"
    $zipUrl = "https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip"
    $tmpZip = Join-Path $env:TEMP ("uv-win-" + [guid]::NewGuid().ToString() + ".zip")
    $tmpDir = Join-Path $env:TEMP ("uv-extract-" + [guid]::NewGuid().ToString())
    try {
        Invoke-WebRequest -Uri $zipUrl -OutFile $tmpZip -UseBasicParsing
        Ensure-Directory $tmpDir
        Expand-Archive -Path $tmpZip -DestinationPath $tmpDir -Force
        $found = Get-ChildItem -Path $tmpDir -Filter "uv.exe" -Recurse | Select-Object -First 1
        if (-not $found) { throw "uv.exe not found in download" }
        Copy-Item -Force $found.FullName $target
        Write-Ok ("uv installed to " + $target)
        return $target
    }
    catch {
        Write-WarnLine ("GitHub download failed: " + $_.Exception.Message)
        Write-Step "Trying official install script"
        $installPs1 = Join-Path $env:TEMP ("uv-install-" + [guid]::NewGuid().ToString() + ".ps1")
        Invoke-WebRequest -Uri "https://astral.sh/uv/install.ps1" -OutFile $installPs1 -UseBasicParsing
        $env:UV_INSTALL_DIR = $tools
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $installPs1
        if (-not (Test-Path $target)) {
            $alt = Join-Path $tools "bin\uv.exe"
            if (Test-Path $alt) {
                Copy-Item -Force $alt $target
            }
        }
        if (-not (Test-Path $target)) {
            throw "Cannot install uv automatically. See https://docs.astral.sh/uv/"
        }
        return $target
    }
    finally {
        Remove-Item -Force $tmpZip -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force $tmpDir -ErrorAction SilentlyContinue
    }
}

function Ensure-Uv([string]$InstallRoot) {
    $uv = Find-UvExe $InstallRoot
    if ($uv) {
        Write-Ok ("Found uv: " + $uv)
        $local = Join-Path $InstallRoot "tools\uv.exe"
        if ($uv -ne $local) {
            Ensure-Directory (Split-Path $local)
            try { Copy-Item -Force $uv $local; $uv = $local } catch { }
        }
        return $uv
    }
    return Install-PortableUv $InstallRoot
}

function Write-Launcher([string]$InstallRoot) {
    $launcher = Join-Path $InstallRoot "Start-SolarAutoTest.bat"
    $lines = @(
        "@echo off",
        "setlocal EnableExtensions",
        "chcp 65001 >nul",
        "pushd `"%~dp0`" >nul 2>&1",
        "if errorlevel 1 (",
        "    echo [ERROR] Cannot open install directory",
        "    pause",
        "    exit /b 1",
        ")",
        "",
        "REM LAN auto-update (before app starts, so files are not locked)",
        "if exist `"%~dp0Check-And-Update.ps1`" (",
        "    echo Checking for updates...",
        "    powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"%~dp0Check-And-Update.ps1`" -InstallDir `"%CD%`"",
        ")",
        "",
        "set `"LOCAL_ROOT=%LOCALAPPDATA%\SolarAutoTestRuntime`"",
        "set `"UV_PROJECT_ENVIRONMENT=%LOCAL_ROOT%\.venv`"",
        "set `"UV_PYTHON_INSTALL_DIR=%LOCAL_ROOT%\python`"",
        "set `"UV_CACHE_DIR=%LOCAL_ROOT%\uv-cache`"",
        "if not exist `"%LOCAL_ROOT%`" mkdir `"%LOCAL_ROOT%`" >nul 2>&1",
        "",
        "set `"UV_EXE=%~dp0tools\uv.exe`"",
        "if not exist `"%UV_EXE%`" (",
        "    for /f `"delims=`" %%I in ('where uv.exe 2^>nul') do (",
        "        if not defined UV_EXE set `"UV_EXE=%%I`"",
        "    )",
        ")",
        "if not exist `"%UV_EXE%`" (",
        "    echo [ERROR] uv.exe not found. Re-run installer.",
        "    popd",
        "    pause",
        "    exit /b 1",
        ")",
        "",
        "echo SolarAutoTest",
        "echo Install: %CD%",
        "echo Runtime: %UV_PROJECT_ENVIRONMENT%",
        "echo.",
        "",
        "REM IOT Agent is started silently by SCPITestWave when config\\solar_agent.json exists",
        "",
        "`"%UV_EXE%`" run --frozen python SCPITestWave.py",
        "set `"EC=%ERRORLEVEL%`"",
        "popd",
        "if not `"%EC%`"==`"0`" (",
        "    echo [ERROR] Exit code %EC%",
        "    pause",
        ")",
        "exit /b %EC%"
    )
    Set-Content -Path $launcher -Value $lines -Encoding ASCII
    Write-Ok ("Launcher written: " + $launcher)
    return $launcher
}

function Resolve-AppIcon([string]$InstallRoot) {
    $candidates = @(
        (Join-Path $InstallRoot "ui_files\logo.ico"),
        (Join-Path $InstallRoot "ui_files\logo.jpg"),
        (Join-Path $InstallRoot "logo.ico")
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) { return $c }
    }
    return $null
}

function New-AppShortcut([string]$TargetBat, [string]$InstallRoot) {
    $desktop = [Environment]::GetFolderPath("Desktop")
    $startMenu = Join-Path ([Environment]::GetFolderPath("StartMenu")) "Programs\SolarAutoTest"
    Ensure-Directory $startMenu

    $iconPath = Resolve-AppIcon $InstallRoot
    $wsh = New-Object -ComObject WScript.Shell
    foreach ($dir in @($desktop, $startMenu)) {
        $lnkPath = Join-Path $dir "SolarAutoTest.lnk"
        $sc = $wsh.CreateShortcut($lnkPath)
        $sc.TargetPath = $TargetBat
        $sc.WorkingDirectory = $InstallRoot
        $sc.WindowStyle = 1
        $sc.Description = "SolarAutoTest"
        if ($iconPath) {
            # Windows shortcuts prefer .ico; jpg may show blank on some builds
            $sc.IconLocation = ($iconPath + ",0")
        }
        $sc.Save()
        Write-Ok ("Shortcut: " + $lnkPath)
    }
    if ($iconPath) {
        Write-Ok ("Shortcut icon: " + $iconPath)
    } else {
        Write-WarnLine "App icon not found (ui_files\logo.ico / logo.jpg)"
    }
}

function Invoke-UvSync([string]$InstallRoot, [string]$UvExe) {
    Write-Step "Syncing Python environment (first run may take several minutes)"
    $runtime = Join-Path $env:LOCALAPPDATA "SolarAutoTestRuntime"
    Ensure-Directory $runtime
    $env:UV_PROJECT_ENVIRONMENT = Join-Path $runtime ".venv"
    $env:UV_PYTHON_INSTALL_DIR = Join-Path $runtime "python"
    $env:UV_CACHE_DIR = Join-Path $runtime "uv-cache"
    Ensure-Directory $env:UV_PROJECT_ENVIRONMENT
    Ensure-Directory $env:UV_PYTHON_INSTALL_DIR
    Ensure-Directory $env:UV_CACHE_DIR

    Push-Location $InstallRoot
    try {
        & $UvExe --version
        & $UvExe sync --frozen
        if ($LASTEXITCODE -ne 0) {
            Write-WarnLine "uv sync --frozen failed, trying uv sync"
            & $UvExe sync
            if ($LASTEXITCODE -ne 0) {
                throw ("uv sync failed, exit code " + $LASTEXITCODE)
            }
        }
        Write-Ok "Dependencies synced"
    }
    finally {
        Pop-Location
    }
}

function Get-AppVersion([string]$Root) {
    foreach ($rel in @("VERSION", "app\VERSION")) {
        $p = Join-Path $Root $rel
        if (Test-Path $p) {
            $line = (Get-Content -Path $p -TotalCount 1 -ErrorAction SilentlyContinue)
            if ($line) { return $line.Trim() }
        }
    }
    return ""
}

function Get-FileHashSafe([string]$Path) {
    if (-not (Test-Path $Path)) { return "" }
    try {
        return (Get-FileHash -Path $Path -Algorithm SHA256).Hash
    } catch {
        return ""
    }
}

$packageRoot = Get-PackageRoot
$source = Get-SourceAppDir

if (-not $InstallDir) {
    $InstallDir = Join-Path $env:LOCALAPPDATA "SolarAutoTest"
}
$InstallDir = [System.IO.Path]::GetFullPath($InstallDir)

$newVersion = Get-AppVersion $packageRoot
if (-not $newVersion) { $newVersion = Get-AppVersion $source }
$oldVersion = ""
$isUpgrade = $false
if (Test-Path (Join-Path $InstallDir "SCPITestWave.py")) {
    $oldVersion = Get-AppVersion $InstallDir
    $isUpgrade = $true
}

Write-Host ("Install dir: " + $InstallDir)
Write-Host ("Source dir:  " + $source)
if ($isUpgrade) {
    if ($oldVersion -and $newVersion) {
        Write-Host ("Mode: UPGRADE  " + $oldVersion + " -> " + $newVersion) -ForegroundColor Yellow
    } else {
        Write-Host "Mode: UPGRADE (reinstall over existing)" -ForegroundColor Yellow
    }
} else {
    if ($newVersion) {
        Write-Host ("Mode: FRESH INSTALL  version=" + $newVersion) -ForegroundColor Cyan
    } else {
        Write-Host "Mode: FRESH INSTALL" -ForegroundColor Cyan
    }
}

$oldLockHash = Get-FileHashSafe (Join-Path $InstallDir "uv.lock")

Ensure-Directory $InstallDir
Copy-AppFiles -Source $source -Destination $InstallDir

# 正式 IOT 地址：每次安装/升级用安装包内 example 覆盖 iot_bootstrap.json
$configDir = Join-Path $InstallDir "config"
$bootPath = Join-Path $configDir "iot_bootstrap.json"
$bootExample = Join-Path $configDir "iot_bootstrap.example.json"
if (Test-Path $bootExample) {
    Ensure-Directory $configDir
    Copy-Item -Force $bootExample $bootPath
    Write-Ok "Updated config\iot_bootstrap.json (formal IOT address from package)"
}

# Persist version into install root (package root VERSION wins)
$verSrc = Join-Path $packageRoot "VERSION"
if (-not (Test-Path $verSrc)) { $verSrc = Join-Path $source "VERSION" }
if (Test-Path $verSrc) {
    Copy-Item -Force $verSrc (Join-Path $InstallDir "VERSION")
}

Copy-Item -Force (Join-Path $packageRoot "Verify-Install.ps1") (Join-Path $InstallDir "Verify-Install.ps1") -ErrorAction SilentlyContinue
Copy-Item -Force (Join-Path $packageRoot "Check-And-Update.ps1") (Join-Path $InstallDir "Check-And-Update.ps1") -ErrorAction SilentlyContinue
Copy-Item -Force (Join-Path $packageRoot "INSTALL.txt") (Join-Path $InstallDir "INSTALL.txt") -ErrorAction SilentlyContinue

$uv = Ensure-Uv -InstallRoot $InstallDir
$launcher = Write-Launcher -InstallRoot $InstallDir

$newLockHash = Get-FileHashSafe (Join-Path $InstallDir "uv.lock")
$skipSyncBecauseSame = $false
if ($isUpgrade -and $oldLockHash -and $newLockHash -and ($oldLockHash -eq $newLockHash)) {
    $skipSyncBecauseSame = $true
}

if ($SkipSync) {
    Write-WarnLine "SkipSync requested; dependencies not refreshed"
} elseif ($skipSyncBecauseSame) {
    Write-Ok "uv.lock unchanged; skip dependency sync (faster upgrade)"
} else {
    Invoke-UvSync -InstallRoot $InstallDir -UvExe $uv
}

if (-not $SkipShortcut) {
    New-AppShortcut -TargetBat $launcher -InstallRoot $InstallDir
}

if (-not $SkipVerify) {
    Write-Step "Post-install verification"
    $verify = Join-Path $packageRoot "Verify-Install.ps1"
    if (-not (Test-Path $verify)) {
        $verify = Join-Path $InstallDir "Verify-Install.ps1"
    }
    $p = Start-Process -FilePath "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" `
        -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $verify, "-InstallDir", $InstallDir) `
        -Wait -PassThru -NoNewWindow
    if ($p.ExitCode -ne 0) {
        throw ("Verify failed, exit code " + $p.ExitCode)
    }
}

Write-Host ""
if ($isUpgrade) {
    Write-Ok ("Upgrade succeeded  version=" + $(if ($newVersion) { $newVersion } else { "unknown" }))
} else {
    Write-Ok ("Install succeeded  version=" + $(if ($newVersion) { $newVersion } else { "unknown" }))
}
Write-Host ("App: " + $InstallDir)
Write-Host ("Start: " + $launcher)
exit 0
