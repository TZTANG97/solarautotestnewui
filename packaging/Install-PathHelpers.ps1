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
    # Index mirror is used when uv resolves (uv sync without --frozen).
    # uv sync --frozen ignores this and downloads lockfile URLs; see
    # Invoke-UvSyncFromChinaMirrors for that path. Existing env wins.
    if (-not $env:UV_DEFAULT_INDEX -and -not $env:UV_INDEX_URL) {
        $env:UV_DEFAULT_INDEX = "https://mirrors.aliyun.com/pypi/simple/"
    }
    if (-not $env:UV_PYTHON_INSTALL_MIRROR) {
        # Same layout as GitHub python-build-standalone releases
        $env:UV_PYTHON_INSTALL_MIRROR = "https://cdn.npmmirror.com/binaries/python-build-standalone"
    }
}

function Get-ChinaPypiPackageBases {
    # Same path layout as https://files.pythonhosted.org/packages/...
    # so lockfile hashes stay valid.
    return @(
        "https://mirrors.aliyun.com/pypi/packages",
        "https://mirrors.cloud.tencent.com/pypi/packages",
        "https://mirrors.huaweicloud.com/repository/pypi/packages",
        "https://pypi.tuna.tsinghua.edu.cn/packages"
    )
}

function Get-ChinaPythonMirrors {
    $list = New-Object System.Collections.Generic.List[string]
    if ($env:UV_PYTHON_INSTALL_MIRROR) {
        [void]$list.Add($env:UV_PYTHON_INSTALL_MIRROR.TrimEnd("/"))
    }
    foreach ($m in @(
        "https://cdn.npmmirror.com/binaries/python-build-standalone",
        "https://registry.npmmirror.com/-/binary/python-build-standalone"
    )) {
        if (-not $list.Contains($m)) { [void]$list.Add($m) }
    }
    return $list
}

function Install-UvPythonForSync {
    param([Parameter(Mandatory)][string]$UvExe)
    $prev = $env:UV_PYTHON_DOWNLOADS
    $env:UV_PYTHON_DOWNLOADS = "never"
    & $UvExe python find 3.14 2>$null | Out-Null
    $found = ($LASTEXITCODE -eq 0)
    if ($null -eq $prev -or $prev -eq "") {
        Remove-Item Env:UV_PYTHON_DOWNLOADS -ErrorAction SilentlyContinue
    } else {
        $env:UV_PYTHON_DOWNLOADS = $prev
    }
    if ($found) { return }

    Write-Host "  本机还没有 Python 3.14，正在从国内镜像安装解释器"
    $last = "python install failed"
    foreach ($mirror in (Get-ChinaPythonMirrors)) {
        Write-Host ("  Python mirror: " + $mirror)
        try {
            & $UvExe python install 3.14 --mirror $mirror
        } catch {
            $LASTEXITCODE = 1
        }
        if ($LASTEXITCODE -eq 0) { return }
        $last = "python install failed via " + $mirror + " exit " + $LASTEXITCODE
        Write-Host ("  [WARN] " + $last)
    }
    Write-Host ("  [WARN] " + $last + " ; uv sync will try again")
}

