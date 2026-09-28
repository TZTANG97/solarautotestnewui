# -*- coding: utf-8 -*-
"""本机数据/运行时根目录解析。

优先级（高→低）：
1. 环境变量 SOLARAUTOTEST_DATA / SOLARAUTOTEST_RUNTIME
2. 安装目录下 config_files/paths.ini（安装时可选手动路径）
3. config_files/config.ini [PATH] data_root / runtime_root
4. 兼容默认：%LOCALAPPDATA%\\SolarAutoTest 与 %LOCALAPPDATA%\\SolarAutoTestRuntime
"""
from __future__ import annotations

import configparser
import os
from pathlib import Path
from typing import Optional

_CACHE_DATA: Optional[str] = None
_CACHE_RUNTIME: Optional[str] = None


def clear_path_cache() -> None:
    global _CACHE_DATA, _CACHE_RUNTIME
    _CACHE_DATA = None
    _CACHE_RUNTIME = None


def _repo_or_install_root() -> Path:
    """安装目录或开发仓库根（含 SCPITestWave.py / config_files）。"""
    override = (os.environ.get("SOLARAUTOTEST_HOME") or "").strip()
    if override:
        return Path(override).expanduser().resolve()
    here = Path(__file__).resolve()
    # utils/app_paths.py → 仓库根
    root = here.parents[1]
    if (root / "SCPITestWave.py").is_file() or (root / "config_files").is_dir():
        return root
    return Path.cwd()


def _expand(raw: str) -> str:
    text = (raw or "").strip().strip('"')
    if not text:
        return ""
    try:
        text = os.path.expandvars(text)
    except Exception:
        pass
    return str(Path(text).expanduser())


def _read_ini_value(path: Path, section: str, key: str) -> str:
    if not path.is_file():
        return ""
    cfg = configparser.ConfigParser(interpolation=None)
    try:
        cfg.read(str(path), encoding="utf-8")
    except Exception:
        try:
            cfg.read(str(path), encoding="gbk")
        except Exception:
            return ""
    if not cfg.has_section(section):
        return ""
    return str(cfg.get(section, key, fallback="") or "").strip()


def _default_local_base() -> Path:
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("USERPROFILE") or str(Path.home())
    return Path(base)


def data_root(*, force_reload: bool = False) -> str:
    """配置 / 预设 / 试验落盘等用户数据根目录。"""
    global _CACHE_DATA
    if _CACHE_DATA and not force_reload:
        return _CACHE_DATA

    env = _expand(os.environ.get("SOLARAUTOTEST_DATA") or "")
    if env:
        p = Path(env)
        p.mkdir(parents=True, exist_ok=True)
        _CACHE_DATA = str(p.resolve())
        return _CACHE_DATA

    root = _repo_or_install_root()
    for rel, section, key in (
        ("config_files/paths.ini", "paths", "data_root"),
        ("config_files/config.ini", "PATH", "data_root"),
    ):
        raw = _read_ini_value(root / rel, section, key)
        expanded = _expand(raw)
        if expanded and expanded.lower() not in {"auto", "default", "~"}:
            p = Path(expanded)
            try:
                p.mkdir(parents=True, exist_ok=True)
                _CACHE_DATA = str(p.resolve())
                return _CACHE_DATA
            except Exception:
                pass

    p = _default_local_base() / "SolarAutoTest"
    p.mkdir(parents=True, exist_ok=True)
    _CACHE_DATA = str(p.resolve())
    return _CACHE_DATA


def runtime_root(*, force_reload: bool = False) -> str:
    """Python venv / uv cache 根目录（体积大，宜放非系统盘）。"""
    global _CACHE_RUNTIME
    if _CACHE_RUNTIME and not force_reload:
        return _CACHE_RUNTIME

    env = _expand(os.environ.get("SOLARAUTOTEST_RUNTIME") or "")
    if env:
        p = Path(env)
        p.mkdir(parents=True, exist_ok=True)
        _CACHE_RUNTIME = str(p.resolve())
        return _CACHE_RUNTIME

    root = _repo_or_install_root()
    # 安装器写入的纯文本，bat 也读它
    txt = root / "runtime_root.txt"
    if txt.is_file():
        try:
            raw = txt.read_text(encoding="utf-8").strip().splitlines()[0].strip()
        except Exception:
            raw = ""
        expanded = _expand(raw)
        if expanded:
            p = Path(expanded)
            try:
                p.mkdir(parents=True, exist_ok=True)
                _CACHE_RUNTIME = str(p.resolve())
                return _CACHE_RUNTIME
            except Exception:
                pass

    for rel, section, key in (
        ("config_files/paths.ini", "paths", "runtime_root"),
        ("config_files/config.ini", "PATH", "runtime_root"),
    ):
        raw = _read_ini_value(root / rel, section, key)
        expanded = _expand(raw)
        if expanded and expanded.lower() not in {"auto", "default", "~"}:
            p = Path(expanded)
            try:
                p.mkdir(parents=True, exist_ok=True)
                _CACHE_RUNTIME = str(p.resolve())
                return _CACHE_RUNTIME
            except Exception:
                pass

    p = _default_local_base() / "SolarAutoTestRuntime"
    p.mkdir(parents=True, exist_ok=True)
    _CACHE_RUNTIME = str(p.resolve())
    return _CACHE_RUNTIME


def data_subdir(*parts: str, ensure: bool = True) -> str:
    path = Path(data_root())
    for part in parts:
        if part:
            path = path / str(part)
    if ensure:
        path.mkdir(parents=True, exist_ok=True)
    return str(path.resolve())
