#Requires -Version 5.1
<#
.SYNOPSIS
  Check update channel (LAN folder or HTTP/GitLab Package) and upgrade before launch.

.DESCRIPTION
  Reads channel from (first hit wins):
    1) env SOLARAUTOTEST_UPDATE_CHANNEL
    2) <InstallDir>\config_files\config.ini  [update] channel=
    3) <InstallDir>\update_channel.txt

  LAN channel: folder with latest.json + zip.
  HTTP channel: URL to latest.json, or a directory URL that contains latest.json
    (GitLab Generic Package "channel" package version recommended).

  Optional auth (only if Package Registry is private):
    env SOLARAUTOTEST_UPDATE_TOKEN / GITLAB_TOKEN / CI_JOB_TOKEN
    or config.ini [update] token=
  Prefer enabling "Allow anyone to pull from Package Registry" so bench PCs need no token.
#>
[CmdletBinding()]
param(
    [string]$InstallDir = "",
    [switch]$AutoYes,
    [switch]$Quiet
)

$ErrorActionPreference = "Stop"
# Avoid IWR console progress spam; we drive a dedicated UI window instead.
$ProgressPreference = "SilentlyContinue"

try {
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [Console]::OutputEncoding
    chcp 65001 | Out-Null
} catch {}

function Info([string]$m) { if (-not $Quiet) { Write-Host $m } }
function Warn([string]$m) { Write-Host ("[WARN] " + $m) -ForegroundColor Yellow }
function Ok([string]$m) { Write-Host ("[OK] " + $m) -ForegroundColor Green }

# Visible top-most progress window (works even when launched with -WindowStyle Hidden)
$script:updForm = $null
$script:updLabel = $null
$script:updDetail = $null
$script:updPctLabel = $null
$script:updBar = $null
$script:updTrack = $null
$script:updFill = $null
$script:updTimer = $null
$script:updMode = "marquee"   # marquee | continuous
$script:updPulse = 0
$script:updPercent = 0
$script:updColorBg = $null
$script:updColorCard = $null
$script:updColorInk = $null
$script:updColorMuted = $null
$script:updColorAccent = $null
$script:updColorTrack = $null
$script:updColorSoft = $null

function Init-UpdateUiColors {
    if ($script:updColorAccent -ne $null) { return }
    Add-Type -AssemblyName System.Windows.Forms | Out-Null
    Add-Type -AssemblyName System.Drawing | Out-Null
    # Match main app theme (components/ui_theme.py)
    $script:updColorBg = [System.Drawing.Color]::FromArgb(244, 246, 249)      # #f4f6f9
    $script:updColorCard = [System.Drawing.Color]::White
    $script:updColorInk = [System.Drawing.Color]::FromArgb(15, 23, 42)         # #0f172a
    $script:updColorMuted = [System.Drawing.Color]::FromArgb(100, 116, 139)    # #64748b
    $script:updColorAccent = [System.Drawing.Color]::FromArgb(13, 148, 136)    # #0d9488
    $script:updColorTrack = [System.Drawing.Color]::FromArgb(226, 232, 240)    # #e2e8f0
    $script:updColorSoft = [System.Drawing.Color]::FromArgb(204, 251, 241)     # #ccfbf1
}

function Get-UpdateUiIconPath {
    $cands = @()
    if ($PSScriptRoot) {
        $cands += (Join-Path $PSScriptRoot "..\ui_files\logo.ico")
        $cands += (Join-Path $PSScriptRoot "logo.ico")
    }
    if ($InstallDir) {
        $cands += (Join-Path $InstallDir "ui_files\logo.ico")
        $cands += (Join-Path $InstallDir "logo.ico")
        $cands += (Join-Path $InstallDir "app\ui_files\logo.ico")
    }
    foreach ($p in $cands) {
        try {
            $full = [System.IO.Path]::GetFullPath($p)
            if (Test-Path -LiteralPath $full) { return $full }
        } catch {}
    }
    return $null
}

function Set-UpdateFillWidth([int]$Percent) {
    if ($script:updTrack -eq $null -or $script:updFill -eq $null) { return }
    $pct = [Math]::Max(0, [Math]::Min(100, $Percent))
    $tw = [Math]::Max(0, $script:updTrack.ClientSize.Width)
    $fw = [int][Math]::Round($tw * $pct / 100.0)
    if ($fw -lt 0) { $fw = 0 }
    if ($fw -gt $tw) { $fw = $tw }
    $script:updFill.Width = $fw
    $script:updFill.Height = $script:updTrack.ClientSize.Height
    $script:updFill.Left = 0
    $script:updFill.Top = 0
}

