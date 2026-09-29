from pathlib import Path

p = Path(r"E:\solarautotestnewui\packaging\Install-SolarAutoTest.ps1")
text = p.read_text(encoding="utf-8")

# 1) extend param block
old_param = '''param(
    [string]$InstallDir = "",
    [switch]$SkipShortcut,
    [switch]$SkipSync,
    [switch]$SkipVerify,
    [switch]$Quiet
)'''
new_param = '''param(
    [string]$InstallDir = "",
    [string]$DataDir = "",
    [string]$RuntimeDir = "",
    [switch]$SkipShortcut,
    [switch]$SkipSync,
    [switch]$SkipVerify,
    [switch]$Quiet,
    [switch]$NoPrompt
)'''
if old_param not in text:
    raise SystemExit("param block missing")
text = text.replace(old_param, new_param, 1)

# 2) insert helper functions before Get-PackageRoot
helpers = r'''
function Get-DefaultInstallDir {
    foreach ($drive in @("D:", "E:", "F:")) {
        if (Test-Path ($drive + "\")) {
            return (Join-Path $drive "SolarAutoTest")
        }
    }
    return (Join-Path $env:LOCALAPPDATA "SolarAutoTest")
}

function Read-ExistingPaths([string]$Root) {
    $result = @{ DataDir = ""; RuntimeDir = "" }
    $txt = Join-Path $Root "runtime_root.txt"
    if (Test-Path $txt) {
        try {
            $line = (Get-Content -Path $txt -TotalCount 1 -ErrorAction Stop)
            if ($line) { $result.RuntimeDir = $line.Trim() }
        } catch {}
    }
    $ini = Join-Path $Root "config_files\paths.ini"
    if (Test-Path $ini) {
        try {
            $cfg = Get-Content -Path $ini -ErrorAction Stop
            foreach ($line in $cfg) {
                if ($line -match '^\s*data_root\s*=\s*(.+)$') {
                    $result.DataDir = $Matches[1].Trim().Trim('"')
                }
                if ($line -match '^\s*runtime_root\s*=\s*(.+)$') {
                    if (-not $result.RuntimeDir) {
                        $result.RuntimeDir = $Matches[1].Trim().Trim('"')
                    }
                }
            }
        } catch {}
    }
    return $result
}

function Choose-Folder([string]$Description, [string]$SelectedPath) {
    try {
        Add-Type -AssemblyName System.Windows.Forms | Out-Null
        $dlg = New-Object System.Windows.Forms.FolderBrowserDialog
        $dlg.Description = $Description
        $dlg.ShowNewFolderButton = $true
        if ($SelectedPath -and (Test-Path $SelectedPath)) {
            $dlg.SelectedPath = $SelectedPath
        } elseif ($SelectedPath) {
            $parent = Split-Path -Parent $SelectedPath
            if ($parent -and (Test-Path $parent)) { $dlg.SelectedPath = $parent }
        }
        $res = $dlg.ShowDialog()
        if ($res -eq [System.Windows.Forms.DialogResult]::OK -and $dlg.SelectedPath) {
            return $dlg.SelectedPath
        }
    } catch {
        Write-WarnLine ("Folder dialog unavailable: " + $_.Exception.Message)
    }
    return ""
}

function Prompt-InstallPaths {
    param(
        [string]$DefaultInstall,
        [string]$DefaultData,
        [string]$DefaultRuntime
    )
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host " 选择安装位置（可不装在 C 盘）" -ForegroundColor Cyan
    Write-Host "============================================================"
    Write-Host ("默认程序目录: " + $DefaultInstall)
    Write-Host ("默认数据目录: " + $DefaultData)
    Write-Host ("默认运行时(venv): " + $DefaultRuntime)
    Write-Host "回车=用默认；输入路径；或输入 B 打开文件夹选择框"
    Write-Host ""

    $inst = $DefaultInstall
    $ans = Read-Host "程序安装目录"
    if ($ans -eq "B" -or $ans -eq "b") {
        $picked = Choose-Folder "选择 SolarAutoTest 程序安装目录" $DefaultInstall
        if ($picked) { $inst = Join-Path $picked "SolarAutoTest" }
    } elseif ($ans) {
        $inst = $ans.Trim().Trim('"')
    }

    $data = Join-Path $inst "data"
    if ($DefaultData) { $data = $DefaultData }
    $ans = Read-Host ("数据目录(配置/预设/试验文件) [默认 " + $data + "]")
    if ($ans -eq "B" -or $ans -eq "b") {
        $picked = Choose-Folder "选择数据目录（配置/预设/试验文件）" $data
        if ($picked) { $data = $picked }
    } elseif ($ans) {
        $data = $ans.Trim().Trim('"')
    }

    $runtime = Join-Path $inst "runtime"
    if ($DefaultRuntime) { $runtime = $DefaultRuntime }
    $ans = Read-Host ("运行时目录(.venv/uv缓存,体积大) [默认 " + $runtime + "]")
    if ($ans -eq "B" -or $ans -eq "b") {
        $picked = Choose-Folder "选择运行时目录（.venv / uv 缓存）" $runtime
        if ($picked) { $runtime = $picked }
    } elseif ($ans) {
        $runtime = $ans.Trim().Trim('"')
    }

    return @{
        InstallDir = $inst
        DataDir = $data
        RuntimeDir = $runtime
    }
}

function Write-PathsConfig([string]$InstallRoot, [string]$DataRoot, [string]$RuntimeRoot) {
    $cfgDir = Join-Path $InstallRoot "config_files"
    Ensure-Directory $cfgDir
    $ini = Join-Path $cfgDir "paths.ini"
    $lines = @(
        "[paths]",
        ("data_root = " + $DataRoot),
        ("runtime_root = " + $RuntimeRoot),
        "",
        "# 也可设环境变量 SOLARAUTOTEST_DATA / SOLARAUTOTEST_RUNTIME 覆盖。",
        "# 修改后重启软件生效。"
    )
    $utf8Bom = New-Object System.Text.UTF8Encoding $true
    [System.IO.File]::WriteAllLines($ini, $lines, $utf8Bom)

    $txt = Join-Path $InstallRoot "runtime_root.txt"
    [System.IO.File]::WriteAllText($txt, ($RuntimeRoot.Trim() + "`r`n"), $utf8Bom)
    Write-Ok ("Paths written: " + $ini)
    Write-Ok ("Runtime pointer: " + $txt)
}

'''

