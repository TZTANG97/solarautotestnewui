# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(r"E:\solarautotestnewui\packaging\Build-ReleasePackage.ps1")
text = p.read_text(encoding="utf-8-sig")

inject = """$ErrorActionPreference = \"Stop\"
# UTF-8 console so Chinese prints correctly under Windows PowerShell 5.1
try {
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [Console]::OutputEncoding
    if ($Host.Name -eq 'ConsoleHost') {
        try { chcp 65001 | Out-Null } catch {}
    }
} catch {}
"""

if "UTF8Encoding" not in text:
    old = '$ErrorActionPreference = "Stop"'
    if old not in text:
        raise SystemExit("anchor not found")
    text = text.replace(old, inject, 1)

# UTF-8 with BOM — required for Windows PowerShell 5.1 to parse Chinese in .ps1
p.write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))
print("OK", p)
print("BOM", list(p.read_bytes()[:3]))
for ln in text.splitlines():
    if "发布" in ln or "发给" in ln or "文件夹" in ln:
        print(ln)