function Ensure-UpdateUi {
    if ($Quiet) { return }
    if ($script:updForm -ne $null) { return }
    try {
        Init-UpdateUiColors
        try { [System.Windows.Forms.Application]::EnableVisualStyles() } catch {}
        try { [System.Windows.Forms.Application]::SetCompatibleTextRenderingDefault($false) } catch {}

        $f = New-Object System.Windows.Forms.Form
        $f.Text = "SolarAutoTest"
        $f.Size = New-Object System.Drawing.Size(560, 220)
        $f.MinimumSize = New-Object System.Drawing.Size(520, 200)
        $f.StartPosition = "CenterScreen"
        $f.TopMost = $true
        $f.FormBorderStyle = "FixedDialog"
        $f.MaximizeBox = $false
        $f.MinimizeBox = $false
        $f.ShowInTaskbar = $true
        $f.ControlBox = $false
        $f.BackColor = $script:updColorBg
        $f.Font = New-Object System.Drawing.Font("Microsoft YaHei UI", 9)
        $iconPath = Get-UpdateUiIconPath
        if ($iconPath) {
            try { $f.Icon = New-Object System.Drawing.Icon($iconPath) } catch {}
        }

        # Card panel
        $card = New-Object System.Windows.Forms.Panel
        $card.Location = New-Object System.Drawing.Point(16, 16)
        $card.Size = New-Object System.Drawing.Size(512, 152)
        $card.BackColor = $script:updColorCard
        $card.Anchor = "Top,Left,Right"

        # Accent strip on left
        $strip = New-Object System.Windows.Forms.Panel
        $strip.Location = New-Object System.Drawing.Point(0, 0)
        $strip.Size = New-Object System.Drawing.Size(4, 152)
        $strip.BackColor = $script:updColorAccent
        $strip.Anchor = "Top,Bottom,Left"
        $card.Controls.Add($strip)

        # Brand
        $brand = New-Object System.Windows.Forms.Label
        $brand.AutoSize = $false
        $brand.Location = New-Object System.Drawing.Point(20, 14)
        $brand.Size = New-Object System.Drawing.Size(360, 22)
        $brand.Font = New-Object System.Drawing.Font("Microsoft YaHei UI", 11, [System.Drawing.FontStyle]::Bold)
        $brand.ForeColor = $script:updColorInk
        $brand.Text = "SolarAutoTest"
        $brand.BackColor = $script:updColorCard

        # Step badge
        $badge = New-Object System.Windows.Forms.Label
        $badge.AutoSize = $false
        $badge.Location = New-Object System.Drawing.Point(390, 14)
        $badge.Size = New-Object System.Drawing.Size(106, 22)
        $badge.Font = New-Object System.Drawing.Font("Microsoft YaHei UI", 8, [System.Drawing.FontStyle]::Bold)
        $badge.ForeColor = $script:updColorAccent
        $badge.BackColor = $script:updColorSoft
        $badge.TextAlign = "MiddleCenter"
        $badge.Text = "自动更新"
        $badge.Anchor = "Top,Right"

        # Status
        $lbl = New-Object System.Windows.Forms.Label
        $lbl.AutoSize = $false
        $lbl.Location = New-Object System.Drawing.Point(20, 46)
        $lbl.Size = New-Object System.Drawing.Size(400, 28)
        $lbl.Font = New-Object System.Drawing.Font("Microsoft YaHei UI", 10)
        $lbl.ForeColor = $script:updColorInk
        $lbl.BackColor = $script:updColorCard
        $lbl.Text = "正在启动..."
        $lbl.Anchor = "Top,Left,Right"

        # Percent
        $pct = New-Object System.Windows.Forms.Label
        $pct.AutoSize = $false
        $pct.Location = New-Object System.Drawing.Point(420, 46)
        $pct.Size = New-Object System.Drawing.Size(76, 28)
        $pct.Font = New-Object System.Drawing.Font("Microsoft YaHei UI", 10, [System.Drawing.FontStyle]::Bold)
        $pct.ForeColor = $script:updColorAccent
        $pct.BackColor = $script:updColorCard
        $pct.TextAlign = "MiddleRight"
        $pct.Text = ""
        $pct.Anchor = "Top,Right"

        # Detail / hint
        $det = New-Object System.Windows.Forms.Label
        $det.AutoSize = $false
        $det.Location = New-Object System.Drawing.Point(20, 76)
        $det.Size = New-Object System.Drawing.Size(476, 20)
        $det.Font = New-Object System.Drawing.Font("Microsoft YaHei UI", 8.25)
        $det.ForeColor = $script:updColorMuted
        $det.BackColor = $script:updColorCard
        $det.Text = "请勿关闭此窗口"
        $det.Anchor = "Top,Left,Right"

        # Custom progress track + fill (flat modern, not classic WinForms bar)
        $track = New-Object System.Windows.Forms.Panel
        $track.Location = New-Object System.Drawing.Point(20, 110)
        $track.Size = New-Object System.Drawing.Size(476, 10)
        $track.BackColor = $script:updColorTrack
        $track.Anchor = "Top,Left,Right"

        $fill = New-Object System.Windows.Forms.Panel
        $fill.Location = New-Object System.Drawing.Point(0, 0)
        $fill.Size = New-Object System.Drawing.Size(40, 10)
        $fill.BackColor = $script:updColorAccent
        $track.Controls.Add($fill)

        $card.Controls.Add($brand)
        $card.Controls.Add($badge)
        $card.Controls.Add($lbl)
        $card.Controls.Add($pct)
        $card.Controls.Add($det)
        $card.Controls.Add($track)
        $f.Controls.Add($card)

        # Marquee pulse timer
        $timer = New-Object System.Windows.Forms.Timer
        $timer.Interval = 40
        $timer.Add_Tick({
            try {
                if ($script:updMode -ne "marquee") { return }
                if ($script:updTrack -eq $null -or $script:updFill -eq $null) { return }
                $script:updPulse = ($script:updPulse + 3) % 200
                $tw = [Math]::Max(1, $script:updTrack.ClientSize.Width)
                $block = [Math]::Max(48, [int]($tw * 0.28))
                # 0..100 go right, 100..200 go left
                $phase = $script:updPulse
                if ($phase -le 100) {
                    $t = $phase / 100.0
                } else {
                    $t = (200 - $phase) / 100.0
                }
                $maxL = [Math]::Max(0, $tw - $block)
                $left = [int][Math]::Round($maxL * $t)
                $script:updFill.Width = $block
                $script:updFill.Height = $script:updTrack.ClientSize.Height
                $script:updFill.Left = $left
                $script:updFill.Top = 0
                if ($script:updPctLabel -ne $null) {
                    $script:updPctLabel.Text = ""
                }
            } catch {}
        })

        $f.Show()
        $f.Activate()
        [System.Windows.Forms.Application]::DoEvents()
        $timer.Start()

        $script:updForm = $f
        $script:updLabel = $lbl
        $script:updDetail = $det
        $script:updPctLabel = $pct
        $script:updTrack = $track
        $script:updFill = $fill
        $script:updBar = $fill   # compat alias for old callers
        $script:updTimer = $timer
        $script:updMode = "marquee"
        $script:updPulse = 0
    } catch {
        # Forms unavailable - fall back to console only
    }
}

