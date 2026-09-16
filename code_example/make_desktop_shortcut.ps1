$ErrorActionPreference = 'Stop'
$desktop = [Environment]::GetFolderPath('Desktop')
$proj = 'E:\solarautotestnewui'
$bat = Join-Path $proj 'start_SolarAutoTest.bat'
$icon = Join-Path $proj 'ui_files\logo.ico'
$lnkPath = Join-Path $desktop 'SolarAutoTest.lnk'

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($lnkPath)
$shortcut.TargetPath = $bat
$shortcut.WorkingDirectory = $proj
$shortcut.WindowStyle = 1
$shortcut.Description = 'SolarAutoTest'
if (Test-Path $icon) {
    $shortcut.IconLocation = "$icon,0"
}
$shortcut.Save()

Write-Output "OK $lnkPath"
Get-Item $lnkPath | Format-List FullName, Length, LastWriteTime
