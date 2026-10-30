# -*- coding: utf-8 -*-
"""德威创模拟通道比例系数。

设备配置里对应属性 Neon/PhysicalScaleFactor（DoubleValue）。
界面电流名用 AI 1/l1，XML ShortId 用 AI 1/I1。
"""

from __future__ import annotations

import math
import re

ANALOG_SCALE_CHANNELS = (
    "AI 1/U1",
    "AI 1/U2",
    "AI 1/U3",
    "AI 1/U4",
    "AI 1/l1",
    "AI 1/l2",
    "AI 1/l3",
    "AI 1/l4",
)

_SCALE_RE = re.compile(
    r'(<Property name="Neon/PhysicalScaleFactor">\s*<DoubleValue>)([^<]*)(</DoubleValue>)'
)


def xml_channel_name(name: str) -> str:
    """UI 通道名 → XML ShortId（电流 l → I）。"""
    return str(name or "").strip().replace("/l", "/I")


def ui_channel_name(name: str) -> str:
    """XML ShortId → 设置页通道名。"""
    text = str(name or "").strip()
    if text.startswith("AI ") and "/I" in text:
        return text.replace("/I", "/l")
    return text


def format_physical_scale_factor(value) -> str | None:
    """把界面上的比例系数收成 Oxygen DoubleValue 能接受的十进制。空或非法返回 None。"""
    text = str(value if value is not None else "").strip().replace("，", "")
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    if not math.isfinite(number):
        return None
    rendered = f"{number:.10f}".rstrip("0").rstrip(".")
    if rendered in ("", "-0"):
        return "0"
    return rendered


def _channel_spans(xml: str, short_id: str):
    token = f'ShortId"><StringValue>"{short_id}"'
    start = 0
    closer = "</Channel>"
    while True:
        pos = xml.find(token, start)
        if pos < 0:
            return
        end = xml.find(closer, pos)
        if end < 0:
            return
        yield pos, end
        start = end + len(closer)


def read_physical_scale_factors(xml: str, channels=None) -> dict:
    """从配置 XML 读出各模拟通道当前的比例系数。键用设置页通道名。"""
    names = tuple(channels or ANALOG_SCALE_CHANNELS)
    found = {}
    if not xml:
        return found
    for name in names:
        short_id = xml_channel_name(name)
        for begin, end in _channel_spans(xml, short_id):
            match = _SCALE_RE.search(xml, begin, end)
            if match:
                found[ui_channel_name(name)] = match.group(2).strip()
                break
    return found


def apply_physical_scale_factors(xml: str, scales) -> str:
    """把比例系数写进对应通道的 Neon/PhysicalScaleFactor。未给出或非法的通道保持原值。"""
    if not xml or not isinstance(scales, dict) or not scales:
        return xml
    replacements = []
    for raw_name, raw_value in scales.items():
        formatted = format_physical_scale_factor(raw_value)
        short_id = xml_channel_name(raw_name)
        if not short_id or formatted is None:
            continue
        touched = False
        for begin, end in _channel_spans(xml, short_id):
            match = _SCALE_RE.search(xml, begin, end)
            if not match:
                continue
            touched = True
            if match.group(2) == formatted:
                continue
            replacements.append((match.start(2), match.end(2), formatted, short_id))
        if not touched:
            print(f"[DEWETRON] {short_id}: 未找到 Neon/PhysicalScaleFactor，跳过")
    if not replacements:
        return xml
    replacements.sort(key=lambda item: item[0], reverse=True)
    for start, end, value, short_id in replacements:
        xml = xml[:start] + value + xml[end:]
        print(f"[DEWETRON] {short_id} PhysicalScaleFactor -> {value}")
    return xml
