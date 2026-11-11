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


def oxygen_store_scpi_path(path: str) -> str:
    """文档示例用正斜杠绝对路径：``D:/DATA/Testrun_1``。"""
    cleaned = (path or "").strip().strip('"').replace("\\", "/")
    if cleaned.lower().endswith(".dmd"):
        cleaned = cleaned[:-4]
    return cleaned


def oxygen_store_path_candidates(save_path: str, *, stamp: Optional[str] = None) -> List[str]:
    """
    生成 :STORE:FILE:NAME 候选（优先级从高到低）：

    1) CSV 同目录绝对路径（用户保存目录，正斜杠）——与官方 ``D:/DATA/Testrun_1`` 一致
    2) 台架盘符短路径 D:/E:
    3) 仅文件名（Oxygen 默认 data 目录）——兜底，不再优先（避免落到未知默认目录）
    """
    stamp = stamp or time.strftime("%Y%m%d_%H%M%S")
    primary = build_oxygen_store_path(save_path, stamp=stamp)
    stem = os.path.splitext(os.path.basename(primary))[0] or f"dewetron_{stamp}"
    simple_name = stem[:80]
    candidates: List[str] = [oxygen_store_scpi_path(primary)]
    for root in (r"D:\SolarAutoTest_Dew", r"E:\SolarAutoTest_Dew", r"D:\dxl"):
        try:
            os.makedirs(root, exist_ok=True)
            candidates.append(
                oxygen_store_scpi_path(os.path.abspath(os.path.join(root, stem)))
            )
        except OSError:
            continue
    candidates.append(simple_name)
    # 去重保序
    out: List[str] = []
    seen = set()
    for c in candidates:
        key = c.replace("\\", "/").casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(c)
    return out


def scpi_store_file_name(path: str) -> str:
    """生成 :STORE:FILE:NAME 命令（正斜杠绝对路径，与官方示例一致）。"""
    cleaned = oxygen_store_scpi_path(path)
    return f':STORE:FILE:NAME "{cleaned}"'


def format_abs_time_for_csv(raw: Optional[str]) -> str:
    """把 Oxygen ABS-TIME 规范成 Excel 友好绝对时间。

    官方示例：``2017-08-28T13:17:26.9715+00:00``
    导出目标：``2025/12/17 16:58:07.971``（去 T、去时区偏移；保留小数秒）
    """
    text = str(raw or "").strip().strip('"').strip("'")
    if not text:
        return ""
    # 去掉 SCPI 偶发前缀
    text = re.sub(r"^:[^\s,]+\s*", "", text).strip()
    # 去掉末尾时区 +08:00 / Z
    text = re.sub(r"(Z|[+-]\d{2}:?\d{2})$", "", text, flags=re.IGNORECASE).strip()
    text = text.replace("T", " ").replace("-", "/")
    # 压缩多余空白
    text = re.sub(r"\s+", " ", text).strip()
    return text


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
    """Started / Armed / Paused 视为录波已武装或进行中。

    ``Stopping`` 不算成功：上一轮 STOP 尚未结束时不能当成本次已开录。
    """
    s = (state or "").strip().casefold()
    return s in {"started", "armed", "paused"}


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


def resolve_oxygen_dmd_path(store_path: str) -> Optional[str]:
    """根据 :STORE:FILE:NAME 结果定位本地 .dmd（可带或不带后缀）。"""
    text = (store_path or "").strip().strip('"').replace("/", "\\")
    if not text or text.upper() == "NONE":
        return None
    candidates = []
    if text.lower().endswith(".dmd"):
        candidates.append(text)
    else:
        candidates.append(text + ".dmd")
        candidates.append(text)
    for path in candidates:
        if os.path.isfile(path):
            return path
    # Oxygen 有时只回文件名：在常见目录里找
    name = os.path.basename(text)
    if not name.lower().endswith(".dmd"):
        name = name + ".dmd"
    search_roots = [
        os.path.dirname(text),
        r"D:\SolarAutoTest_Dew",
        r"E:\SolarAutoTest_Dew",
        r"D:\dxl",
    ]
    try:
        from utils.wt_save_path import default_dewetron_save_dir, ensure_dewetron_save_dir

        search_roots.extend(
            [ensure_dewetron_save_dir(), default_dewetron_save_dir()]
        )
    except Exception:
        pass
    for root in search_roots:
        if not root:
            continue
        cand = os.path.join(root, name)
        if os.path.isfile(cand):
            return cand
    return candidates[0] if candidates else None


def preserve_oxygen_dmd_beside_csv(
    store_path: str,
    csv_path: str,
) -> Tuple[bool, str]:
    """把 Oxygen .dmd 保留到 CSV 同目录；已在目标处则直接返回成功。

    返回 ``(ok, message)``。
    """
    import shutil

    src = resolve_oxygen_dmd_path(store_path)
    if not src or not os.path.isfile(src):
        return False, f"未找到 .dmd（STORE 路径={store_path!r}）"
    folder = ""
    if csv_path:
        folder = os.path.dirname(os.path.abspath(csv_path))
    if not folder:
        from utils.wt_save_path import ensure_dewetron_save_dir

        folder = ensure_dewetron_save_dir()
    os.makedirs(folder, exist_ok=True)
    dest = os.path.join(folder, os.path.basename(src))
    try:
        src_abs = os.path.abspath(src)
        dest_abs = os.path.abspath(dest)
        if src_abs.casefold() == dest_abs.casefold():
            return True, dest_abs
        shutil.copy2(src_abs, dest_abs)
        return True, dest_abs
    except OSError as exc:
        return False, f"复制 .dmd 失败: {exc}"
