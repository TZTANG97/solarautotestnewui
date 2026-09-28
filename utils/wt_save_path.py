# -*- coding: utf-8 -*-
"""WT / 试验数据保存目录：默认可用路径 + 自动创建。"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from utils.app_paths import data_subdir


def default_wt_save_path() -> str:
    """本机默认可写目录（不依赖 D:\\EnergyTest）。"""
    return data_subdir("wt_save")


def default_dewetron_save_dir() -> str:
    """德威创 CSV / Oxygen 默认可写目录。"""
    return data_subdir("dewetron_save")


def resolve_config_wt_save_path(raw: Optional[str] = None) -> str:
    """解析 config.ini [PATH] wt_file_save_path；空/auto/非法则回退默认并建目录。"""
    text = "" if raw is None else str(raw).strip().strip('"')
    if not text or text.lower() in {"auto", "default", "~"}:
        return ensure_wt_save_dir(default_wt_save_path())
    try:
        expanded = os.path.expandvars(text)
    except Exception:
        expanded = text
    return ensure_wt_save_dir(expanded)


def ensure_dewetron_save_dir(path: Optional[str] = None) -> str:
    """确保德威创保存目录存在。"""
    raw = (path or "").strip().strip('"')
    if not raw or raw.lower() in {"auto", "default", "~"}:
        return ensure_wt_save_dir(default_dewetron_save_dir())
    return ensure_wt_save_dir(raw)


def ensure_wt_save_dir(path: Optional[str] = None) -> str:
    """确保保存目录存在；失败则回退到默认目录。"""
    candidates = []
    raw = (path or "").strip().strip('"')
    if raw:
        candidates.append(raw)
    candidates.append(default_wt_save_path())
    candidates.append(str(Path.cwd() / "wt_save"))

    last_err: Optional[Exception] = None
    for cand in candidates:
        try:
            pth = Path(cand).expanduser()
            if pth.suffix and not pth.exists():
                if len(pth.suffix) <= 5 and "." in pth.name:
                    pth = pth.parent
            pth.mkdir(parents=True, exist_ok=True)
            if pth.is_dir():
                return str(pth.resolve())
        except Exception as exc:
            last_err = exc
            continue
    fallback = Path.cwd()
    try:
        fallback.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    if last_err:
        print(f"[wt_save] ensure dir fallback={fallback}: {last_err}", flush=True)
    return str(fallback.resolve())