if "function Get-DefaultInstallDir" not in text:
    if "function Get-PackageRoot" not in text:
        raise SystemExit("Get-PackageRoot missing")
    text = text.replace("function Get-PackageRoot", helpers + "function Get-PackageRoot", 1)
    print("helpers inserted")
else:
    print("helpers already present")

# 3) Replace Write-Launcher LOCAL_ROOT section to read runtime_root.txt
old_local = """        'REM Split path: avoid mid-upgrade bat rewrite eating LOCAL_ROOT',
        'set "LOCAL_ROOT=%LOCALAPPDATA%"',
        'if not defined LOCAL_ROOT set "LOCAL_ROOT=%USERPROFILE%\\AppData\\Local"',
        'set "LOCAL_ROOT=%LOCAL_ROOT%\\SolarAutoTestRuntime"',"""
new_local = """        'REM Runtime: prefer install-dir runtime_root.txt (custom disk); else LOCALAPPDATA',
        'set "LOCAL_ROOT="',
        'if exist "%~dp0runtime_root.txt" (',
        '    set /p LOCAL_ROOT=<"%~dp0runtime_root.txt"',
        ')',
        'if not defined LOCAL_ROOT (',
        '    set "LOCAL_ROOT=%LOCALAPPDATA%"',
        '    if not defined LOCAL_ROOT set "LOCAL_ROOT=%USERPROFILE%\\AppData\\Local"',
        '    set "LOCAL_ROOT=%LOCAL_ROOT%\\SolarAutoTestRuntime"',
        ')',"""
if old_local not in text:
    raise SystemExit("LOCAL_ROOT block missing")
