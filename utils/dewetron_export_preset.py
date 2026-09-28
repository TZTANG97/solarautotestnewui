# -*- coding: utf-8 -*-
"""德威创导出勾选预设：保存后下次自动加载 / 可命名多套选用。"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


def _preset_dir() -> str:
    override = (os.environ.get("SOLARAUTOTEST_DEW_PRESET_DIR") or "").strip()
    if override:
        path = os.path.abspath(override)
    else:
        from utils.app_paths import data_subdir

        path = data_subdir("command_save_files", "dewetron_presets")
    os.makedirs(path, exist_ok=True)
    return path


def preset_file_path(preset_name: str = "default") -> str:
    safe = re.sub(r"[^\w\-]+", "_", str(preset_name or "default")).strip("_") or "default"
    return os.path.join(_preset_dir(), f"export_fields_{safe}.json")


def list_export_presets() -> List[str]:
    """本机已保存的配置名（不含路径），按名称排序；default 靠前。"""
    root = _preset_dir()
    names: List[str] = []
    try:
        for fn in os.listdir(root):
            if not fn.startswith("export_fields_") or not fn.endswith(".json"):
                continue
            mid = fn[len("export_fields_") : -len(".json")]
            if mid:
                names.append(mid)
    except OSError:
        return []
    names = sorted(set(names), key=lambda x: (0 if x == "default" else 1, x.lower()))
    return names


def save_export_preset(
    *,
    export_fields: List[str],
    rate_text: str = "Default",
    decimal_places: int = 4,
    realtime_waveform: bool = False,
    preset_name: str = "default",
) -> str:
    """写入勾选预设，返回文件路径。"""
    path = preset_file_path(preset_name)
    payload: Dict[str, Any] = {
        "name": str(preset_name or "default"),
        "export_fields": [str(x) for x in (export_fields or []) if str(x).strip()],
        "rate_text": str(rate_text or "Default"),
        "decimal_places": int(decimal_places),
        "realtime_waveform": bool(realtime_waveform),
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    return path


def load_export_preset(preset_name: str = "default") -> Optional[Dict[str, Any]]:
    """读取勾选预设；不存在返回 None。"""
    path = preset_file_path(preset_name)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    fields = data.get("export_fields") or []
    if not isinstance(fields, list):
        fields = []
    return {
        "name": str(data.get("name") or preset_name or "default"),
        "export_fields": [str(x) for x in fields if str(x).strip()],
        "rate_text": str(data.get("rate_text") or "Default"),
        "decimal_places": int(data.get("decimal_places") or 4),
        "realtime_waveform": bool(data.get("realtime_waveform")),
    }


def delete_export_preset(preset_name: str) -> bool:
    """删除命名配置（不允许删 default）。"""
    name = (preset_name or "").strip()
    if not name or name == "default":
        return False
    path = preset_file_path(name)
    if not os.path.isfile(path):
        return False
    try:
        os.remove(path)
        return True
    except OSError:
        return False