function Split-UpdateMessage([string]$msg) {
    $main = $msg
    $detail = "请勿关闭此窗口"
    if (-not $msg) { return @{ Main = "正在处理..."; Detail = $detail } }
    # Long path / version trail → subtitle
    if ($msg -match '^(.*?)\s{2,}(.+)$') {
        $main = $Matches[1].Trim()
        $detail = $Matches[2].Trim()
    } elseif ($msg -match '^(正在安装到本机)\.\.\.\s*(.+)$') {
        $main = $Matches[1] + "... 请稍候"
        $p = $Matches[2].Trim()
        if ($p -and $p -ne "请稍候") { $detail = $p }
    } elseif ($msg -match '^(发现新版本)\s+(.+)$') {
        $main = $Matches[1]
        $detail = $Matches[2]
    } elseif ($msg -match '^(已是最新版)\s+(\S+)(.*)$') {
        $main = $Matches[1] + " " + $Matches[2]
        $detail = if ($Matches[3]) { $Matches[3].Trim(" ，,") } else { "正在打开软件..." }
    } elseif ($msg -match '^(升级完成)\s+(\S+)(.*)$') {
        $main = $Matches[1] + " " + $Matches[2]
        $detail = if ($Matches[3]) { $Matches[3].Trim(" ，,") } else { "即将重新启动" }
    } elseif ($msg -match '^(正在下载)\s+(.+)$') {
        $main = $Matches[1] + "..."
        $detail = $Matches[2]
    } elseif ($msg.Length -gt 42) {
        $main = $msg.Substring(0, 40) + "..."
        $detail = $msg
    }
    return @{ Main = $main; Detail = $detail }
}

function Set-UpdateUi([string]$msg) {
    Info $msg
    if ($Quiet) { return }
    Ensure-UpdateUi
    try {
        $parts = Split-UpdateMessage $msg
        if ($script:updLabel -ne $null) {
            $script:updLabel.Text = [string]$parts.Main
        }
        if ($script:updDetail -ne $null) {
            $script:updDetail.Text = [string]$parts.Detail
        }
        $script:updMode = "marquee"
        if ($script:updPctLabel -ne $null) {
            $script:updPctLabel.Text = ""
        }
        if ($script:updTimer -ne $null -and -not $script:updTimer.Enabled) {
            $script:updTimer.Start()
        }
        if ($script:updForm -ne $null) {
            $script:updForm.Activate()
            [System.Windows.Forms.Application]::DoEvents()
        }
    } catch {}
}

function Pump-UpdateUi {
    try {
        if ($script:updForm -ne $null) {
            [System.Windows.Forms.Application]::DoEvents()
        }
    } catch {}
}

function Set-UpdateProgress([int]$Percent, [string]$msg) {
    if (-not $Quiet) {
        Ensure-UpdateUi
        try {
            $script:updMode = "continuous"
            if ($script:updTimer -ne $null -and $script:updTimer.Enabled) {
                # keep timer running for DoEvents friendliness but skip marquee paint
            }
            $pct = [Math]::Max(0, [Math]::Min(100, $Percent))
            $script:updPercent = $pct
            Set-UpdateFillWidth $pct
            if ($script:updPctLabel -ne $null) {
                $script:updPctLabel.Text = ("{0}%" -f $pct)
            }
            if ($msg) {
                $parts = Split-UpdateMessage $msg
                if ($script:updLabel -ne $null) {
                    $script:updLabel.Text = [string]$parts.Main
                }
                if ($script:updDetail -ne $null) {
                    $script:updDetail.Text = [string]$parts.Detail
                }
            }
            Pump-UpdateUi
        } catch {}
    }
    if ($msg) { Info $msg }
}

function Close-UpdateUi {
    try {
        if ($script:updTimer -ne $null) {
            $script:updTimer.Stop()
            $script:updTimer.Dispose()
        }
    } catch {}
    try {
        if ($script:updForm -ne $null) {
            $script:updForm.Close()
            $script:updForm.Dispose()
        }
    } catch {}
    $script:updForm = $null
    $script:updLabel = $null
    $script:updDetail = $null
    $script:updPctLabel = $null
    $script:updBar = $null
    $script:updTrack = $null
    $script:updFill = $null
    $script:updTimer = $null
    $script:updMode = "marquee"
    $script:updPulse = 0
    $script:updPercent = 0
}

function Get-IniValue([string]$Path, [string]$Section, [string]$Key) {
    if (-not (Test-Path $Path)) { return $null }
    $inSection = $false
    foreach ($raw in Get-Content -Path $Path -Encoding UTF8 -ErrorAction SilentlyContinue) {
        $line = $raw.Trim()
        if (-not $line -or $line.StartsWith("#") -or $line.StartsWith(";")) { continue }
        if ($line -match '^\[(.+)\]$') {
            $inSection = ($Matches[1].Trim().ToLowerInvariant() -eq $Section.ToLowerInvariant())
            continue
        }
        if (-not $inSection) { continue }
        $parts = $line.Split("=", 2)
        if ($parts.Count -lt 2) { continue }
        if ($parts[0].Trim().ToLowerInvariant() -eq $Key.ToLowerInvariant()) {
            return $parts[1].Trim()
        }
    }
    return $null
}