function Invoke-UvSyncFromChinaMirrors {
    <#
      uv sync --frozen installs the exact URLs in uv.lock
      (https://files.pythonhosted.org/packages/...), and ignores UV_DEFAULT_INDEX.
      Rewrite those URLs to a China mirror with the same /packages/ path, sync,
      then restore the original lock so upgrade hashes stay stable.
    #>
    param(
        [Parameter(Mandatory)][string]$UvExe,
        [Parameter(Mandatory)][string]$ProjectDir
    )
    $lockPath = Join-Path $ProjectDir "uv.lock"
    if (-not (Test-Path -LiteralPath $lockPath)) {
        throw ("uv.lock not found: " + $lockPath)
    }
    $utf8 = New-Object System.Text.UTF8Encoding $false
    $original = [System.IO.File]::ReadAllText($lockPath)
    $marker = "https://files.pythonhosted.org/packages"
    $synced = $false
    Push-Location $ProjectDir
    try {
        if ($original.Contains($marker)) {
            foreach ($base in (Get-ChinaPypiPackageBases)) {
                $patched = $original.Replace($marker, $base.TrimEnd("/"))
                [System.IO.File]::WriteAllText($lockPath, $patched, $utf8)
                Write-Host ("  依赖包改从国内镜像下载: " + $base)
                try {
                    & $UvExe sync --frozen
                } catch {
                    $LASTEXITCODE = 1
                }
                if ($LASTEXITCODE -eq 0) {
                    $synced = $true
                    break
                }
                Write-Host ("  [WARN] 该镜像失败，换下一个。exit=" + $LASTEXITCODE)
            }
        } else {
            try {
                & $UvExe sync --frozen
            } catch {
                $LASTEXITCODE = 1
            }
            $synced = ($LASTEXITCODE -eq 0)
        }
    }
    finally {
        try { [System.IO.File]::WriteAllText($lockPath, $original, $utf8) } catch {}
        Pop-Location
    }
    if ($synced) { return }

    Write-Host "  国内文件镜像都失败，改为按阿里云索引重新解析依赖"
    Set-UvDownloadMirrors
    Push-Location $ProjectDir
    try {
        try {
            & $UvExe sync
        } catch {
            $LASTEXITCODE = 1
        }
        if ($LASTEXITCODE -ne 0) {
            throw ("uv sync failed, exit code " + $LASTEXITCODE)
        }
    }
    finally {
        Pop-Location
    }
}

function Sync-SolarAutoTestRuntime {
    <#
      Startup path. uv run --frozen downloads lockfile URLs from
      files.pythonhosted.org and ignores UV_DEFAULT_INDEX. That is the
      "Preparing packages" window at ~100 KiB/s.
      If the venv is already complete, offline sync returns immediately.
      Otherwise install from a China /packages/ mirror, then the later
      uv run sees the packages and does not hit the foreign file host.
    #>
    param(
        [Parameter(Mandatory)][string]$UvExe,
        [Parameter(Mandatory)][string]$ProjectDir
    )
    if (-not (Test-Path -LiteralPath $UvExe)) {
        throw ("uv.exe not found: " + $UvExe)
    }
    Set-UvDownloadMirrors
    $runtime = ""
    $ptr = Join-Path $ProjectDir "runtime_root.txt"
    if (Test-Path -LiteralPath $ptr) {
        try { $runtime = ((Get-Content -Path $ptr -TotalCount 1) + "").Trim() } catch {}
    }
    if (-not $runtime) {
        $runtime = Join-Path $env:LOCALAPPDATA "SolarAutoTestRuntime"
    }
    $env:UV_PROJECT_ENVIRONMENT = Join-Path $runtime ".venv"
    $env:UV_PYTHON_INSTALL_DIR = Join-Path $runtime "python"
    $env:UV_CACHE_DIR = Join-Path $runtime "uv-cache"
    foreach ($d in @($runtime, $env:UV_PROJECT_ENVIRONMENT, $env:UV_PYTHON_INSTALL_DIR, $env:UV_CACHE_DIR)) {
        if (-not (Test-Path -LiteralPath $d)) {
            New-Item -ItemType Directory -Force -Path $d | Out-Null
        }
    }
    $script:SolarUvFetched = $false
    $py = Join-Path $env:UV_PROJECT_ENVIRONMENT "Scripts\python.exe"
    if (Test-Path -LiteralPath $py) {
        Push-Location $ProjectDir
        try {
            & $UvExe sync --frozen --offline
            if ($LASTEXITCODE -eq 0) { return }
        } catch {
            $LASTEXITCODE = 1
        } finally {
            Pop-Location
        }
    }
    $script:SolarUvFetched = $true
    Write-Host "环境未就绪，正在从国内镜像下载依赖（不走 files.pythonhosted.org）"
    Install-UvPythonForSync -UvExe $UvExe
    Invoke-UvSyncFromChinaMirrors -UvExe $UvExe -ProjectDir $ProjectDir
}
