from __future__ import annotations

import os
from pathlib import Path

from .app_config import config

# WT 可执行文件路径仍从 config.ini 读取（便于不同电脑安装路径不同）
PATH_WT_EXE = config.get('PATH', 'wt_exe')


def _with_trailing_sep(p: str) -> str:
    """确保目录路径以分隔符结尾，便于后续 PATH_RECORDINGS[type] + filename 直接拼接。"""
    if not p:
        return p
    return p if p.endswith(("/", "\\")) else (p + os.sep)


# 录制宏(Recordings)目录：强制使用“当前项目根目录/recordings/”，避免依赖 D:/EnergyTest/... 这类机器相关绝对路径
# 本文件位置：<repo>/config/path_config.py  -> repo_root = parents[1]
# 注意：这里不要用 resolve()，否则在网络映射盘(Z:)场景下可能被展开成 UNC(\\192.168...)
# 我们希望“代码从哪个盘符/路径启动，就用哪个盘符/路径”。
_REPO_ROOT = Path(__file__).parent.parent
_RECORDINGS_ROOT = _REPO_ROOT / "recordings"

PATH_RECORDINGS = {
    "WT3000": _with_trailing_sep(str(_RECORDINGS_ROOT / "WT3000")),
    "WT1800": _with_trailing_sep(str(_RECORDINGS_ROOT / "WT1800")),
    "WT1806E": _with_trailing_sep(str(_RECORDINGS_ROOT / "WT1806E")),
    "WT5000": _with_trailing_sep(str(_RECORDINGS_ROOT / "WT5000")),
}
