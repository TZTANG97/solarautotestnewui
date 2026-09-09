#Requires -Version 5.1
<#
.SYNOPSIS
  Post-install health check for SolarAutoTest.
#>
[CmdletBinding()]
param(
    [string]$InstallDir = ""
)

$ErrorActionPreference = "Continue"
$failed = 0

function Pass([string]$msg) { Write-Host ("[PASS] " + $msg) -ForegroundColor Green }
function Fail([string]$msg) { Write-Host ("[FAIL] " + $msg) -ForegroundColor Red; $script:failed++ }
function Info([string]$msg) { Write-Host ("[INFO] " + $msg) }

if (-not $InstallDir) {
    $InstallDir = Join-Path $env:LOCALAPPDATA "SolarAutoTest"
}
$InstallDir = [System.IO.Path]::GetFullPath($InstallDir)
Info ("Install dir: " + $InstallDir)

if (-not (Test-Path $InstallDir)) {
    Fail "Install directory does not exist"
    exit 1
}

$required = @(
    "SCPITestWave.py",
    "pyproject.toml",
    "uv.lock",
    "Start-SolarAutoTest.bat",
    "tools\uv.exe"
)
foreach ($rel in $required) {
    $p = Join-Path $InstallDir $rel
    if (Test-Path $p) { Pass $rel } else { Fail ("Missing " + $rel) }
}

$uv = Join-Path $InstallDir "tools\uv.exe"
if (Test-Path $uv) {
    try {
        $ver = & $uv --version 2>&1 | Out-String
        if ($LASTEXITCODE -eq 0) { Pass ("uv runs: " + $ver.Trim()) } else { Fail "uv --version failed" }
    } catch {
        Fail ("uv cannot run: " + $_.Exception.Message)
    }
}

$runtime = Join-Path $env:LOCALAPPDATA "SolarAutoTestRuntime"
$env:UV_PROJECT_ENVIRONMENT = Join-Path $runtime ".venv"
$env:UV_PYTHON_INSTALL_DIR = Join-Path $runtime "python"
$env:UV_CACHE_DIR = Join-Path $runtime "uv-cache"

Push-Location $InstallDir
try {
    if (Test-Path $uv) {
        Info "Import check (PyQt5 / numpy / pyvisa) ..."
        & $uv run --frozen python -c "import sys; print('python', sys.version); import PyQt5; import numpy; import pyvisa; import psutil; print('IMPORT_OK')"
        if ($LASTEXITCODE -eq 0) {
            Pass "Core imports OK"
        } else {
            Fail "Core imports failed (re-run installer)"
        }

        Info "Syntax check SCPITestWave.py ..."
        & $uv run --frozen python -c "import ast; ast.parse(open('SCPITestWave.py', encoding='utf-8').read()); print('SYNTAX_OK')"
        if ($LASTEXITCODE -eq 0) { Pass "SCPITestWave.py syntax OK" } else { Fail "SCPITestWave.py syntax failed" }

        Info "Syntax check Dialog_thai*.py ..."
        & $uv run --frozen python -c @"
from pathlib import Path
import ast, sys
errs=[]
for p in sorted(Path('.').glob('Dialog_thai*.py')):
    try:
        ast.parse(p.read_text(encoding='utf-8'))
    except SyntaxError as e:
        errs.append(f'{p.name}:{e.lineno}: {e.msg}')
if errs:
    print('DIALOG_SYNTAX_FAIL')
    print('\n'.join(errs))
    sys.exit(1)
print('DIALOG_SYNTAX_OK', len(list(Path('.').glob('Dialog_thai*.py'))))
"@
        if ($LASTEXITCODE -eq 0) { Pass "Dialog_thai*.py syntax OK" } else { Fail "Dialog_thai*.py syntax failed" }

        Info "Overfreq cross smoke (no instruments) ..."
        $smoke = Join-Path $InstallDir "code_example\test_overfreq_cross_smoke.py"
        if (Test-Path $smoke) {
            & $uv run --frozen python $smoke
            if ($LASTEXITCODE -eq 0) { Pass "Overfreq cross smoke OK" } else { Fail "Overfreq cross smoke failed" }
        } else {
            Info "Smoke script not packaged, skip"
        }
    }
}
finally {
    Pop-Location
}

Write-Host ""
if ($failed -gt 0) {
    Write-Host ("Verify failed: " + $failed + " item(s)") -ForegroundColor Red
    exit 1
}
Write-Host "All verify checks passed" -ForegroundColor Green
exit 0
