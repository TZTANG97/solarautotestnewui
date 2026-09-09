#Requires -Version 5.1
<#
.SYNOPSIS
  Create a GitLab Deploy Token instructions helper + optional save to user env.
  We cannot create tokens without API access; this guides + stores what you paste.
#>
param(
    [string]$Token = "",
    [string]$GitLabUrl = "http://gitlab.wisecom-tech.com",
    [string]$ProjectPath = "solarapp/solarautotest/solarautotestnewui"
)

Write-Host ""
Write-Host "=== GitLab one-time setup (you do in browser) ===" -ForegroundColor Cyan
Write-Host "1) Open: $GitLabUrl/$ProjectPath"
Write-Host "2) Settings → General → Visibility → enable:"
Write-Host "     Allow anyone to pull from Package Registry"
Write-Host "3) Settings → Repository → Deploy tokens → Add token:"
Write-Host "     Name: solarautotest-publish"
Write-Host "     Scopes: write_package_registry, read_package_registry"
Write-Host "     Copy the token password once."
Write-Host ""
Write-Host "4) Then run on THIS PC:"
Write-Host '     $env:SOLARAUTOTEST_GITLAB_TOKEN = ''<paste-token>'''
Write-Host "     [Environment]::SetEnvironmentVariable('SOLARAUTOTEST_GITLAB_TOKEN',$env:SOLARAUTOTEST_GITLAB_TOKEN,'User')"
Write-Host "     packaging\build_release.bat -PublishGitLab"
Write-Host ""

if ($Token) {
    [Environment]::SetEnvironmentVariable("SOLARAUTOTEST_GITLAB_TOKEN", $Token, "User")
    $env:SOLARAUTOTEST_GITLAB_TOKEN = $Token
    Write-Host "[OK] Saved SOLARAUTOTEST_GITLAB_TOKEN to User env for this Windows account." -ForegroundColor Green
}
