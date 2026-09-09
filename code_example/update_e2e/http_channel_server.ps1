#Requires -Version 5.1
param(
    [string]$Root = "",
    [int]$Port = 18765
)
$ErrorActionPreference = "Stop"
if (-not $Root) { $Root = Join-Path $PSScriptRoot "channel" }
$prefix = "http://127.0.0.1:$Port/"
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add($prefix)
try {
    $listener.Start()
} catch {
    # URL ACL may be needed; try localhost reservation fallback message
    throw
}
Set-Content -Path (Join-Path $env:TEMP "sat_e2e_http_ready.txt") -Value $prefix -Encoding ascii
Write-Host "READY $prefix"
while ($listener.IsListening) {
    $ctx = $listener.GetContext()
    $path = [Uri]::UnescapeDataString($ctx.Request.Url.AbsolutePath.TrimStart('/'))
    if ([string]::IsNullOrWhiteSpace($path)) { $path = "latest.json" }
    $file = Join-Path $Root $path
    if (-not (Test-Path -LiteralPath $file)) {
        $ctx.Response.StatusCode = 404
        $msg = [Text.Encoding]::UTF8.GetBytes("not found")
        $ctx.Response.OutputStream.Write($msg, 0, $msg.Length)
        $ctx.Response.Close()
        continue
    }
    $bytes = [IO.File]::ReadAllBytes($file)
    $ctx.Response.StatusCode = 200
    $ctx.Response.ContentLength64 = $bytes.LongLength
    if ($path -like "*.json") { $ctx.Response.ContentType = "application/json" }
    else { $ctx.Response.ContentType = "application/zip" }
    $ctx.Response.OutputStream.Write($bytes, 0, $bytes.Length)
    $ctx.Response.Close()
}
