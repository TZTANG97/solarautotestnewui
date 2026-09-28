# -*- coding: utf-8 -*-
"""Oxygen :STORE 录波路径与跳脱操作日志文案。"""

from __future__ import annotations

import os
import re
import time
from typing import List, Optional, Tuple


def build_oxygen_store_path(save_path: str, *, stamp: Optional[str] = None) -> str:
    """
    与 CSV 同目录的 Oxygen 录波基名（.dmd 由设备可自动补）。
    返回 Windows 反斜杠绝对路径（Oxygen 文档示例为 D:\\DATA\\Testrun_1）。
    """
    from utils.wt_save_path import ensure_dewetron_save_dir

    stamp = stamp or time.strftime("%Y%m%d_%H%M%S")
    base = (save_path or "").strip()
    if base:
        folder = os.path.dirname(os.path.abspath(base)) or ensure_dewetron_save_dir()
        stem = os.path.splitext(os.path.basename(base))[0] or "dewetron"
    else:
        folder = ensure_dewetron_save_dir()
        stem = f"dewetron_{stamp}"
    os.makedirs(folder, exist_ok=True)
    return os.path.abspath(os.path.join(folder, f"{stem}_oxygen"))


def oxygen_store_path_candidates(save_path: str, *, stamp: Optional[str] = None) -> List[str]:
    """
    按官方文档优先级生成候选：
    1) 仅文件名（写到 Oxygen 默认目录）——最稳
    2) CSV 同目录绝对路径（反斜杠）
    3) 常见台架盘符 D:/E: 短路径
    """
    stamp = stamp or time.strftime("%Y%m%d_%H%M%S")
    primary = build_oxygen_store_path(save_path, stamp=stamp)
    stem = os.path.splitext(os.path.basename(primary))[0] or f"dewetron_{stamp}"
    # 文档示例：:STORE:FILE:NAME "Testrun_1"
    simple_name = stem[:80]
    candidates: List[str] = [simple_name, primary]
    for root in (r"D:\SolarAutoTest_Dew", r"E:\SolarAutoTest_Dew", r"D:\dxl"):
        try:
            os.makedirs(root, exist_ok=True)
            candidates.append(os.path.abspath(os.path.join(root, stem)))
        except OSError:
            continue
    # 去重保序
    out: List[str] = []
    seen = set()
    for c in candidates:
        key = c.replace("/", "\\").casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(c)
    return out


def scpi_store_file_name(path: str) -> str:
    """生成 :STORE:FILE:NAME 命令（Windows 反斜杠，与官方示例一致）。"""
    cleaned = (path or "").strip().replace("/", "\\")
    return f':STORE:FILE:NAME "{cleaned}"'


def parse_store_file_name_response(raw: Optional[str]) -> Optional[str]:
    """
    解析 :STORE:FILE:NAME?。
    文档：未开始录波时返回 NONE（不代表路径未设置）。
    例: ':STOR:FILE "D:\\DATA\\Testrun_1.dmd"' / ':STOR:FILE NONE'
    """
    text = str(raw or "").strip()
    if not text:
        return None
    # 取最后一个引号串
    quoted = re.findall(r'"([^"]+)"', text)
    if quoted:
        return quoted[-1].strip()
    # 无引号：取最后一个 token
    parts = text.replace("=", " ").split()
    if not parts:
        return None
    token = parts[-1].strip().strip('"')
    if token.upper() == "NONE":
        return None
    if token.upper().startswith(":STOR"):
        return None
    return token


def parse_store_state_response(raw: Optional[str]) -> str:
    """
    解析 :STORE:STATE? → Started|Stopped|Stopping|Paused|Armed|Unknown
    例: ':STOR:STAT Stopped' / 'Started'
    """
    text = str(raw or "").strip()
    if not text:
        return "Unknown"
    low = text.casefold()
    for name in ("stopping", "started", "stopped", "paused", "armed"):
        if re.search(rf"\b{name}\b", low):
            return name[:1].upper() + name[1:]
    # 无词界时：Stopped 优先于含 start 的误判
    if "stopped" in low:
        return "Stopped"
    if "started" in low:
        return "Started"
    if "armed" in low:
        return "Armed"
    if "paused" in low:
        return "Paused"
    return text.split()[-1] if text.split() else "Unknown"


def store_state_is_active(state: str) -> bool:
    """Started / Armed 视为录波已武装或进行中。"""
    s = (state or "").strip().casefold()
    return s in {"started", "armed", "paused", "stopping"}


def scpi_marker_add(
    label: str,
    *,
    description: str = "",
    time_s: Optional[float] = None,
) -> str:
    """
    生成 :MARKER:ADD 命令。

    TIME 为相对录波起点的秒数；省略则钉在当前时刻。
    例: :MARKER:ADD "跳脱","I drop",45.2
    """
    lab = str(label or "标记").replace('"', "'")
    desc = str(description or "").replace('"', "'")
    if time_s is None:
        if desc:
            return f':MARKER:ADD "{lab}","{desc}"'
        return f':MARKER:ADD "{lab}"'
    t = f"{float(time_s):.4f}"
    if desc:
        return f':MARKER:ADD "{lab}","{desc}",{t}'
    return f':MARKER:ADD "{lab}",{t}'


def format_trip_operator_log(
    *,
    wall_clock: str,
    elapsed_s: float,
    reason: str,
    store_path: str = "",
    marker_ok: Optional[bool] = None,
) -> str:
    """操作日志一行：跳脱时刻 + Oxygen 打开提示。"""
    path_hint = (store_path or "").strip()
    marker_hint = ""
    if marker_ok is True:
        marker_hint = "已打标记「跳脱」(钉死)；Oxygen 可拖光标对照查看；"
    elif marker_ok is False:
        marker_hint = "标记写入失败，请按时刻手动拖光标；"
    if path_hint:
        return (
            f"[DEWETRON][跳脱] 时刻 {wall_clock} (录波+{elapsed_s:.1f}s) {reason}；"
            f"{marker_hint}请用 Oxygen 打开录波: {path_hint}"
        )
    return (
        f"[DEWETRON][跳脱] 时刻 {wall_clock} (录波+{elapsed_s:.1f}s) {reason}；"
        f"{marker_hint}请用 Oxygen 打开本段录波，可拖光标查看"
    )


def trip_wall_clock_from_gather_start(
    gather_start_unix: float, elapsed_s: float
) -> Tuple[str, float]:
    """由采集起点 + 相对秒算出墙钟时间字符串。"""
    wall = float(gather_start_unix) + float(elapsed_s)
    return time.strftime("%H:%M:%S", time.localtime(wall)), wall
