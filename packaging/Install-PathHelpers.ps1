#Requires -Version 5.1
# Dot-sourced by Install-SolarAutoTest.ps1 for custom install/data/runtime paths.

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
    if (-not $Root) { return $result }
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
            foreach ($line in (Get-Content -Path $ini -ErrorAction Stop)) {
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
        if ($dlg.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK -and $dlg.SelectedPath) {
            return $dlg.SelectedPath
        }
    } catch {
        Write-Host ("[WARN] Folder dialog unavailable: " + $_.Exception.Message) -ForegroundColor Yellow
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
    Write-Host " Choose install locations (can be outside C:)" -ForegroundColor Cyan
    Write-Host "============================================================"
    Write-Host ("Default app:     " + $DefaultInstall)
    Write-Host ("Default data:    " + $DefaultData)
    Write-Host ("Default runtime: " + $DefaultRuntime)
    Write-Host "Enter=default | type a path | B=browse folder"
    Write-Host ""

    $inst = $DefaultInstall
    $ans = Read-Host "App install directory"
    if ($ans -eq "B" -or $ans -eq "b") {
        $picked = Choose-Folder "Select SolarAutoTest install folder" $DefaultInstall
        if ($picked) {
            if ((Split-Path -Leaf $picked) -ieq "SolarAutoTest") { $inst = $picked }
            else { $inst = Join-Path $picked "SolarAutoTest" }
        }
    } elseif ($ans) {
        $inst = $ans.Trim().Trim('"')
    }

    $data = if ($DefaultData) { $DefaultData } else { Join-Path $inst "data" }
    $ans = Read-Host ("Data directory (config/presets/test files) [" + $data + "]")
    if ($ans -eq "B" -or $ans -eq "b") {
        $picked = Choose-Folder "Select data directory" $data
        if ($picked) { $data = $picked }
    } elseif ($ans) {
        $data = $ans.Trim().Trim('"')
    }

    $runtime = if ($DefaultRuntime) { $DefaultRuntime } else { Join-Path $inst "runtime" }
    $ans = Read-Host ("Runtime directory (.venv / uv cache) [" + $runtime + "]")
    if ($ans -eq "B" -or $ans -eq "b") {
        $picked = Choose-Folder "Select runtime directory" $runtime
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
    if (-not (Test-Path $cfgDir)) {
        New-Item -ItemType Directory -Path $cfgDir -Force | Out-Null
    }
    $ini = Join-Path $cfgDir "paths.ini"
    $lines = @(
        "[paths]",
        ("data_root = " + $DataRoot),
        ("runtime_root = " + $RuntimeRoot),
        "",
        "# Env override: SOLARAUTOTEST_DATA / SOLARAUTOTEST_RUNTIME",
        "# Edit this file then restart the app."
    )
    $utf8Bom = New-Object System.Text.UTF8Encoding $true
    [System.IO.File]::WriteAllLines($ini, $lines, $utf8Bom)
    $txt = Join-Path $InstallRoot "runtime_root.txt"
    [System.IO.File]::WriteAllText($txt, ($RuntimeRoot.Trim() + "`r`n"), $utf8Bom)
    Write-Host ("[OK] Paths written: " + $ini) -ForegroundColor Green
    Write-Host ("[OK] Runtime pointer: " + $txt) -ForegroundColor Green
}

function Resolve-ClassicRuntime([string]$InstallRoot) {
    # Old installs under %LOCALAPPDATA%\SolarAutoTest kept venv in SolarAutoTestRuntime
    $localApp = Join-Path $env:LOCALAPPDATA "SolarAutoTest"
    try {
        $a = [System.IO.Path]::GetFullPath($InstallRoot)
        $b = [System.IO.Path]::GetFullPath($localApp)
        if ($a -ieq $b) {
            return (Join-Path $env:LOCALAPPDATA "SolarAutoTestRuntime")
        }
    } catch {}
    return (Join-Path $InstallRoot "runtime")
}

function Resolve-ClassicData([string]$InstallRoot) {
    $localApp = Join-Path $env:LOCALAPPDATA "SolarAutoTest"
    try {
        $a = [System.IO.Path]::GetFullPath($InstallRoot)
        $b = [System.IO.Path]::GetFullPath($localApp)
        if ($a -ieq $b) {
            return $localApp
        }
    } catch {}
    return (Join-Path $InstallRoot "data")
}

function Test-UvRuntimeReady([string]$RuntimeRoot) {
    if (-not $RuntimeRoot) { return $false }
    try {
        $py = Join-Path $RuntimeRoot ".venv\Scripts\python.exe"
        return (Test-Path $py)
    } catch {
        return $false
    }
}

function Find-ReusableUvRuntime([string]$Preferred = "") {
    # Prefer an already-synced .venv (avoids re-downloading PyPI / Python after folder moves).
    $cands = New-Object System.Collections.Generic.List[string]
    if ($Preferred) { [void]$cands.Add($Preferred) }
    if ($env:SOLARAUTOTEST_RUNTIME) { [void]$cands.Add($env:SOLARAUTOTEST_RUNTIME) }
    [void]$cands.Add((Join-Path $env:LOCALAPPDATA "SolarAutoTestRuntime"))
    [void]$cands.Add((Join-Path $env:LOCALAPPDATA "SolarAutoTest\runtime"))
    foreach ($drive in @("D:", "E:", "F:", "C:")) {
        if (-not (Test-Path ($drive + "\"))) { continue }
        [void]$cands.Add((Join-Path $drive "SolarAutoTest\runtime"))
        [void]$cands.Add((Join-Path $drive "SolarAutoTestRuntime"))
    }
    $seen = @{}
    foreach ($c in $cands) {
        if (-not $c) { continue }
        try {
            $full = [System.IO.Path]::GetFullPath($c)
        } catch {
            continue
        }
        $key = $full.ToLowerInvariant()
        if ($seen.ContainsKey($key)) { continue }
        $seen[$key] = $true
        if (Test-UvRuntimeReady $full) { return $full }
    }
    return ""
}

function Set-UvDownloadMirrors {
    # Speed up first sync in China; existing env wins.
    if (-not $env:UV_DEFAULT_INDEX -and -not $env:UV_INDEX_URL) {
        $env:UV_DEFAULT_INDEX = "https://mirrors.aliyun.com/pypi/simple/"
    }
    if (-not $env:UV_PYTHON_INSTALL_MIRROR) {
        # Same layout as GitHub python-build-standalone releases
        $env:UV_PYTHON_INSTALL_MIRROR = "https://cdn.npmmirror.com/binaries/python-build-standalone"
    }
}
