# -*- coding: utf-8 -*-
"""最近一次德威创导出路径（中途停机 / 结案找 CSV 用）。

内存变量可能因双份 utils 导入对不上；同时写 sidecar，结案从磁盘读。
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Optional, Tuple

_LAST_CSV = ""
_LAST_DIR = ""
_LAST_DMD = ""

_SIDECAR_NAME = ".last_dew_export.json"


def _localappdata_dewetron_save() -> Path:
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("USERPROFILE") or str(Path.home())
    return Path(base) / "SolarAutoTest" / "dewetron_save"


def _sidecar_candidates(csv_path: str = "") -> list:
    """可能写入/读取 sidecar 的位置（去重）。"""
    out: list = []
    seen = set()

    def _add(p: Path) -> None:
        try:
            key = str(p.resolve()).lower()
        except OSError:
            key = str(p).lower()
        if key in seen:
            return
        seen.add(key)
        out.append(p)

    text = str(csv_path or "").strip()
    if text:
        parent = Path(text).parent
        if str(parent):
            _add(parent / _SIDECAR_NAME)
    try:
        from utils.wt_save_path import default_dewetron_save_dir

        _add(Path(default_dewetron_save_dir()) / _SIDECAR_NAME)
    except Exception:
        pass
    _add(_localappdata_dewetron_save() / _SIDECAR_NAME)
    return out


def _write_sidecar(csv_path: str, csv_dir: str, dmd_path: str = "") -> None:
    payload = {
        "csv": str(csv_path or ""),
        "dir": str(csv_dir or ""),
        "dmd": str(dmd_path or _LAST_DMD or ""),
        "ts": time.time(),
    }
    raw = json.dumps(payload, ensure_ascii=False)
    for side in _sidecar_candidates(csv_path):
        try:
            side.parent.mkdir(parents=True, exist_ok=True)
            side.write_text(raw, encoding="utf-8")
        except OSError:
            continue


def remember_dew_export(csv_path: str) -> None:
    global _LAST_CSV, _LAST_DIR

    text = str(csv_path or "").strip()
    _LAST_CSV = text
    _LAST_DIR = os.path.dirname(text) if text else ""
    if text:
        _write_sidecar(text, _LAST_DIR, _LAST_DMD)


def remember_dew_dmd(dmd_path: str) -> None:
    """Oxygen 保留的 .dmd 路径（结案上传用）。"""
    global _LAST_DMD

    text = str(dmd_path or "").strip()
    _LAST_DMD = text
    if _LAST_CSV or text:
        _write_sidecar(_LAST_CSV, _LAST_DIR or (os.path.dirname(text) if text else ""), text)


def last_dew_dmd() -> str:
    mem = str(_LAST_DMD or "").strip()
    if mem:
        return mem
    _csv, _dir, dmd = read_sidecar_full()
    return dmd


def last_dew_csv() -> str:
    mem = str(_LAST_CSV or "").strip()
    if mem:
        return mem
    csv_path, _dir = read_sidecar()
    return csv_path


def last_dew_dir() -> str:
    mem = str(_LAST_DIR or "").strip()
    if mem:
        return mem
    _csv, d = read_sidecar()
    return d


def read_sidecar_full() -> Tuple[str, str, str]:
    """从 sidecar 读最近导出；多候选取 mtime 最新。返回 (csv, dir, dmd)。"""
    best: Optional[Tuple[float, str, str, str]] = None
    for side in _sidecar_candidates():
        try:
            if not side.is_file():
                continue
            mtime = side.stat().st_mtime
            data = json.loads(side.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                continue
            csv_path = str(data.get("csv") or "").strip()
            d = str(data.get("dir") or "").strip()
            dmd = str(data.get("dmd") or "").strip()
            if not d and csv_path:
                d = str(Path(csv_path).parent)
            if not csv_path and not d and not dmd:
                continue
            if best is None or mtime >= best[0]:
                best = (mtime, csv_path, d, dmd)
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            continue
    if best is None:
        return "", "", ""
    return best[1], best[2], best[3]


def read_sidecar() -> Tuple[str, str]:
    """从 sidecar 读最近导出；多候选取 mtime 最新。"""
    csv_path, d, _dmd = read_sidecar_full()
    return csv_path, d


def hard_dewetron_save_dirs() -> list:
    """不依赖 data_root 的本机德威创目录（结案兜底扫描）。"""
    dirs: list = []
    seen = set()

    def _add(raw: str) -> None:
        text = str(raw or "").strip()
        if not text:
            return
        try:
            p = Path(os.path.expandvars(text)).expanduser()
        except Exception:
            p = Path(text)
        try:
            key = str(p.resolve()).lower() if p.exists() else str(p).lower()
        except OSError:
            key = str(p).lower()
        if key in seen:
            return
        seen.add(key)
        dirs.append(p)

    _add(str(_localappdata_dewetron_save()))
    try:
        from utils.wt_save_path import default_dewetron_save_dir

        _add(default_dewetron_save_dir())
    except Exception:
        pass
    # 常见安装/配置覆盖
    for env_k in ("SOLARAUTOTEST_DATA", "SOLARAUTOTEST_HOME"):
        env = str(os.environ.get(env_k) or "").strip()
        if env:
            _add(str(Path(env) / "dewetron_save"))
    return dirs
