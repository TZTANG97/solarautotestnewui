$e = $null
$path = "E:\solarautotestnewui\packaging\Install-SolarAutoTest.ps1"
[void][System.Management.Automation.Language.Parser]::ParseFile($path, [ref]$null, [ref]$e)
if ($e -and $e.Count -gt 0) {
  Write-Host "PARSE_FAIL"
  $e | ForEach-Object { Write-Host $_.ToString() }
  exit 1
}
Write-Host "PARSE_OK"
