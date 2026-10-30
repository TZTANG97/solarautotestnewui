# -*- coding: utf-8 -*-
"""打开软件时检查更新。不依赖快捷方式里的 bat，旧入口直接运行 python 也会走这里。"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

_DEFAULT_CHANNEL = "https://qgongye.oss-cn-shanghai.aliyuncs.com/solarautotest/updates"


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def _digits(text: str) -> int:
    try:
        return int(re.sub(r"\D", "", str(text or "")) or "0")
    except ValueError:
        return 0


def _read_local_version(root: Path) -> str:
    path = root / "VERSION"
    if not path.is_file():
        return ""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    return lines[0].strip() if lines else ""


def _channel(root: Path) -> str:
    ini = root / "config_files" / "config.ini"
    enabled = True
    found = ""
    try:
        text = ini.read_text(encoding="utf-8", errors="replace")
    except OSError:
        text = ""
    in_update = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith(";"):
            continue
        if line.startswith("[") and line.endswith("]"):
            in_update = line[1:-1].strip().lower() == "update"
            continue
        if not in_update or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip().lower()
        val = val.strip()
        if key == "enabled" and val.lower() in ("0", "false", "no", "off"):
            enabled = False
        elif key == "channel" and val:
            found = val
    if not enabled:
        return ""
    return found or _DEFAULT_CHANNEL


def _fetch_remote_version(channel: str) -> str:
    url = channel.rstrip("/")
    if not url.lower().endswith("latest.json"):
        url += "/latest.json"
    curl = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "curl.exe"
    if not curl.is_file():
        return ""
    try:
        proc = subprocess.run(
            [str(curl), "-fsSL", "--connect-timeout", "15", "--max-time", "40", url],
            capture_output=True,
            check=False,
            timeout=50,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    if proc.returncode != 0:
        return ""
    raw = (proc.stdout or b"").decode("utf-8", errors="replace")
    match = re.search(r'"version"\s*:\s*"([^"]+)"', raw)
    return match.group(1).strip() if match else ""


def _restart_self() -> None:
    argv = [sys.executable, *sys.argv]
    env = os.environ.copy()
    env["SOLARAUTOTEST_SKIP_STARTUP_UPDATE"] = "1"
    subprocess.Popen(argv, cwd=str(_root()), env=env)
    raise SystemExit(0)


def maybe_apply_startup_update() -> None:
    if os.environ.get("SOLARAUTOTEST_UPDATE_DISABLE") == "1":
        return
    if os.environ.get("SOLARAUTOTEST_SKIP_STARTUP_UPDATE") == "1":
        return
    root = _root()
    local = _read_local_version(root)
    # 源码目录没有 VERSION，避免把开发仓库覆盖成安装包。
    if not local:
        return
    channel = _channel(root)
    if not channel:
        print("[更新] 已关闭自动更新", flush=True)
        return
    remote = _fetch_remote_version(channel)
    if not remote:
        print("[更新] 暂时连不上更新通道，先打开当前版本 " + local, flush=True)
        return
    if _digits(remote) <= _digits(local):
        print("[更新] 已是最新 " + local, flush=True)
        return
    print("[更新] 发现新版本 %s -> %s，正在升级，请勿关闭" % (local, remote), flush=True)
    ps1 = root / "Check-And-Update.ps1"
    if not ps1.is_file():
        print("[更新] 缺少 Check-And-Update.ps1，无法自动升级", flush=True)
        return
    try:
        proc = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ps1),
                "-InstallDir",
                str(root),
                "-AutoYes",
            ],
            cwd=str(root),
            timeout=900,
        )
        code = int(proc.returncode or 0)
    except (OSError, subprocess.TimeoutExpired) as exc:
        print("[更新] 升级没有完成: %s" % exc, flush=True)
        return
    now = _read_local_version(root)
    if code == 10 or (now and now != local and _digits(now) >= _digits(remote)):
        print("[更新] 已升到 " + (now or remote) + "，正在重新打开", flush=True)
        _restart_self()
        return
    print("[更新] 升级未完成（退出码 %s），仍打开当前版本 %s" % (code, local), flush=True)
