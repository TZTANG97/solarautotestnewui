# Download portable uv.exe into tools\ (not committed to git).
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$toolsDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$dest = Join-Path $toolsDir "uv.exe"
if (Test-Path $dest) {
    Write-Host "[OK] already exists: $dest"
    exit 0
}

$urls = @(
    "https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip",
    "https://ghproxy.net/https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip"
)

foreach ($u in $urls) {
    try {
        Write-Host "[INFO] download $u"
        $z = Join-Path $env:TEMP ("uv-" + [guid]::NewGuid().ToString() + ".zip")
        $d = Join-Path $env:TEMP ("uvx-" + [guid]::NewGuid().ToString())
        Invoke-WebRequest -Uri $u -OutFile $z -UseBasicParsing
        Expand-Archive -Path $z -DestinationPath $d -Force
        $f = Get-ChildItem -Path $d -Filter "uv.exe" -Recurse | Select-Object -First 1
        if (-not $f) { throw "uv.exe missing in zip" }
        Copy-Item -Force $f.FullName $dest
        Write-Host "[OK] saved $dest"
        exit 0
    }
    catch {
        Write-Host "[WARN] $($_.Exception.Message)"
    }
}

Write-Host "[ERROR] failed to download uv.exe"
exit 1
