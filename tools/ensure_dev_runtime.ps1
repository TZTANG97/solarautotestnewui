#Requires -Version 5.1
<#
.SYNOPSIS
  测试版启动前自动补齐本机环境（对齐桌面版 Start 前的 Sync-SolarAutoTestRuntime）。
  使用 %LOCALAPPDATA%\SolarAutoTestDev 作为 runtime，不碰正式安装目录。
#>
param(
    [Parameter(Mandatory = $true)][string]$UvExe,
    [Parameter(Mandatory = $true)][string]$ProjectDir,
    [Parameter(Mandatory = $true)][string]$LocalRoot
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$helpers = Join-Path (Split-Path -Parent $PSScriptRoot) "packaging\Install-PathHelpers.ps1"
if (-not (Test-Path -LiteralPath $helpers)) {
    Write-Host "[ERROR] Missing: $helpers" -ForegroundColor Red
    exit 1
}
. $helpers

if (-not (Test-Path -LiteralPath $UvExe)) {
    Write-Host "[ERROR] uv.exe not found: $UvExe" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path -LiteralPath (Join-Path $ProjectDir "SCPITestWave.py"))) {
    Write-Host "[ERROR] Not a SolarAutoTest project: $ProjectDir" -ForegroundColor Red
    exit 1
}

Set-UvDownloadMirrors
Write-Host ("  UV_DEFAULT_INDEX=" + $env:UV_DEFAULT_INDEX)
Write-Host ("  UV_PYTHON_INSTALL_MIRROR=" + $env:UV_PYTHON_INSTALL_MIRROR)

$runtime = [System.IO.Path]::GetFullPath($LocalRoot)
$env:UV_PROJECT_ENVIRONMENT = Join-Path $runtime ".venv"
$env:UV_PYTHON_INSTALL_DIR = Join-Path $runtime "python"
$env:UV_CACHE_DIR = Join-Path $runtime "uv-cache"
foreach ($d in @($runtime, $env:UV_PROJECT_ENVIRONMENT, $env:UV_PYTHON_INSTALL_DIR, $env:UV_CACHE_DIR)) {
    if (-not (Test-Path -LiteralPath $d)) {
        New-Item -ItemType Directory -Force -Path $d | Out-Null
    }
}

$py = Join-Path $env:UV_PROJECT_ENVIRONMENT "Scripts\python.exe"
if (Test-Path -LiteralPath $py) {
    Push-Location $ProjectDir
    try {
        Write-Host "[INFO] Checking local venv (offline sync)..."
        & $UvExe sync --frozen --offline
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Local runtime ready: $env:UV_PROJECT_ENVIRONMENT" -ForegroundColor Green
            exit 0
        }
    } catch {
        $LASTEXITCODE = 1
    } finally {
        Pop-Location
    }
}

Write-Host "环境未就绪，正在自动安装 Python / 依赖（国内镜像）..." -ForegroundColor Cyan
Write-Host ("Runtime: " + $env:UV_PROJECT_ENVIRONMENT)
Install-UvPythonForSync -UvExe $UvExe
try {
    Invoke-UvSyncFromChinaMirrors -UvExe $UvExe -ProjectDir $ProjectDir
} catch {
    Write-Host ("[ERROR] " + $_.Exception.Message) -ForegroundColor Red
    exit 1
}

if (-not (Test-Path -LiteralPath $py)) {
    Write-Host "[ERROR] python.exe still missing after sync: $py" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Dev runtime installed: $env:UV_PROJECT_ENVIRONMENT" -ForegroundColor Green
exit 0