text = text.replace(old_local, new_local, 1)
print("launcher runtime patched")

# 4) Invoke-UvSync accept RuntimeDir
old_sync = '''function Invoke-UvSync([string]$InstallRoot, [string]$UvExe) {
    Write-Step "Syncing Python environment (first run may take several minutes)"
    $runtime = Join-Path $env:LOCALAPPDATA "SolarAutoTestRuntime"
    Ensure-Directory $runtime'''
new_sync = '''function Invoke-UvSync([string]$InstallRoot, [string]$UvExe, [string]$RuntimeRoot = "") {
    Write-Step "Syncing Python environment (first run may take several minutes)"
    $runtime = $RuntimeRoot
    if (-not $runtime) {
        $ptr = Join-Path $InstallRoot "runtime_root.txt"
        if (Test-Path $ptr) {
            try { $runtime = ((Get-Content -Path $ptr -TotalCount 1) + "").Trim() } catch {}
        }
    }
    if (-not $runtime) {
        $runtime = Join-Path $env:LOCALAPPDATA "SolarAutoTestRuntime"
    }
    Ensure-Directory $runtime'''
if old_sync not in text:
    raise SystemExit("Invoke-UvSync head missing")
text = text.replace(old_sync, new_sync, 1)

# 5) Replace InstallDir default resolution block
old_resolve = '''$packageRoot = Get-PackageRoot
$source = Get-SourceAppDir

if (-not $InstallDir) {
    $InstallDir = Join-Path $env:LOCALAPPDATA "SolarAutoTest"
}
$InstallDir = [System.IO.Path]::GetFullPath($InstallDir)'''

new_resolve = '''$packageRoot = Get-PackageRoot
$source = Get-SourceAppDir

$script:ResolvedDataDir = $DataDir
$script:ResolvedRuntimeDir = $RuntimeDir

if (-not $InstallDir) {
    # 升级场景：安装脚本位于已安装目录旁（Check-And-Update 会显式传 InstallDir）
    $InstallDir = ""
}

if (-not $InstallDir) {
    $defaultInstall = Get-DefaultInstallDir
    $defaultData = Join-Path $defaultInstall "data"
    $defaultRuntime = Join-Path $defaultInstall "runtime"
    $existingLocal = Join-Path $env:LOCALAPPDATA "SolarAutoTest"
    if (Test-Path (Join-Path $existingLocal "SCPITestWave.py")) {
        $prev = Read-ExistingPaths $existingLocal
        $defaultInstall = $existingLocal
        if ($prev.DataDir) { $defaultData = $prev.DataDir }
        if ($prev.RuntimeDir) { $defaultRuntime = $prev.RuntimeDir }
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
if (-not $script:ResolvedDataDir) {
    $prev = Read-ExistingPaths $InstallDir
    if ($prev.DataDir) { $script:ResolvedDataDir = $prev.DataDir }
    else { $script:ResolvedDataDir = Join-Path $InstallDir "data" }
}
if (-not $script:ResolvedRuntimeDir) {
    $prev = Read-ExistingPaths $InstallDir
    if ($prev.RuntimeDir) { $script:ResolvedRuntimeDir = $prev.RuntimeDir }
    else { $script:ResolvedRuntimeDir = Join-Path $InstallDir "runtime" }
}
$script:ResolvedDataDir = [System.IO.Path]::GetFullPath($script:ResolvedDataDir)
$script:ResolvedRuntimeDir = [System.IO.Path]::GetFullPath($script:ResolvedRuntimeDir)'''

if old_resolve not in text:
    raise SystemExit("resolve block missing")
text = text.replace(old_resolve, new_resolve, 1)
print("resolve patched")

# after Write-Host Install dir, also print data/runtime
old_print = '''Write-Host ("Install dir: " + $InstallDir)
Write-Host ("Source dir:  " + $source)'''
new_print = '''Write-Host ("Install dir: " + $InstallDir)
Write-Host ("Data dir:    " + $script:ResolvedDataDir)
Write-Host ("Runtime dir: " + $script:ResolvedRuntimeDir)
Write-Host ("Source dir:  " + $source)'''
if old_print not in text:
    raise SystemExit("print block missing")
