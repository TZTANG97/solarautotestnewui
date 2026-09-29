$e=$null
[void][System.Management.Automation.Language.Parser]::ParseFile("E:\solarautotestnewui\packaging\Install-PathHelpers.ps1",[ref]$null,[ref]$e)
if($e -and $e.Count -gt 0){$e[0].ToString(); exit 1} else {"HELPERS_PARSE_OK"}