function Read-LocalVersion([string]$Root) {
    $p = Join-Path $Root "VERSION"
    if (-not (Test-Path $p)) { return "" }
    $line = (Get-Content -Path $p -TotalCount 1 -ErrorAction SilentlyContinue)
    if ($line) { return $line.Trim() }
    return ""
}

function Resolve-Channel([string]$Root) {
    if ($env:SOLARAUTOTEST_UPDATE_CHANNEL) {
        return $env:SOLARAUTOTEST_UPDATE_CHANNEL.Trim()
    }
    $ini = Join-Path $Root "config_files\config.ini"
    $ch = Get-IniValue $ini "update" "channel"
    if ($ch) { return $ch }
    $txt = Join-Path $Root "update_channel.txt"
    if (Test-Path $txt) {
        $line = (Get-Content -Path $txt -TotalCount 1 -ErrorAction SilentlyContinue)
        if ($line) { return $line.Trim() }
    }
    return ""
}

function Resolve-UpdateToken([string]$Root) {
    foreach ($k in @(
        $env:SOLARAUTOTEST_UPDATE_TOKEN,
        $env:GITLAB_TOKEN,
        $env:GITLAB_DEPLOY_TOKEN,
        $env:CI_JOB_TOKEN
    )) {
        if ($k -and $k.Trim()) { return $k.Trim() }
    }
    $ini = Join-Path $Root "config_files\config.ini"
    $t = Get-IniValue $ini "update" "token"
    if ($t) { return $t.Trim() }
    return ""
}

function New-HttpHeaders([string]$Token) {
    $h = @{
        "Accept" = "application/json, application/octet-stream, */*"
    }
    if (-not $Token) { return $h }
    # Deploy Token / Personal / Project Access -> PRIVATE-TOKEN
    # CI Job Token -> JOB-TOKEN
    if ($env:CI_JOB_TOKEN -and ($Token -eq $env:CI_JOB_TOKEN)) {
        $h["JOB-TOKEN"] = $Token
    } else {
        $h["PRIVATE-TOKEN"] = $Token
    }
    return $h
}

function Is-HttpChannel([string]$Channel) {
    return $Channel -match '^https?://'
}

function Get-ManifestUrl([string]$Channel) {
    $c = $Channel.TrimEnd('/')
    if ($c.ToLowerInvariant().EndsWith("latest.json")) { return $c }
    return ($c + "/latest.json")
}

function Is-UpdateEnabled([string]$Root) {
    if ($env:SOLARAUTOTEST_UPDATE_DISABLE -eq "1") { return $false }
    $ini = Join-Path $Root "config_files\config.ini"
    $v = Get-IniValue $ini "update" "enabled"
    if ($null -eq $v -or $v -eq "") { return $true }
    $v = $v.Trim().ToLowerInvariant()
    return @("1", "true", "yes", "on") -contains $v
}

function Is-AutoInstall([string]$Root) {
    if ($AutoYes) { return $true }
    if ($env:SOLARAUTOTEST_UPDATE_AUTO -eq "1") { return $true }
    $ini = Join-Path $Root "config_files\config.ini"
    $v = Get-IniValue $ini "update" "auto_install"
    if (-not $v) { return $false }
    $v = $v.Trim().ToLowerInvariant()
    return @("1", "true", "yes", "on") -contains $v
}

function Compare-VersionTag([string]$A, [string]$B) {
    $na = 0L; $nb = 0L
    $pa = ($A -replace '[^\d]', '')
    $pb = ($B -replace '[^\d]', '')
    [void][long]::TryParse($pa, [ref]$na)
    [void][long]::TryParse($pb, [ref]$nb)
    if ($na -eq $nb) { return 0 }
    if ($na -gt $nb) { return 1 }
    return -1
}

function Get-CurlExe {
    $candidates = @(
        (Join-Path $env:SystemRoot "System32\curl.exe"),
        (Join-Path $env:SystemRoot "Sysnative\curl.exe")
    )
    foreach ($c in $candidates) {
        if ($c -and (Test-Path $c)) { return $c }
    }
    $cmd = Get-Command curl.exe -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source -and ($cmd.Source -notmatch 'WindowsPowerShell')) { return $cmd.Source }
    return $null
}

function Save-UrlViaCurl([string]$Url, [string]$OutFile, [string]$Token) {
    $curl = Get-CurlExe
    if (-not $curl) { throw "curl.exe not found" }
    $last = "curl failed"
    foreach ($try in 1..4) {
        if (Test-Path $OutFile) { Remove-Item -Force $OutFile -ErrorAction SilentlyContinue }
        $curlArgs = @("-fsSL", "--connect-timeout", "20", "--max-time", "900", "-o", $OutFile)
        if ($Token) { $curlArgs += @("-H", ("PRIVATE-TOKEN: " + $Token)) }
        $curlArgs += $Url
        & $curl @curlArgs
        if (($LASTEXITCODE -eq 0) -and (Test-Path $OutFile) -and ((Get-Item $OutFile).Length -gt 0)) {
            return
        }
        $last = "curl exit " + $LASTEXITCODE
        Start-Sleep -Seconds 1
    }
    throw $last
}

function Save-HttpToFile([string]$Url, [string]$OutFile, [string]$Token) {
    $parent = Split-Path $OutFile -Parent
    if ($parent -and -not (Test-Path $parent)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }
    $curlErr = ""
    try {
        Save-UrlViaCurl $Url $OutFile $Token
        return
    } catch {
        $curlErr = $_.Exception.Message
        Warn ("curl download failed, retry with PowerShell: " + $curlErr)
    }
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    } catch {}
    $headers = New-HttpHeaders $Token
    $last = $curlErr
    foreach ($try in 1..3) {
        try {
            Invoke-WebRequest -Uri $Url -Headers $headers -OutFile $OutFile -UseBasicParsing -TimeoutSec 900
            if ((Test-Path $OutFile) -and ((Get-Item $OutFile).Length -gt 0)) { return }
            $last = "empty download"
        } catch {
            $last = $_.Exception.Message
        }
        Start-Sleep -Seconds 1
    }
    throw ("Download failed: " + $last)
}