text = text.replace(old_print, new_print, 1)

# backup paths.ini like identity
old_id = '''foreach ($name in @("solar_machine_id", "solar_agent.json")) {
    $srcId = Join-Path $configDir $name
    if (Test-Path $srcId) {
        Copy-Item -Force $srcId (Join-Path $identityBackup $name)
    }
}'''
new_id = '''foreach ($name in @("solar_machine_id", "solar_agent.json")) {
    $srcId = Join-Path $configDir $name
    if (Test-Path $srcId) {
        Copy-Item -Force $srcId (Join-Path $identityBackup $name)
    }
}
$pathsIniSrc = Join-Path $InstallDir "config_files\\paths.ini"
if (Test-Path $pathsIniSrc) {
    Copy-Item -Force $pathsIniSrc (Join-Path $identityBackup "paths.ini")
}
$runtimePtrSrc = Join-Path $InstallDir "runtime_root.txt"
if (Test-Path $runtimePtrSrc) {
    Copy-Item -Force $runtimePtrSrc (Join-Path $identityBackup "runtime_root.txt")
}'''
if old_id not in text:
    raise SystemExit("identity backup missing")
text = text.replace(old_id, new_id, 1)

# after Copy-AppFiles write paths (and restore if backup had them unless user passed new)
# Insert after Copy-AppFiles line
marker = "Copy-AppFiles -Source $source -Destination $InstallDir\n"
if marker not in text:
    raise SystemExit("Copy-AppFiles marker missing")
insert_after_copy = '''Copy-AppFiles -Source $source -Destination $InstallDir

# 保留升级前路径；若本次显式传入 DataDir/RuntimeDir 则用新值
$bakPaths = Join-Path $identityBackup "paths.ini"
$bakRuntime = Join-Path $identityBackup "runtime_root.txt"
if ((-not $DataDir) -and (Test-Path $bakPaths)) {
    try {
        $cfg = Get-Content -Path $bakPaths -ErrorAction Stop
        foreach ($line in $cfg) {
            if ($line -match '^\\s*data_root\\s*=\\s*(.+)$') {
                $script:ResolvedDataDir = [System.IO.Path]::GetFullPath($Matches[1].Trim().Trim('"'))
            }
            if ($line -match '^\\s*runtime_root\\s*=\\s*(.+)$') {
                if (-not $RuntimeDir) {
                    $script:ResolvedRuntimeDir = [System.IO.Path]::GetFullPath($Matches[1].Trim().Trim('"'))
                }
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
Write-PathsConfig -InstallRoot $InstallDir -DataRoot $script:ResolvedDataDir -RuntimeRoot $script:ResolvedRuntimeDir
'''
text = text.replace(marker, insert_after_copy, 1)

# Invoke-UvSync call with runtime
old_call = "    Invoke-UvSync -InstallRoot $InstallDir -UvExe $uv\n"
new_call = "    Invoke-UvSync -InstallRoot $InstallDir -UvExe $uv -RuntimeRoot $script:ResolvedRuntimeDir\n"
if old_call not in text:
    raise SystemExit("Invoke-UvSync call missing")
text = text.replace(old_call, new_call, 1)

# final Write-Host
old_end = '''Write-Host ("App: " + $InstallDir)
Write-Host ("Start: " + $launcher)
exit 0'''
new_end = '''Write-Host ("App: " + $InstallDir)
Write-Host ("Data: " + $script:ResolvedDataDir)
Write-Host ("Runtime: " + $script:ResolvedRuntimeDir)
Write-Host ("Start: " + $launcher)
Write-Host "如需改盘：重跑 install.bat 重选，或编辑 config_files\\paths.ini / runtime_root.txt 后重启。"
exit 0'''
if old_end not in text:
    raise SystemExit("end block missing")
text = text.replace(old_end, new_end, 1)

p.write_text(text, encoding="utf-8")
print("Install-SolarAutoTest.ps1 patched, len", len(text))
