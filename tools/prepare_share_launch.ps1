# Prepare launch on a shared/network project folder:
# 1) copy uv.exe to local AppData (Windows often blocks running exe from UNC)
# 2) report whether local/share venv exists
param(
    [Parameter(Mandatory = $true)][string]$ProjectRoot,
    [Parameter(Mandatory = $true)][string]$LocalRoot
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path $ProjectRoot).Path
$toolsUv = Join-Path $ProjectRoot "tools\uv.exe"
$localUv = Join-Path $LocalRoot "uv.exe"
$shareVenvPy = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$localVenvPy = Join-Path $LocalRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $LocalRoot)) {
    New-Item -ItemType Directory -Path $LocalRoot -Force | Out-Null
}

$isUnc = $ProjectRoot.StartsWith("\\")
$drive = [System.IO.Path]::GetPathRoot($ProjectRoot)
$driveType = $null
try {
    if ($drive -and $drive.Length -ge 2 -and $drive[1] -eq ":") {
        $driveType = (New-Object -ComObject Scripting.FileSystemObject).GetDrive($drive.Substring(0, 2)).DriveType
    }
} catch { }
# DriveType 4 = Network
$isNetwork = $isUnc -or ($driveType -eq 4)

if (Test-Path $toolsUv) {
    $needCopy = $isNetwork
    if (-not (Test-Path $localUv)) { $needCopy = $true }
    elseif ((Get-Item $toolsUv).Length -ne (Get-Item $localUv).Length) { $needCopy = $true }
    if ($needCopy) {
        Copy-Item -Force $toolsUv $localUv
        Write-Host "[INFO] uv.exe copied to local: $localUv"
    }
}

$result = [ordered]@{
    isNetwork = $isNetwork
    localUv = $(if (Test-Path $localUv) { $localUv } else { "" })
    toolsUv = $(if (Test-Path $toolsUv) { $toolsUv } else { "" })
    localVenv = $(if (Test-Path $localVenvPy) { $true } else { $false })
    shareVenv = $(if (Test-Path $shareVenvPy) { $true } else { $false })
}
$result | ConvertTo-Json -Compress
