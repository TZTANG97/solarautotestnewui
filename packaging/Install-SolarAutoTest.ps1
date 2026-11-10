#Requires -Version 5.1
<#
.SYNOPSIS
  Install SolarAutoTest to this PC (local copy + uv + venv).
#>
[CmdletBinding()]
param(
    [string]$InstallDir = "",
    [string]$DataDir = "",
    [string]$RuntimeDir = "",
    [switch]$SkipShortcut,
    [switch]$SkipSync,
    [switch]$SkipVerify,
    [switch]$Quiet,
    [switch]$NoPrompt
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

. (Join-Path $PSScriptRoot "Install-PathHelpers.ps1")

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
    # Install excludes command_save_files (runtime data); create empty dirs for first append.
    Ensure-Directory (Join-Path $Destination "command_save_files\command_data")
    Ensure-Directory (Join-Path $Destination "command_save_files\dewetron_data")
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
    $zipUrls = @(
        "https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip",
        "https://ghproxy.net/https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip"
    )
    $tmpZip = Join-Path $env:TEMP ("uv-win-" + [guid]::NewGuid().ToString() + ".zip")
    $tmpDir = Join-Path $env:TEMP ("uv-extract-" + [guid]::NewGuid().ToString())
    $downloaded = $false
    try {
        foreach ($zipUrl in $zipUrls) {
            try {
                Write-Host ("  try: " + $zipUrl)
                Invoke-WebRequest -Uri $zipUrl -OutFile $tmpZip -UseBasicParsing
                $downloaded = $true
                break
            } catch {
                Write-WarnLine ("uv zip failed: " + $_.Exception.Message)
            }
        }
        if (-not $downloaded) { throw "all uv zip mirrors failed" }
        Ensure-Directory $tmpDir
        Expand-Archive -Path $tmpZip -DestinationPath $tmpDir -Force
        $found = Get-ChildItem -Path $tmpDir -Filter "uv.exe" -Recurse | Select-Object -First 1
        if (-not $found) { throw "uv.exe not found in download" }
        Copy-Item -Force $found.FullName $target
        Write-Ok ("uv installed to " + $target)
        return $target
    }
    catch {
        Write-WarnLine ("uv download failed: " + $_.Exception.Message)
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
    $local = Join-Path $InstallRoot "tools\uv.exe"
    $bundled = Join-Path (Get-PackageRoot) "bundled\uv.exe"
    # 全量 zip 的 app/ 不含 tools\uv.exe；若保留旧 uv，下次增量会因 ~60MB 对不上又逼全量。
    if ($bundled -and (Test-Path -LiteralPath $bundled)) {
        Ensure-Directory (Split-Path $local)
        $needCopy = $true
        if (Test-Path -LiteralPath $local) {
            try {
                $a = (Get-FileHash -Algorithm SHA256 -LiteralPath $local).Hash
                $b = (Get-FileHash -Algorithm SHA256 -LiteralPath $bundled).Hash
                if ($a -eq $b) { $needCopy = $false }
            } catch {
                $needCopy = $true
            }
        }
        if ($needCopy) {
            Write-Step "Sync tools\uv.exe from package bundled (keeps incremental updates working)"
            Copy-Item -Force $bundled $local
        }
        Write-Ok ("Found uv: " + $local)
        return $local
    }
    $uv = Find-UvExe $InstallRoot
    if ($uv) {
        Write-Ok ("Found uv: " + $uv)
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
    # bat 行用单引号写入，避免 PowerShell `"...\`" 弄乱；升级后若改写本 bat，
    # Check-And-Update 返回 10，必须 restart，否则 cmd 按行号错位（'OOT'/LOCAL_ROOT 空）。
    $lines = @(
        '@echo off',
        'setlocal EnableExtensions EnableDelayedExpansion',
        'chcp 65001 >nul',
        'pushd "%~dp0" >nul 2>&1',
        'if errorlevel 1 (',
        '    echo [ERROR] Cannot open install directory',
        '    pause',
        '    exit /b 1',
        ')',
        '',
        'REM Update before the app starts. Do not hide this window, and do not',
        'REM read ERRORLEVEL inside the same parentheses block (%VAR% is stale).',
        'set "UPD_EC=0"',
        'if exist "%~dp0Check-And-Update.ps1" (',
        '    echo Checking for updates...',
        '    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Check-And-Update.ps1" -InstallDir "%CD%"',
        '    set "UPD_EC=!ERRORLEVEL!"',
        ')',
        'if "!UPD_EC!"=="10" (',
        '    echo Restarting after upgrade...',
        '    popd',
        '    call "%~f0"',
        '    exit /b !ERRORLEVEL!',
        ')',
        'if not "!UPD_EC!"=="0" (',
        '    echo [WARN] Update did not finish. See update.log',
        ')',
        '',
        'REM Runtime root: runtime_root.txt in install dir, else LOCALAPPDATA',
        'set "LOCAL_ROOT="',
        'if exist "%~dp0runtime_root.txt" set /p LOCAL_ROOT=<"%~dp0runtime_root.txt"',
        'if not defined LOCAL_ROOT (',
        '    set "LOCAL_ROOT=%LOCALAPPDATA%"',
        '    if not defined LOCAL_ROOT set "LOCAL_ROOT=%USERPROFILE%\AppData\Local"',
        '    set "LOCAL_ROOT=%LOCAL_ROOT%\SolarAutoTestRuntime"',
        ')',
        'set "UV_PROJECT_ENVIRONMENT=%LOCAL_ROOT%\.venv"',
        'set "UV_PYTHON_INSTALL_DIR=%LOCAL_ROOT%\python"',
        'set "UV_CACHE_DIR=%LOCAL_ROOT%\uv-cache"',
        'REM China-friendly mirrors (override by setting these before launch)',
        'if not defined UV_DEFAULT_INDEX set "UV_DEFAULT_INDEX=https://mirrors.aliyun.com/pypi/simple/"',
        'if not defined UV_PYTHON_INSTALL_MIRROR set "UV_PYTHON_INSTALL_MIRROR=https://cdn.npmmirror.com/binaries/python-build-standalone"',
        'if not exist "%LOCAL_ROOT%" mkdir "%LOCAL_ROOT%" >nul 2>&1',
        '',
        'set "UV_EXE=%~dp0tools\uv.exe"',
        'if not exist "%UV_EXE%" (',
        '    for /f "delims=" %%I in (''where uv.exe 2^>nul'') do (',
        '        if not defined UV_EXE set "UV_EXE=%%I"',
        '    )',
        ')',
        'if not exist "%UV_EXE%" (',
        '    echo [ERROR] uv.exe not found. Re-run installer.',
        '    popd',
        '    pause',
        '    exit /b 1',
        ')',
        '',
        'echo SolarAutoTest',
        'echo Install: %CD%',
        'echo Runtime: %UV_PROJECT_ENVIRONMENT%',
        'echo.',
        'echo Preparing Python packages...',
        'powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ". ''%~dp0Install-PathHelpers.ps1''; Sync-SolarAutoTestRuntime -UvExe ''%UV_EXE%'' -ProjectDir ''%CD%''"',
        'if errorlevel 1 (',
        '    echo [WARN] Dependency sync failed.',
        ')',
        '',
        'REM IOT Agent is started silently by SCPITestWave when config\solar_agent.json exists',
        'REM --offline: do not fall back to files.pythonhosted.org at startup',
        '"%UV_EXE%" run --frozen --offline python SCPITestWave.py',
        'set "EC=%ERRORLEVEL%"',
        'popd',
        'if not "%EC%"=="0" (',
        '    echo [ERROR] Exit code %EC%',
        '    pause',
        ')',
        'exit /b %EC%'
    )
    Set-Content -Path $launcher -Value $lines -Encoding ASCII
    Write-Ok ("Launcher written: " + $launcher)
    # 桌面快捷方式必须指向可见 bat（升级/进度要看得见）；
    # IOT Agent 黑窗由 agent/process_control.py 单独隐藏，不要用 Silent.vbs 藏主控制台。
    $silentVbs = Join-Path $InstallRoot "Start-SolarAutoTest-Silent.vbs"
    if (Test-Path $silentVbs) {
        Remove-Item -Force $silentVbs -ErrorAction SilentlyContinue
    }
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
    # 始终指向可见 bat，方便看升级/启动进度；不要指向 Silent.vbs
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

function Invoke-UvSync([string]$InstallRoot, [string]$UvExe, [string]$RuntimeRoot = "") {
    Write-Step "正在安装 Python 环境（依赖走国内镜像，不从 files.pythonhosted.org 下载）"
    Set-UvDownloadMirrors
    Write-Host ("  UV_DEFAULT_INDEX=" + $env:UV_DEFAULT_INDEX)
    Write-Host ("  UV_PYTHON_INSTALL_MIRROR=" + $env:UV_PYTHON_INSTALL_MIRROR)
    $runtime = $RuntimeRoot
    if (-not $runtime) {
        $ptr = Join-Path $InstallRoot "runtime_root.txt"
        if (Test-Path $ptr) {
            try { $runtime = ((Get-Content -Path $ptr -TotalCount 1) + "").Trim() } catch {}
        }
    }
    if (-not $runtime) {
        $runtime = Resolve-ClassicRuntime $InstallRoot
    }
    Ensure-Directory $runtime
    $env:UV_PROJECT_ENVIRONMENT = Join-Path $runtime ".venv"
    $env:UV_PYTHON_INSTALL_DIR = Join-Path $runtime "python"
    $env:UV_CACHE_DIR = Join-Path $runtime "uv-cache"
    Ensure-Directory $env:UV_PROJECT_ENVIRONMENT
    Ensure-Directory $env:UV_PYTHON_INSTALL_DIR
    Ensure-Directory $env:UV_CACHE_DIR

    & $UvExe --version
    Sync-SolarAutoTestRuntime -UvExe $UvExe -ProjectDir $InstallRoot
    Write-Ok "Dependencies synced"
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

$script:ResolvedDataDir = $DataDir
$script:ResolvedRuntimeDir = $RuntimeDir

if (-not $InstallDir) {
    $defaultInstall = Get-DefaultInstallDir
    $defaultData = Join-Path $defaultInstall "data"
    $defaultRuntime = Join-Path $defaultInstall "runtime"
    $existingLocal = Join-Path $env:LOCALAPPDATA "SolarAutoTest"
    if (Test-Path (Join-Path $existingLocal "SCPITestWave.py")) {
        $prev = Read-ExistingPaths $existingLocal
        $defaultInstall = $existingLocal
        if ($prev.DataDir) { $defaultData = $prev.DataDir } else { $defaultData = Resolve-ClassicData $existingLocal }
        if ($prev.RuntimeDir) { $defaultRuntime = $prev.RuntimeDir } else { $defaultRuntime = Resolve-ClassicRuntime $existingLocal }
    }
    if ($Quiet -or $NoPrompt) {
        $InstallDir = $defaultInstall
        if (-not $script:ResolvedDataDir) { $script:ResolvedDataDir = $defaultData }
        if (-not $script:ResolvedRuntimeDir) { $script:ResolvedRuntimeDir = $defaultRuntime }
    } else {
        $picked = Prompt-InstallPaths -DefaultInstall $defaultInstall -DefaultData $defaultData -DefaultRuntime $defaultRuntime
        $InstallDir = $picked.InstallDir
        if (-not $script:ResolvedDataDir) { $script:ResolvedDataDir = $picked.DataDir }
        if (-not $script:ResolvedRuntimeDir) { $script:ResolvedRuntimeDir = $picked.RuntimeDir }
    }
}

$InstallDir = [System.IO.Path]::GetFullPath($InstallDir)
$prevPaths = Read-ExistingPaths $InstallDir
if (-not $script:ResolvedDataDir) {
    if ($prevPaths.DataDir) { $script:ResolvedDataDir = $prevPaths.DataDir }
    else { $script:ResolvedDataDir = Resolve-ClassicData $InstallDir }
}
if (-not $script:ResolvedRuntimeDir) {
    if ($prevPaths.RuntimeDir) { $script:ResolvedRuntimeDir = $prevPaths.RuntimeDir }
    else { $script:ResolvedRuntimeDir = Resolve-ClassicRuntime $InstallDir }
}
$script:ResolvedDataDir = [System.IO.Path]::GetFullPath($script:ResolvedDataDir)
$script:ResolvedRuntimeDir = [System.IO.Path]::GetFullPath($script:ResolvedRuntimeDir)

$newVersion = Get-AppVersion $packageRoot
if (-not $newVersion) { $newVersion = Get-AppVersion $source }
$oldVersion = ""
$isUpgrade = $false
if (Test-Path (Join-Path $InstallDir "SCPITestWave.py")) {
    $oldVersion = Get-AppVersion $InstallDir
    $isUpgrade = $true
}

Write-Host ("Install dir: " + $InstallDir)
Write-Host ("Data dir:    " + $script:ResolvedDataDir)
Write-Host ("Runtime dir: " + $script:ResolvedRuntimeDir)
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

# 升级前备份本机身份，避免被安装包 config 覆盖后当成「新电脑」又要重新添加
$configDir = Join-Path $InstallDir "config"
$identityBackup = Join-Path $env:TEMP ("SolarAutoTest-identity-" + [guid]::NewGuid().ToString())
Ensure-Directory $identityBackup
foreach ($name in @("solar_machine_id", "solar_agent.json")) {
    $srcId = Join-Path $configDir $name
    if (Test-Path $srcId) {
        Copy-Item -Force $srcId (Join-Path $identityBackup $name)
    }
}
foreach ($name in @("paths.ini", "runtime_root.txt")) {
    $srcPath = if ($name -eq "paths.ini") {
        Join-Path $InstallDir "config_files\paths.ini"
    } else {
        Join-Path $InstallDir $name
    }
    if (Test-Path $srcPath) {
        Copy-Item -Force $srcPath (Join-Path $identityBackup $name)
    }
}

Copy-AppFiles -Source $source -Destination $InstallDir

# Keep previous custom paths on upgrade unless DataDir/RuntimeDir explicitly passed
$bakPaths = Join-Path $identityBackup "paths.ini"
$bakRuntime = Join-Path $identityBackup "runtime_root.txt"
if ((-not $DataDir) -and (Test-Path $bakPaths)) {
    try {
        foreach ($line in (Get-Content -Path $bakPaths -ErrorAction Stop)) {
            if ($line -match '^\s*data_root\s*=\s*(.+)$') {
                $script:ResolvedDataDir = [System.IO.Path]::GetFullPath($Matches[1].Trim().Trim('"'))
            }
            if ((-not $RuntimeDir) -and ($line -match '^\s*runtime_root\s*=\s*(.+)$')) {
                $script:ResolvedRuntimeDir = [System.IO.Path]::GetFullPath($Matches[1].Trim().Trim('"'))
            }
        }
    } catch {}
}
if ((-not $RuntimeDir) -and (Test-Path $bakRuntime)) {
    try {
        $line = ((Get-Content -Path $bakRuntime -TotalCount 1) + "").Trim()
        if ($line) { $script:ResolvedRuntimeDir = [System.IO.Path]::GetFullPath($line) }
    } catch {}
}
Ensure-Directory $script:ResolvedDataDir
Ensure-Directory $script:ResolvedRuntimeDir

# 目录迁移后常见情况：新 runtime 是空的，但旧盘/旧路径仍有 .venv+uv-cache。
# 未显式指定 -RuntimeDir 时，自动复用已就绪的 runtime，避免重新从外网拉包。
if (-not $RuntimeDir) {
    if (-not (Test-UvRuntimeReady $script:ResolvedRuntimeDir)) {
        $donor = Find-ReusableUvRuntime $script:ResolvedRuntimeDir
        if ($donor -and ($donor.ToLowerInvariant() -ne $script:ResolvedRuntimeDir.ToLowerInvariant())) {
            Write-Ok ("Reusing existing Python runtime (skip re-download): " + $donor)
            Write-WarnLine "To force a fresh runtime later: delete its .venv or set a new runtime_root in paths.ini"
            $script:ResolvedRuntimeDir = $donor
        }
    }
}

Write-PathsConfig -InstallRoot $InstallDir -DataRoot $script:ResolvedDataDir -RuntimeRoot $script:ResolvedRuntimeDir

# 正式 IOT 地址：每次安装/升级用安装包内 example 覆盖 iot_bootstrap.json
$bootPath = Join-Path $configDir "iot_bootstrap.json"
$bootExample = Join-Path $configDir "iot_bootstrap.example.json"
if (Test-Path $bootExample) {
    Ensure-Directory $configDir
    Copy-Item -Force $bootExample $bootPath
    Write-Ok "Updated config\iot_bootstrap.json (formal IOT address from package)"
}

# 还原本机 machineId / 令牌（只还原升级前已有的文件）
$restoredIdentity = $false
foreach ($name in @("solar_machine_id", "solar_agent.json")) {
    $bak = Join-Path $identityBackup $name
    if (Test-Path $bak) {
        Ensure-Directory $configDir
        Copy-Item -Force $bak (Join-Path $configDir $name)
        Write-Ok ("Restored config/" + $name + " (keep same bench identity)")
        $restoredIdentity = $true
    }
}
Remove-Item -Recurse -Force $identityBackup -ErrorAction SilentlyContinue

# 新装或包内误带了联调身份：丢掉 solar_agent.json / solar_machine_id，让软件启动时重新 announce
# （否则会带着打包机的 machineId / 127.0.0.1 令牌，IOT「添加设备」永远看不见本机）
if (-not $restoredIdentity) {
    foreach ($name in @("solar_machine_id", "solar_agent.json")) {
        $p = Join-Path $configDir $name
        if (Test-Path $p) {
            Remove-Item -Force $p
            Write-WarnLine ("Removed packaged config/" + $name + " (will re-register on first launch)")
        }
    }
} else {
    # 升级保留身份时：若残留的是本机联调地址，仍清掉令牌文件里的 127.0.0.1（iot_bootstrap 会覆盖正式地址）
    $agentCfg = Join-Path $configDir "solar_agent.json"
    if (Test-Path $agentCfg) {
        try {
            $raw = Get-Content -Raw -Encoding UTF8 $agentCfg
            if ($raw -match '127\.0\.0\.1|localhost') {
                Write-WarnLine "Detected local IOT URL in solar_agent.json; keeping machine_id but clearing stale token/base on next Agent announce"
            }
        } catch {}
    }
}

# Persist version into install root (package root VERSION wins)
$verSrc = Join-Path $packageRoot "VERSION"
if (-not (Test-Path $verSrc)) { $verSrc = Join-Path $source "VERSION" }
if (Test-Path $verSrc) {
    Copy-Item -Force $verSrc (Join-Path $InstallDir "VERSION")
}

Copy-Item -Force (Join-Path $packageRoot "Verify-Install.ps1") (Join-Path $InstallDir "Verify-Install.ps1") -ErrorAction SilentlyContinue
Copy-Item -Force (Join-Path $packageRoot "Check-And-Update.ps1") (Join-Path $InstallDir "Check-And-Update.ps1") -ErrorAction SilentlyContinue
Copy-Item -Force (Join-Path $packageRoot "Install-PathHelpers.ps1") (Join-Path $InstallDir "Install-PathHelpers.ps1") -ErrorAction SilentlyContinue
Copy-Item -Force (Join-Path $packageRoot "INSTALL.txt") (Join-Path $InstallDir "INSTALL.txt") -ErrorAction SilentlyContinue

$uv = Ensure-Uv -InstallRoot $InstallDir
$launcher = Write-Launcher -InstallRoot $InstallDir

$newLockHash = Get-FileHashSafe (Join-Path $InstallDir "uv.lock")
$venvReady = Test-UvRuntimeReady $script:ResolvedRuntimeDir
$skipSyncBecauseSame = $false
if ($venvReady -and $oldLockHash -and $newLockHash -and ($oldLockHash -eq $newLockHash)) {
    $skipSyncBecauseSame = $true
}

if ($SkipSync) {
    Write-WarnLine "SkipSync requested; dependencies not refreshed"
} elseif ($skipSyncBecauseSame) {
    Write-Ok "uv.lock unchanged and runtime ready; skip dependency sync (faster upgrade)"
} elseif ($venvReady -and (-not $oldLockHash) -and $newLockHash) {
    # 新装目录但已指向旧 runtime：仍跑一次 sync，有本地 uv-cache 时通常很快
    Write-Ok "Runtime already has .venv; syncing with local cache + mirrors"
    Invoke-UvSync -InstallRoot $InstallDir -UvExe $uv -RuntimeRoot $script:ResolvedRuntimeDir
} else {
    if (-not $venvReady) {
        Write-WarnLine ("Runtime not ready yet: " + (Join-Path $script:ResolvedRuntimeDir ".venv"))
    }
    Invoke-UvSync -InstallRoot $InstallDir -UvExe $uv -RuntimeRoot $script:ResolvedRuntimeDir
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
Write-Host ("Data: " + $script:ResolvedDataDir)
Write-Host ("Runtime: " + $script:ResolvedRuntimeDir)
Write-Host ("Start: " + $launcher)
Write-Host "To move disks later: re-run install.bat or edit config_files\paths.ini and runtime_root.txt"
exit 0
