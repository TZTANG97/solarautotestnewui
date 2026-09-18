# -*- coding: utf-8 -*-
"""过载试验 IOT 参数 schema 加载（软件侧，与 IOT solar_test_schemas 同源 JSON）。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

_DATA = Path(__file__).resolve().parent / "iot_overload_schema_data.json"
_cache: Dict[str, Any] | None = None


def load_overload_schema() -> Dict[str, Any]:
    global _cache
    if _cache is not None:
        return _cache
    raw = json.loads(_DATA.read_text(encoding="utf-8"))
    _cache = raw
    return raw


def default_widgets() -> Dict[str, Any]:
    """schema 默认值 → handoff params.widgets。"""
    schema = load_overload_schema()
    out: Dict[str, Any] = {}
    for f in schema.get("fields") or []:
        name = f.get("name")
        if not name:
            continue
        if f.get("default") is not None:
            out[name] = f["default"]
    return out


def merge_widgets(base: Dict[str, Any] | None, override: Dict[str, Any] | None) -> Dict[str, Any]:
    merged = dict(default_widgets())
    if isinstance(base, dict):
        merged.update(base)
    if isinstance(override, dict):
        merged.update(override)
    return merged


def field_names() -> List[str]:
    return [str(f.get("name")) for f in (load_overload_schema().get("fields") or []) if f.get("name")]
