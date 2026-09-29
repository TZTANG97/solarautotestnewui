# -*- coding: utf-8 -*-
"""Patch Install-SolarAutoTest.ps1 for custom install/data/runtime paths."""
from __future__ import annotations

from pathlib import Path


def main() -> None:
    p = Path(r"E:\solarautotestnewui\packaging\Install-SolarAutoTest.ps1")
    text = p.read_text(encoding="utf-8-sig")

    old_param = (
        "param(\n"
        '    [string]$InstallDir = "",\n'
        "    [switch]$SkipShortcut,\n"
        "    [switch]$SkipSync,\n"
        "    [switch]$SkipVerify,\n"
        "    [switch]$Quiet\n"
        ")"
    )
    new_param = (
        "param(\n"
        '    [string]$InstallDir = "",\n'
        '    [string]$DataDir = "",\n'
        '    [string]$RuntimeDir = "",\n'
        "    [switch]$SkipShortcut,\n"
        "    [switch]$SkipSync,\n"
        "    [switch]$SkipVerify,\n"
        "    [switch]$Quiet,\n"
        "    [switch]$NoPrompt\n"
        ")"
    )
    if old_param not in text:
        raise SystemExit("param missing")
    text = text.replace(old_param, new_param, 1)

    needle = '$ErrorActionPreference = "Stop"\n$ProgressPreference = "SilentlyContinue"\n'
    if "Install-PathHelpers.ps1" not in text:
        if needle not in text:
            raise SystemExit("ErrorAction needle missing")
        text = text.replace(
            needle,
            needle + '\n. (Join-Path $PSScriptRoot "Install-PathHelpers.ps1")\n',
            1,
        )

    old_local = (
        "        'REM Split path: avoid mid-upgrade bat rewrite eating LOCAL_ROOT',\n"
        "        'set \"LOCAL_ROOT=%LOCALAPPDATA%\"',\n"
        "        'if not defined LOCAL_ROOT set \"LOCAL_ROOT=%USERPROFILE%\\AppData\\Local\"',\n"
        "        'set \"LOCAL_ROOT=%LOCAL_ROOT%\\SolarAutoTestRuntime\"',"
    )
    new_local = (
        "        'REM Runtime root: runtime_root.txt in install dir, else LOCALAPPDATA',\n"
        "        'set \"LOCAL_ROOT=\"',\n"
        "        'if exist \"%~dp0runtime_root.txt\" set /p LOCAL_ROOT=<\"%~dp0runtime_root.txt\"',\n"
        "        'if not defined LOCAL_ROOT (',\n"
        "        '    set \"LOCAL_ROOT=%LOCALAPPDATA%\"',\n"
        "        '    if not defined LOCAL_ROOT set \"LOCAL_ROOT=%USERPROFILE%\\AppData\\Local\"',\n"
        "        '    set \"LOCAL_ROOT=%LOCAL_ROOT%\\SolarAutoTestRuntime\"',\n"
        "        ')',"
    )
    if old_local not in text:
        raise SystemExit("LOCAL_ROOT missing")
    text = text.replace(old_local, new_local, 1)

    old_sync = (
        "function Invoke-UvSync([string]$InstallRoot, [string]$UvExe) {\n"
        '    Write-Step "Syncing Python environment (first run may take several minutes)"\n'
        '    $runtime = Join-Path $env:LOCALAPPDATA "SolarAutoTestRuntime"\n'
        "    Ensure-Directory $runtime"
    )
    new_sync = (
        'function Invoke-UvSync([string]$InstallRoot, [string]$UvExe, [string]$RuntimeRoot = "") {\n'
        '    Write-Step "Syncing Python environment (first run may take several minutes)"\n'
        "    $runtime = $RuntimeRoot\n"
        "    if (-not $runtime) {\n"
        '        $ptr = Join-Path $InstallRoot "runtime_root.txt"\n'
        "        if (Test-Path $ptr) {\n"
        '            try { $runtime = ((Get-Content -Path $ptr -TotalCount 1) + "").Trim() } catch {}\n'
        "        }\n"
        "    }\n"
        "    if (-not $runtime) {\n"
        "        $runtime = Resolve-ClassicRuntime $InstallRoot\n"
        "    }\n"
        "    Ensure-Directory $runtime"
    )
    if old_sync not in text:
        raise SystemExit("Invoke-UvSync missing")
    text = text.replace(old_sync, new_sync, 1)

    old_resolve = (
        "$packageRoot = Get-PackageRoot\n"
        "$source = Get-SourceAppDir\n"
        "\n"
        "if (-not $InstallDir) {\n"
        '    $InstallDir = Join-Path $env:LOCALAPPDATA "SolarAutoTest"\n'
        "}\n"
        "$InstallDir = [System.IO.Path]::GetFullPath($InstallDir)"
    )
    new_resolve = r"""$packageRoot = Get-PackageRoot
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
$script:ResolvedRuntimeDir = [System.IO.Path]::GetFullPath($script:ResolvedRuntimeDir)"""
    if old_resolve not in text:
        raise SystemExit("resolve missing")
    text = text.replace(old_resolve, new_resolve, 1)

    old_print = (
        'Write-Host ("Install dir: " + $InstallDir)\n'
        'Write-Host ("Source dir:  " + $source)'
    )
    new_print = (
        'Write-Host ("Install dir: " + $InstallDir)\n'
        'Write-Host ("Data dir:    " + $script:ResolvedDataDir)\n'
        'Write-Host ("Runtime dir: " + $script:ResolvedRuntimeDir)\n'
        'Write-Host ("Source dir:  " + $source)'
    )
    if old_print not in text:
        raise SystemExit("print missing")
    text = text.replace(old_print, new_print, 1)

    old_bak = (
        'foreach ($name in @("solar_machine_id", "solar_agent.json")) {\n'
        "    $srcId = Join-Path $configDir $name\n"
        "    if (Test-Path $srcId) {\n"
        "        Copy-Item -Force $srcId (Join-Path $identityBackup $name)\n"
        "    }\n"
        "}"
    )
    new_bak = (
        'foreach ($name in @("solar_machine_id", "solar_agent.json")) {\n'
        "    $srcId = Join-Path $configDir $name\n"
        "    if (Test-Path $srcId) {\n"
        "        Copy-Item -Force $srcId (Join-Path $identityBackup $name)\n"
        "    }\n"
        "}\n"
        'foreach ($name in @("paths.ini", "runtime_root.txt")) {\n'
        '    $srcPath = if ($name -eq "paths.ini") {\n'
        '        Join-Path $InstallDir "config_files\\paths.ini"\n'
        "    } else {\n"
        "        Join-Path $InstallDir $name\n"
        "    }\n"
        "    if (Test-Path $srcPath) {\n"
        "        Copy-Item -Force $srcPath (Join-Path $identityBackup $name)\n"
        "    }\n"
        "}"
    )
    if old_bak not in text:
        raise SystemExit("backup missing")
    text = text.replace(old_bak, new_bak, 1)

    marker = "Copy-AppFiles -Source $source -Destination $InstallDir\n"
    insert = (
        "Copy-AppFiles -Source $source -Destination $InstallDir\n"
        "\n"
        "# Keep previous custom paths on upgrade unless DataDir/RuntimeDir explicitly passed\n"
        '$bakPaths = Join-Path $identityBackup "paths.ini"\n'
        '$bakRuntime = Join-Path $identityBackup "runtime_root.txt"\n'
        "if ((-not $DataDir) -and (Test-Path $bakPaths)) {\n"
        "    try {\n"
        "        foreach ($line in (Get-Content -Path $bakPaths -ErrorAction Stop)) {\n"
        "            if ($line -match '^\\s*data_root\\s*=\\s*(.+)$') {\n"
        '                $script:ResolvedDataDir = [System.IO.Path]::GetFullPath($Matches[1].Trim().Trim(\'"\'))\n'
        "            }\n"
        "            if ((-not $RuntimeDir) -and ($line -match '^\\s*runtime_root\\s*=\\s*(.+)$')) {\n"
        '                $script:ResolvedRuntimeDir = [System.IO.Path]::GetFullPath($Matches[1].Trim().Trim(\'"\'))\n'
        "            }\n"
        "        }\n"
        "    } catch {}\n"
        "}\n"
        "if ((-not $RuntimeDir) -and (Test-Path $bakRuntime)) {\n"
        "    try {\n"
        '        $line = ((Get-Content -Path $bakRuntime -TotalCount 1) + "").Trim()\n'
        "        if ($line) { $script:ResolvedRuntimeDir = [System.IO.Path]::GetFullPath($line) }\n"
        "    } catch {}\n"
        "}\n"
        "Ensure-Directory $script:ResolvedDataDir\n"
        "Ensure-Directory $script:ResolvedRuntimeDir\n"
        "Write-PathsConfig -InstallRoot $InstallDir -DataRoot $script:ResolvedDataDir -RuntimeRoot $script:ResolvedRuntimeDir\n"
    )
    if marker not in text:
        raise SystemExit("Copy-AppFiles missing")
    text = text.replace(marker, insert, 1)

    old_call = "    Invoke-UvSync -InstallRoot $InstallDir -UvExe $uv\n"
    new_call = "    Invoke-UvSync -InstallRoot $InstallDir -UvExe $uv -RuntimeRoot $script:ResolvedRuntimeDir\n"
    if old_call not in text:
        raise SystemExit("uv sync call missing")
    text = text.replace(old_call, new_call, 1)

    old_end = (
        'Write-Host ("App: " + $InstallDir)\n'
        'Write-Host ("Start: " + $launcher)\n'
        "exit 0"
    )
    new_end = (
        'Write-Host ("App: " + $InstallDir)\n'
        'Write-Host ("Data: " + $script:ResolvedDataDir)\n'
        'Write-Host ("Runtime: " + $script:ResolvedRuntimeDir)\n'
        'Write-Host ("Start: " + $launcher)\n'
        'Write-Host "To move disks later: re-run install.bat or edit config_files\\paths.ini and runtime_root.txt"\n'
        "exit 0"
    )
    if old_end not in text:
        raise SystemExit("end missing")
    text = text.replace(old_end, new_end, 1)

    p.write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))
    print("patched ok", len(text))


if __name__ == "__main__":
    main()