function Get-HttpText([string]$Url, [string]$Token) {
    $tmp = Join-Path $env:TEMP ("sat-http-" + [guid]::NewGuid().ToString("N"))
    try {
        Save-HttpToFile $Url $tmp $Token
        return [System.IO.File]::ReadAllText($tmp)
    } finally {
        Remove-Item -Force $tmp -ErrorAction SilentlyContinue
    }
}

function Get-RemoteManifest([string]$Channel, [string]$Token) {
    if (Is-HttpChannel $Channel) {
        $url = Get-ManifestUrl $Channel
        Info ("Fetching manifest: " + $url)
        try {
            $raw = Get-HttpText $url $Token
        } catch {
            throw ("Cannot download latest.json: " + $_.Exception.Message)
        }
        if ($raw.Length -gt 0 -and [int][char]$raw[0] -eq 0xFEFF) {
            $raw = $raw.Substring(1)
        }
        $raw = $raw.TrimStart([char]0xFEFF)
        return ($raw | ConvertFrom-Json)
    }

    if (-not (Test-Path $Channel)) {
        throw ("Update channel not reachable: " + $Channel)
    }
    $manifestPath = Join-Path $Channel "latest.json"
    if (-not (Test-Path $manifestPath)) {
        throw ("latest.json missing in channel: " + $Channel)
    }
    $raw = Get-Content -Path $manifestPath -Raw -Encoding UTF8
    if ($raw.Length -gt 0 -and [int][char]$raw[0] -eq 0xFEFF) {
        $raw = $raw.Substring(1)
    }
    return ($raw | ConvertFrom-Json)
}

function Resolve-ZipSource([string]$Channel, $Manifest) {
    $zipName = [string]$Manifest.zip_name
    $zipUrl = [string]$Manifest.zip_url
    if ($zipUrl) {
        return @{ Mode = "http"; Uri = $zipUrl; Name = $(if ($zipName) { $zipName } else { [IO.Path]::GetFileName(($zipUrl -split '\?')[0]) }) }
    }
    if (-not $zipName) {
        throw "latest.json missing zip_name/zip_url"
    }
    if (Is-HttpChannel $Channel) {
        # Prefer zip_base_url from manifest (package version folder for the build)
        $base = [string]$Manifest.zip_base_url
        if (-not $base) {
            # Same directory as latest.json
            $murl = Get-ManifestUrl $Channel
            $base = $murl.Substring(0, $murl.LastIndexOf('/'))
        }
        $base = $base.TrimEnd('/')
        return @{ Mode = "http"; Uri = ($base + "/" + $zipName); Name = $zipName }
    }
    $path = Join-Path $Channel $zipName
    return @{ Mode = "file"; Path = $path; Name = $zipName }
}

function Get-LocalSha256([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) { return "" }
    try {
        return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
    } catch {
        return ""
    }
}

function Resolve-FilesManifestSource([string]$Channel, $Manifest) {
    $filesUrl = [string]$Manifest.files_url
    $filesName = [string]$Manifest.files_name
    if (-not $filesName) { $filesName = "files-latest.json" }
    if (Is-HttpChannel $Channel) {
        if ($filesUrl) {
            return @{ Mode = "http"; Uri = $filesUrl }
        }
        $base = [string]$Manifest.zip_base_url
        if (-not $base) {
            $murl = Get-ManifestUrl $Channel
            $base = $murl.Substring(0, $murl.LastIndexOf('/'))
        }
        return @{ Mode = "http"; Uri = ($base.TrimEnd('/') + "/" + $filesName) }
    }
    $path = Join-Path $Channel $filesName
    if (-not (Test-Path $path)) { return $null }
    return @{ Mode = "file"; Path = $path }
}

function Get-BlobsBase([string]$Channel, $Manifest) {
    $blobs = [string]$Manifest.blobs_base_url
    if ($blobs) { return $blobs.TrimEnd('/') }
    if (Is-HttpChannel $Channel) {
        $base = [string]$Manifest.zip_base_url
        if (-not $base) {
            $murl = Get-ManifestUrl $Channel
            $base = $murl.Substring(0, $murl.LastIndexOf('/'))
        }
        return ($base.TrimEnd('/') + "/blobs")
    }
    return (Join-Path $Channel "blobs")
}

function Test-ShouldPreserveInstallPath([string]$RelPath) {
    $n = ($RelPath -replace '\\', '/').TrimStart('/').ToLowerInvariant()
    $preserve = @(
        'config/solar_agent.json',
        'config/solar_machine_id',
        'config_files/paths.ini',
        'runtime_root.txt',
        'status.json'
    )
    return ($preserve -contains $n)
}

