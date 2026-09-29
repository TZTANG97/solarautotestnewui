from pathlib import Path

p = Path(r"E:\solarautotestnewui\packaging\Install-SolarAutoTest.ps1")
# preserve BOM if present
raw = p.read_bytes()
has_bom = raw.startswith(b"\xef\xbb\xbf")
text = raw.decode("utf-8-sig")

old_param = """param(
    [string]$InstallDir = "",
    [switch]$SkipShortcut,
    [switch]$SkipSync,
    [switch]$SkipVerify,
    [switch]$Quiet
)"""
new_param = """param(
    [string]$InstallDir = "",
    [string]$DataDir = "",
    [string]$RuntimeDir = "",
    [switch]$SkipShortcut,
    [switch]$SkipSync,
    [switch]$SkipVerify,
    [switch]$Quiet,
    [switch]$NoPrompt
)"""
if old_param not in text:
    raise SystemExit("param missing")
text = text.replace(old_param, new_param, 1)

# Dot-source helpers after ErrorAction
needle = '$ErrorActionPreference = "Stop"\n$ProgressPreference = "SilentlyContinue"\n'
insert = needle + '\n. (Join-Path $PSScriptRoot "Install-PathHelpers.ps1")\n'
if "Install-PathHelpers.ps1" not in text:
    if needle not in text:
        raise SystemExit("ErrorAction needle missing")
    text = text.replace(needle, insert, 1)

old_local = """        'REM Split path: avoid mid-upgrade bat rewrite eating LOCAL_ROOT',
        'set "LOCAL_ROOT=%LOCALAPPDATA%"',
        'if not defined LOCAL_ROOT set "LOCAL_ROOT=%USERPROFILE%\\AppData\\Local"',
        'set "LOCAL_ROOT=%LOCAL_ROOT%\\SolarAutoTestRuntime"',"""
new_local = """        'REM Runtime root: runtime_root.txt in install dir, else LOCALAPPDATA',
        'set "LOCAL_ROOT="',
        'if exist "%~dp0runtime_root.txt" set /p LOCAL_ROOT=<"%~dp0runtime_root.txt"',
        'if not defined LOCAL_ROOT (',
        '    set "LOCAL_ROOT=%LOCALAPPDATA%"',
        '    if not defined LOCAL_ROOT set "LOCAL_ROOT=%USERPROFILE%\\AppData\\Local"',
        '    set "LOCAL_ROOT=%LOCAL_ROOT%\\SolarAutoTestRuntime"',
        ')',"""
if old_local not in text:
    raise SystemExit("LOCAL_ROOT missing")
text = text.replace(old_local, new_local, 1)

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
        $runtime = Resolve-ClassicRuntime $InstallRoot
    }
    Ensure-Directory $runtime'''
if old_sync not in text:
    raise SystemExit("Invoke-UvSync missing")
text = text.replace(old_sync, new_sync, 1)

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
$script:ResolvedRuntimeDir = [System.IO.Path]::GetFullPath($script:ResolvedRuntimeDir)'''

if old_resolve not in text:
    raise SystemExit("resolve missing")
text = text.replace(old_resolve, new_resolve, 1)

old_print = '''Write-Host ("Install dir: " + $InstallDir)
Write-Host ("Source dir:  " + $source)'''
new_print = '''Write-Host ("Install dir: " + $InstallDir)
Write-Host ("Data dir:    " + $script:ResolvedDataDir)
Write-Host ("Runtime dir: " + $script:ResolvedRuntimeDir)
Write-Host ("Source dir:  " + $source)'''
if old_print not in text:
    raise SystemExit("print missing")
text = text.replace(old_print, new_print, 1)

old_bak = '''foreach ($name in @("solar_machine_id", "solar_agent.json")) {
    $srcId = Join-Path $configDir $name
    if (Test-Path $srcId) {
        Copy-Item -Force $srcId (Join-Path $identityBackup $name)
    }
}'''
new_bak = '''foreach ($name in @("solar_machine_id", "solar_agent.json")) {
    $srcId = Join-Path $configDir $name
    if (Test-Path $srcId) {
        Copy-Item -Force $srcId (Join-Path $identityBackup $name)
    }
}
foreach ($name in @("paths.ini", "runtime_root.txt")) {
    $srcPath = if ($name -eq "paths.ini") {
        Join-Path $InstallDir "config_files\\paths.ini"
    } else {
        Join-Path $InstallDir $name
    }
    if (Test-Path $srcPath) {
        Copy-Item -Force $srcPath (Join-Path $identityBackup $name)
    }
}'''
if old_bak not in text:
    raise SystemExit("backup missing")
text = text.replace(old_bak, new_bak, 1)

marker = "Copy-AppFiles -Source $source -Destination $InstallDir\n"
insert = '''Copy-AppFiles -Source $source -Destination $InstallDir

# Keep previous custom paths on upgrade unless DataDir/RuntimeDir explicitly passed
$bakPaths = Join-Path $identityBackup "paths.ini"
$bakRuntime = Join-Path $identityBackup "runtime_root.txt"
if ((-not $DataDir) -and (Test-Path $bakPaths)) {
    try {
        foreach ($line in (Get-Content -Path $bakPaths -ErrorAction Stop)) {
            if ($line -match '^\\s*data_root\\s*=\\s*(.+)$') {
                $script:ResolvedDataDir = [System.IO.Path]::GetFullPath($Matches[1].Trim().Trim('"'))
            }
            if ((-not $RuntimeDir) -and ($line -match '^\\s*runtime_root\\s*=\\s*(.+)$')) {
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
Write-PathsConfig -InstallRoot $InstallDir -DataRoot $script:ResolvedDataDir -RuntimeRoot $script:ResolvedRuntimeDir
'''
if marker not in text:
    raise SystemExit("Copy-AppFiles missing")
text = text.replace(marker, insert, 1)

old_call = "    Invoke-UvSync -InstallRoot $InstallDir -UvExe $uv\n"
new_call = "    Invoke-UvSync -InstallRoot $InstallDir -UvExe $uv -RuntimeRoot $script:ResolvedRuntimeDir\n"
if old_call not in text:
    raise SystemExit("uv sync call missing")
text = text.replace(old_call, new_call, 1)

old_end = '''Write-Host ("App: " + $InstallDir)
Write-Host ("Start: " + $launcher)
exit 0'''
new_end = '''Write-Host ("App: " + $InstallDir)
Write-Host ("Data: " + $script:ResolvedDataDir)
Write-Host ("Runtime: " + $script:ResolvedRuntimeDir)
Write-Host ("Start: " + $launcher)
Write-Host "To move disks later: re-run install.bat or edit config_files\\paths.ini and runtime_root.txt"
exit 0'''
if old_end not in text:
    raise SystemExit("end missing")
text = text.replace(old_end, new_end, 1)

out = b"\xef\xbb\xbf" + text.encode("utf-8")
p.write_bytes(out)
print("patched ok", len(text))
