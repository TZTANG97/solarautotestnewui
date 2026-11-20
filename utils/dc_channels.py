# -*- coding: utf-8 -*-
"""逻辑直流路数。默认 DC1～DC4，台架上再加的路写在 dc_channels.json，不在代码里写死。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

_DEFAULT = (1, 2, 3, 4)
_CONFIG = Path(__file__).resolve().parents[1] / "dc_channels.json"


def config_path() -> Path:
    return _CONFIG


def _positive_ints(raw: Iterable) -> List[int]:
    out: List[int] = []
    for item in raw:
        try:
            n = int(item)
        except (TypeError, ValueError):
            continue
        if n > 0 and n not in out:
            out.append(n)
    return out


def channel_numbers() -> List[int]:
    """已配置的直流路号。始终保留 1～4，文件里多出来的路按号追加。"""
    extra: List[int] = []
    path = config_path()
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
        if isinstance(data, dict):
            extra = _positive_ints(data.get("channels") or [])
        elif isinstance(data, list):
            extra = _positive_ints(data)
    nums = list(_DEFAULT)
    for n in extra:
        if n not in nums:
            nums.append(n)
    return nums


def add_channel() -> int:
    """追加下一路（当前最大号 + 1），并写回配置。"""
    nums = channel_numbers()
    nxt = max(nums) + 1
    payload = {"channels": nums + [nxt]}
    config_path().write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return nxt


def remove_channel(channel: int) -> List[int]:
    """删掉第 5 路及以后的某一路。1～4 固定保留。返回删后路号列表。"""
    n = int(channel)
    if n <= 4:
        raise ValueError("直流电源1～4不能删除")
    nums = [x for x in channel_numbers() if x != n]
    # 只把额外路写进文件；1～4 始终存在
    extra = [x for x in nums if x > 4]
    payload = {"channels": list(range(1, 5)) + extra}
    config_path().write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return channel_numbers()


def dc_token(channel: int) -> str:
    return "DC%d" % int(channel)


def parse_dc_token(token) -> int:
    """'DC5' / 'dc5' → 5。不是直流令牌时返回 0。"""
    text = str(token or "").strip().upper()
    if not text.startswith("DC"):
        return 0
    tail = text[2:]
    if not tail.isdigit():
        return 0
    n = int(tail)
    return n if n > 0 else 0


def s1_dc_slots(ui):
    """界面上实际有的直流路 (路号, 设备名, 0 基下标, 标签)。没有控件的路跳过。"""
    out = []
    for ch in channel_numbers():
        cb = getattr(ui, "checkBox_S1_DC%d" % ch, None)
        if cb is None:
            continue
        out.append((ch, "DC%d" % ch, ch - 1, "DC电源%d" % ch))
    return out


def extra_setting_names() -> List[str]:
    """第 5 路起的设定控件名。接在原表头后面，不插进 DC1～DC4 已有列。"""
    names: List[str] = []
    for n in channel_numbers():
        if n <= 4:
            continue
        names.extend(
            [
                "checkBox_S1_DC%d" % n,
                "comboBox_S1_DC%d" % n,
                "textEdit_S1_DC%d_VOLT" % n,
                "textEdit_S1_DC%d_CURR" % n,
                "textEdit_S1_DC%d_Voc" % n,
                "textEdit_S1_DC%d_Isc" % n,
                "textEdit_S1_DC%d_PF" % n,
                "checkBox_S3_DC%d" % n,
                "checkBox_S_End_DC%d" % n,
                "comboBox_S_End_DC%d" % n,
                "checkBox_S_END_DC%d" % n,
                "comboBox_S_END_DC%d" % n,
            ]
        )
    return names


def extend_setting_headers(headers: Iterable[str]) -> List[str]:
    out = [str(name) for name in headers]
    have = set(out)
    for name in extra_setting_names():
        if name not in have:
            out.append(name)
            have.add(name)
    return out


def ensure_slot(values: list, index: int, fill):
    """把列表扩到能放下 index。就地修改并返回原列表。"""
    while len(values) <= int(index):
        values.append(fill)
    return values
