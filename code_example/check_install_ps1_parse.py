# -*- coding: utf-8 -*-
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PS1 = ROOT / "packaging" / "Install-SolarAutoTest.ps1"


def main() -> int:
    helper = r"""
param([Parameter(Mandatory=$true)][string]$Path)
$err = $null
$tok = $null
[void][System.Management.Automation.Language.Parser]::ParseFile($Path, [ref]$tok, [ref]$err)
if ($err -and $err.Count -gt 0) {
  foreach ($e in $err) { Write-Output ('PARSE_ERR: ' + $e.ToString()) }
  exit 1
}
Write-Output 'PARSE_OK'
exit 0
"""
    with tempfile.TemporaryDirectory() as td:
        helper_path = Path(td) / "parse_check.ps1"
        helper_path.write_text(helper, encoding="utf-8")
        r = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(helper_path),
                "-Path",
                str(PS1),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    out = (r.stdout or r.stderr or "").strip()
    sys.stdout.buffer.write((out + "\n").encode("utf-8", errors="replace"))
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
