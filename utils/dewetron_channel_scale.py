# -*- coding: utf-8 -*-
"""德威创模拟通道比例系数。

设备配置里对应属性 Neon/PhysicalScaleFactor（DoubleValue）。
界面电流名用 AI 1/l1，XML ShortId 用 AI 1/I1。
"""

from __future__ import annotations

import configparser
import math
import os
import re
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

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


def scale_config_path() -> Path:
    """本机德威创比例系数记忆档（与 WT wt_scale.ini 同级）。"""
    override = (os.environ.get("SOLARAUTOTEST_DEW_SCALE") or "").strip()
    if override:
        return Path(override).expanduser()
    try:
        from utils.app_paths import data_subdir

        return Path(data_subdir("config")) / "dewetron_scale.ini"
    except Exception:
        from utils.app_paths import _repo_or_install_root

        return _repo_or_install_root() / "config_files" / "dewetron_scale.ini"


def load_saved_dew_scales() -> Dict[str, str]:
    """读上次在设置页/开测填写的比例系数。键为 AI 1/U1、AI 1/l1。"""
    path = scale_config_path()
    if not path.is_file():
        return {}
    parser = configparser.ConfigParser()
    try:
        parser.read(str(path), encoding="utf-8")
    except Exception:
        return {}
    if not parser.has_section("DEW_SCALE"):
        return {}
    out: Dict[str, str] = {}
    for name in ANALOG_SCALE_CHANNELS:
        key = name.replace(" ", "_").replace("/", "_")
        if not parser.has_option("DEW_SCALE", key):
            continue
        text = str(parser.get("DEW_SCALE", key) or "").strip()
        if text:
            out[name] = text
    return out


def save_saved_dew_scales(mapping: Optional[Mapping] = None) -> None:
    """把当前比例系数写入本机记忆档，下次打开设置页回填。"""
    path = scale_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    parser = configparser.ConfigParser()
    if path.is_file():
        try:
            parser.read(str(path), encoding="utf-8")
        except Exception:
            parser = configparser.ConfigParser()
    section: Dict[str, str] = {}
    source = mapping if isinstance(mapping, Mapping) else {}
    for name in ANALOG_SCALE_CHANNELS:
        key = name.replace(" ", "_").replace("/", "_")
        raw = source.get(name)
        if raw is None:
            raw = source.get(name.replace("/l", "/I"))
        text = str(raw if raw is not None else "1").strip() or "1"
        section[key] = text
    parser["DEW_SCALE"] = section
    with path.open("w", encoding="utf-8") as handle:
        parser.write(handle)


def _is_default_one(value: Any) -> bool:
    formatted = format_physical_scale_factor(value)
    if formatted is None:
        return True
    try:
        return abs(float(formatted) - 1.0) <= 1e-12
    except ValueError:
        return False


def load_saved_record_lead_s() -> float:
    """本机统一的提前录制秒数（设备页与各试验德威创面板共用）。"""
    path = scale_config_path()
    if not path.is_file():
        return 0.0
    parser = configparser.ConfigParser()
    try:
        parser.read(str(path), encoding="utf-8")
    except Exception:
        return 0.0
    if not parser.has_section("DEW_LEAD"):
        return 0.0
    try:
        return max(0.0, float(parser.get("DEW_LEAD", "record_lead_s", fallback="0") or 0))
    except (TypeError, ValueError):
        return 0.0


def save_saved_record_lead_s(lead_s: Any) -> float:
    """写入提前录制秒数；非法值按 0。返回实际写入值。不覆盖比例系数段。"""
    try:
        value = float(lead_s or 0)
    except (TypeError, ValueError):
        value = 0.0
    if value != value or value < 0:
        value = 0.0
    path = scale_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    parser = configparser.ConfigParser()
    if path.is_file():
        try:
            parser.read(str(path), encoding="utf-8")
        except Exception:
            # 读失败时不要空写覆盖：先尽量保留已有 DEW_SCALE
            try:
                text = path.read_text(encoding="utf-8")
                parser.read_string(text)
            except Exception:
                return value
    parser["DEW_LEAD"] = {"record_lead_s": f"{value:g}"}
    with path.open("w", encoding="utf-8") as handle:
        parser.write(handle)
    return value


def merge_device_and_saved_scales(
    device_scales: Optional[Mapping] = None,
    saved_scales: Optional[Mapping] = None,
) -> Dict[str, str]:
    """设备 XML 与本机记忆合并：本机有非 1 时优先，避免更新/重建 Oxygen 后被盖回 1。"""
    merged: Dict[str, str] = {}
    for name, raw in (device_scales or {}).items():
        formatted = format_physical_scale_factor(raw)
        if formatted is None:
            continue
        merged[ui_channel_name(str(name))] = formatted
    source = saved_scales if saved_scales is not None else load_saved_dew_scales()
    for name, raw in (source or {}).items():
        formatted = format_physical_scale_factor(raw)
        if formatted is None:
            continue
        key = ui_channel_name(str(name))
        if key not in merged or (_is_default_one(merged.get(key)) and not _is_default_one(formatted)):
            merged[key] = formatted
    return merged


def scales_worth_applying(scales) -> Dict[str, str]:
    """IOT/交接下发用：去掉空值和「全是默认 1」的噪声，避免盖掉本机已填的 1000 等。

    - 空 dict → 不下发
    - 若所有给出的值都是 1/1.0 → 视为未改，不下发
    - 否则只返回有有效数字的项（含故意写成 1 且同批有非 1 时保留 1）
    """
    if not isinstance(scales, Mapping) or not scales:
        return {}
    cleaned: Dict[str, str] = {}
    non_default = False
    for raw_name, raw_value in scales.items():
        formatted = format_physical_scale_factor(raw_value)
        if formatted is None:
            continue
        name = ui_channel_name(str(raw_name))
        cleaned[name] = formatted
        try:
            if abs(float(formatted) - 1.0) > 1e-12:
                non_default = True
        except ValueError:
            non_default = True
    if not cleaned or not non_default:
        return {}
    return cleaned


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