function Invoke-IncrementalUpdate {
    param(
        [string]$InstallDir,
        [string]$Channel,
        $Manifest,
        [string]$Token,
        [string]$RemoteVer,
        [string]$WorkDir
    )

    $src = Resolve-FilesManifestSource $Channel $Manifest
    if (-not $src) { throw "No files manifest on channel" }

    Set-UpdateUi ("增量更新：读取文件清单 " + $RemoteVer + "...")
    if ($src.Mode -eq "http") {
        $raw = Get-HttpText $src.Uri $Token
    } else {
        $raw = Get-Content -Path $src.Path -Raw -Encoding UTF8
    }
    if ($raw.Length -gt 0 -and [int][char]$raw[0] -eq 0xFEFF) {
        $raw = $raw.Substring(1)
    }
    $filesManifest = $raw | ConvertFrom-Json
    if (-not $filesManifest.files) { throw "files manifest missing files[]" }

    $blobsBase = Get-BlobsBase $Channel $Manifest
    $need = New-Object System.Collections.ArrayList
    $needBytes = [long]0
    foreach ($f in $filesManifest.files) {
        $rel = [string]$f.path
        if (-not $rel) { continue }
        if (Test-ShouldPreserveInstallPath $rel) { continue }
        $sha = ([string]$f.sha256).ToLowerInvariant()
        $size = [long]$f.size
        $localPath = Join-Path $InstallDir ($rel -replace '/', '\')
        $localSha = Get-LocalSha256 $localPath
        if ($localSha -and ($localSha -eq $sha)) { continue }
        [void]$need.Add(@{ path = $rel; sha256 = $sha; size = $size })
        $needBytes += $size
    }

    $zipMb = 0.0
    try { $zipMb = [double]$Manifest.size_mb } catch { $zipMb = 0.0 }
    $needMb = [math]::Round($needBytes / 1MB, 1)
    Info ("Incremental: {0} files / {1} MB to download (full zip ~{2} MB)" -f $need.Count, $needMb, $zipMb)

    # If almost everything changed, full zip is simpler / similar cost
    if ($zipMb -gt 5 -and $needMb -ge ($zipMb * 0.85)) {
        throw ("Incremental not worth it ({0} MB ~= full zip); use zip" -f $needMb)
    }

    if ($need.Count -eq 0) {
        Set-UpdateUi "文件已齐，仅刷新版本号..."
        $verText = @($RemoteVer, ("built=" + (Get-Date -Format "yyyy-MM-dd HH:mm:ss")), "source=incremental-noop") -join "`r`n"
        Set-Content -Path (Join-Path $InstallDir "VERSION") -Value $verText -Encoding UTF8
        return
    }

    $dlDir = Join-Path $WorkDir "blobs"
    New-Item -ItemType Directory -Force -Path $dlDir | Out-Null
    $doneBytes = 0L
    $i = 0
    foreach ($f in $need) {
        $i++
        $sha = [string]$f.sha256
        $rel = [string]$f.path
        $tmp = Join-Path $dlDir $sha
        Set-UpdateProgress ([int][Math]::Min(95, [Math]::Floor(($doneBytes / [Math]::Max(1, $needBytes)) * 100))) `
            ("增量下载 $i/$($need.Count)  $($rel)  $([math]::Round($doneBytes/1MB,1))/$needMb MB")

        if (Is-HttpChannel $Channel) {
            $uri = $blobsBase.TrimEnd('/') + "/" + $sha
            Save-HttpToFile $uri $tmp $Token
        } else {
            $srcBlob = Join-Path $blobsBase $sha
            if (-not (Test-Path $srcBlob)) { throw ("Blob missing: " + $srcBlob) }
            Copy-Item -Force $srcBlob $tmp
        }
        $got = Get-LocalSha256 $tmp
        if ($got -ne $sha) {
            throw ("Blob hash mismatch for " + $rel + " expected=" + $sha + " got=" + $got)
        }
        $doneBytes += [int64]$f.size
    }

    Set-UpdateUi "正在写入本机文件..."
    $lockChanged = $false
    $oldLock = Get-LocalSha256 (Join-Path $InstallDir "uv.lock")
    foreach ($f in $need) {
        $rel = [string]$f.path
        $sha = [string]$f.sha256
        $dest = Join-Path $InstallDir ($rel -replace '/', '\')
        $parent = Split-Path $dest -Parent
        if ($parent -and -not (Test-Path $parent)) {
            New-Item -ItemType Directory -Force -Path $parent | Out-Null
        }
        Copy-Item -Force (Join-Path $dlDir $sha) $dest
        if ($rel -replace '\\', '/' -eq 'uv.lock') { $lockChanged = $true }
    }

    # Keep formal IOT bootstrap in sync when example shipped
    $bootExample = Join-Path $InstallDir "config\iot_bootstrap.example.json"
    $bootPath = Join-Path $InstallDir "config\iot_bootstrap.json"
    if (Test-Path $bootExample) {
        Copy-Item -Force $bootExample $bootPath
    }

    $verText = @($RemoteVer, ("built=" + (Get-Date -Format "yyyy-MM-dd HH:mm:ss")), "source=incremental") -join "`r`n"
    Set-Content -Path (Join-Path $InstallDir "VERSION") -Value $verText -Encoding UTF8

    $newLock = Get-LocalSha256 (Join-Path $InstallDir "uv.lock")
    if ($lockChanged -or ($oldLock -and $newLock -and ($oldLock -ne $newLock))) {
        $uv = Join-Path $InstallDir "tools\uv.exe"
        if (-not (Test-Path $uv)) {
            $cmd = Get-Command uv.exe -ErrorAction SilentlyContinue
            if ($cmd) { $uv = $cmd.Source }
        }
        if (Test-Path $uv) {
            Set-UpdateUi "依赖有变，正在 uv sync ..."
            Info "uv.lock changed; running uv sync --frozen"
            $runtimeRoot = ""
            $rr = Join-Path $InstallDir "runtime_root.txt"
            if (Test-Path $rr) {
                try { $runtimeRoot = ((Get-Content $rr -TotalCount 1) + "").Trim() } catch {}
            }
            if (-not $runtimeRoot) {
                $runtimeRoot = Join-Path $env:LOCALAPPDATA "SolarAutoTestRuntime"
            }
            $env:UV_PROJECT_ENVIRONMENT = Join-Path $runtimeRoot ".venv"
            $env:UV_PYTHON_INSTALL_DIR = Join-Path $runtimeRoot "python"
            $env:UV_CACHE_DIR = Join-Path $runtimeRoot "uv-cache"
            Push-Location $InstallDir
            try {
                & $uv sync --frozen
                if ($LASTEXITCODE -ne 0) {
                    & $uv sync
                }
            } finally {
                Pop-Location
            }
        } else {
            Warn "uv.lock changed but uv.exe missing; launch may sync on next start"
        }
    }

    Set-UpdateProgress 100 ("增量升级完成 " + $needMb + " MB / " + $need.Count + " 个文件")
}

function Get-ZipToTemp($Source, [string]$Token, [string]$WorkDir) {
    $localZip = Join-Path $WorkDir $Source.Name
    if ($Source.Mode -eq "file") {
        if (-not (Test-Path $Source.Path)) {
            throw ("Zip not found: " + $Source.Path)
        }
        Info ("Copying package (" + $Source.Name + ") ...")
        Set-UpdateUi ("正在复制安装包 " + $Source.Name + "...")
        Copy-Item -Force $Source.Path $localZip
        return $localZip
    }
    Info ("Downloading package (" + $Source.Name + ") ...")
    Info ("  " + $Source.Uri)
    Set-UpdateProgress 0 ("正在下载 " + $Source.Name + " 0%")

    $curl = Get-CurlExe
    if ($curl) {
        if (Test-Path $localZip) { Remove-Item -Force $localZip -ErrorAction SilentlyContinue }
        $curlArgs = @("-fsSL", "--connect-timeout", "20", "--max-time", "900", "-o", $localZip, $Source.Uri)
        $proc = Start-Process -FilePath $curl -ArgumentList $curlArgs -PassThru -WindowStyle Hidden
        $lastMb = -1.0
        while (-not $proc.HasExited) {
            $mb = 0.0
            if (Test-Path $localZip) {
                try { $mb = [Math]::Round(((Get-Item $localZip).Length) / 1MB, 1) } catch { $mb = 0.0 }
            }
            if ($mb -ne $lastMb) {
                $lastMb = $mb
                $soft = [int][Math]::Min(95, [Math]::Floor(($mb / 160.0) * 100))
                Set-UpdateProgress $soft ("正在下载 " + $Source.Name + "  " + $mb + " MB (请勿关闭)")
            } else {
                Pump-UpdateUi
            }
            Start-Sleep -Milliseconds 250
        }
        if (($proc.ExitCode -eq 0) -and (Test-Path $localZip) -and ((Get-Item $localZip).Length -gt 1000)) {
            Set-UpdateProgress 100 ("下载完成 " + [Math]::Round(((Get-Item $localZip).Length) / 1MB, 1) + " MB")
            return $localZip
        }
        Warn ("curl zip download failed, exit " + $proc.ExitCode)
    }

    # Background download so the progress window keeps painting (IWR blocks UI thread).
    $job = Start-Job -ScriptBlock {
        param($Uri, $OutFile, $Token)
        $ProgressPreference = "SilentlyContinue"
        try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch {}
        $hdr = @{
            "Accept" = "application/json, application/octet-stream, */*"
        }
        if ($Token) {
            $hdr["PRIVATE-TOKEN"] = [string]$Token
        }
        Invoke-WebRequest -Uri $Uri -Headers $hdr -OutFile $OutFile -UseBasicParsing -TimeoutSec 900
        if (-not (Test-Path $OutFile) -or ((Get-Item $OutFile).Length -lt 1000)) {
            throw "Downloaded zip looks empty/invalid"
        }
    } -ArgumentList @($Source.Uri, $localZip, $Token)

    $lastMb = -1.0
    while ($true) {
        $state = $job.State
        if ($state -eq "Completed" -or $state -eq "Failed" -or $state -eq "Stopped") {
            break
        }
        $mb = 0.0
        if (Test-Path $localZip) {
            try { $mb = [Math]::Round(((Get-Item $localZip).Length) / 1MB, 1) } catch { $mb = 0.0 }
        }
        if ($mb -ne $lastMb) {
            $lastMb = $mb
            # OSS zip is ~160MB; show soft percent capped at 95 until job finishes
            $soft = [int][Math]::Min(95, [Math]::Floor(($mb / 160.0) * 100))
            Set-UpdateProgress $soft ("正在下载 " + $Source.Name + "  " + $mb + " MB (请勿关闭)")
        } else {
            Pump-UpdateUi
        }
        Start-Sleep -Milliseconds 250
    }

    try {
        Receive-Job -Job $job -ErrorAction Stop | Out-Null
    } catch {
        Remove-Job -Job $job -Force -ErrorAction SilentlyContinue
        throw ("Download failed: " + $_.Exception.Message)
    } finally {
        Remove-Job -Job $job -Force -ErrorAction SilentlyContinue
    }

    if (-not (Test-Path $localZip) -or ((Get-Item $localZip).Length -lt 1000)) {
        throw "Downloaded zip looks empty/invalid"
    }
    Set-UpdateProgress 100 ("下载完成 " + [Math]::Round(((Get-Item $localZip).Length) / 1MB, 1) + " MB")
    return $localZip
}

if (-not $InstallDir) {
    $InstallDir = $PSScriptRoot
}
$InstallDir = [System.IO.Path]::GetFullPath($InstallDir)

if (-not (Is-UpdateEnabled $InstallDir)) {
    Info "Update check disabled."
    exit 0
}

$channel = Resolve-Channel $InstallDir
if (-not $channel) {
    Info "No update channel configured; skip."
    exit 0
}
if ($channel -match 'YOUR-SERVER|CHANGE_ME|example\.com|YOUR-GITLAB') {
    Info "Update channel is placeholder; skip."
    exit 0
}

$token = Resolve-UpdateToken $InstallDir

try {
    Set-UpdateUi "正在检查更新，请稍候..."
    $manifest = Get-RemoteManifest $channel $token
} catch {
    Close-UpdateUi
    Warn $_.Exception.Message
    exit 0
}

$remoteVer = [string]$manifest.version
if (-not $remoteVer) {
    Close-UpdateUi
    Warn "latest.json missing version"
    exit 0
}

$localVer = Read-LocalVersion $InstallDir
if (-not $localVer) { $localVer = "0" }

if ((Compare-VersionTag $remoteVer $localVer) -le 0) {
    Set-UpdateUi ("已是最新版 " + $localVer + "，正在打开软件...")
    Start-Sleep -Milliseconds 600
    Close-UpdateUi
    Info ("Up to date. local=" + $localVer + " remote=" + $remoteVer)
    exit 0
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ("  New version available: " + $localVer + "  ->  " + $remoteVer) -ForegroundColor Cyan
Write-Host ("  Channel: " + $channel) -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Set-UpdateUi ("发现新版本 " + $localVer + " -> " + $remoteVer + "，准备升级...")

$doInstall = Is-AutoInstall $InstallDir
if (-not $doInstall) {
    Close-UpdateUi
    $ans = Read-Host "Upgrade now? [Y/n]"
    if ($ans -and $ans.Trim().ToLowerInvariant().StartsWith("n")) {
        Info "Skipped upgrade."
        exit 0
    }
    Ensure-UpdateUi
}

$work = Join-Path $env:TEMP ("SolarAutoTest-update-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $work -Force | Out-Null

try {
    $usedIncremental = $false
    $canIncremental = (
        (Test-Path (Join-Path $InstallDir "SCPITestWave.py")) -and
        (
            ([string]$manifest.files_url) -or
            ([string]$manifest.files_name) -or
            (([string]$manifest.update_mode) -eq "incremental")
        )
    )

    if ($canIncremental) {
        try {
            Set-UpdateUi ("发现新版本 " + $localVer + " -> " + $remoteVer + "，增量更新中...")
            Invoke-IncrementalUpdate -InstallDir $InstallDir -Channel $channel -Manifest $manifest `
                -Token $token -RemoteVer $remoteVer -WorkDir $work
            $usedIncremental = $true
            Set-UpdateUi ("增量升级完成 " + $remoteVer + "，即将重新启动软件...")
            Ok ("Upgraded to " + $remoteVer + " (incremental)")
            Start-Sleep -Milliseconds 800
            Close-UpdateUi
            exit 10
        } catch {
            Warn ("Incremental update failed, falling back to full zip: " + $_.Exception.Message)
            Set-UpdateUi "增量失败，改为全量下载安装包..."
        }
    }

    $src = Resolve-ZipSource $channel $manifest
    Set-UpdateUi ("正在下载新版本 " + $remoteVer + "...（窗口勿关）")
    $localZip = Get-ZipToTemp $src $token $work

    Set-UpdateUi "正在解压安装包..."
    Info "Extracting ..."
    Expand-Archive -Path $localZip -DestinationPath $work -Force

    $setupRoot = $work
    $installPs1 = Join-Path $setupRoot "Install-SolarAutoTest.ps1"
    if (-not (Test-Path $installPs1)) {
        $hit = Get-ChildItem $work -Filter "Install-SolarAutoTest.ps1" -Recurse -ErrorAction SilentlyContinue |
            Select-Object -First 1
        if ($hit) {
            $setupRoot = $hit.Directory.FullName
            $installPs1 = $hit.FullName
        }
    }
    if (-not (Test-Path $installPs1)) {
        throw "Install-SolarAutoTest.ps1 not found inside zip"
    }

    Set-UpdateUi ("正在安装到本机...  " + $InstallDir)
    Info ("Installing into " + $InstallDir + " ...")
    $args = @(
        "-NoProfile", "-ExecutionPolicy", "Bypass",
        "-File", $installPs1,
        "-InstallDir", $InstallDir,
        "-Quiet",
        "-SkipVerify"
    )
    # Do not -Wait on UI thread; pump the progress window while installer runs.
    $p = Start-Process -FilePath "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" `
        -ArgumentList $args -PassThru -NoNewWindow
    while (-not $p.HasExited) {
        Pump-UpdateUi
        Start-Sleep -Milliseconds 120
    }
    if ($p.ExitCode -ne 0) {
        throw ("Installer exit code " + $p.ExitCode)
    }

    Set-UpdateUi ("升级完成 " + $remoteVer + "，即将重新启动软件...")
    Ok ("Upgraded to " + $remoteVer + $(if ($usedIncremental) { " (incremental)" } else { " (full zip)" }))
    Start-Sleep -Milliseconds 800
    Close-UpdateUi
    # 10 = 已升级；父级 Start-SolarAutoTest.bat 必须重启自身，
    # 否则 cmd 按行号继续读已被重写的 bat，会错位（出现 'OOT'、LOCAL_ROOT 丢失）。
    exit 10
}
catch {
    Close-UpdateUi
    Warn ("Upgrade failed: " + $_.Exception.Message)
    if (Is-HttpChannel $channel -and -not $token) {
        Warn "If the project is private, enable Package Registry public pull in GitLab,"
        Warn "or set [update] token= (Deploy Token read_package_registry) on this PC."
    }
    exit 1
}
finally {
    try { Remove-Item -Recurse -Force $work -ErrorAction SilentlyContinue } catch {}
}
