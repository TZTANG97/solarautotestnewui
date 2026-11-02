# -*- coding: utf-8 -*-
"""WT 电压/电流比例系数。

横河通信手册（WT5000 IM WT5000-17EN 5-90，WT3000 IM 760301-17E 6-70）
两边都是同一组命令，不能改写成 :SCALING 或把 STATE 放到元素前面：

    :INPUT:SCALING:STATE:ELEMENTn ON|OFF
    :INPUT:SCALING:VT:ELEMENTn <比例>
    :INPUT:SCALING:CT:ELEMENTn <比例>

比例范围 0.0001～99999.9999。1 表示不额外缩放。空或越界的格子不下发。
"""
from __future__ import annotations

import configparser
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

SCALE_ELEMENTS = (1, 2, 3, 4, 5, 6, 7)
_SCALE_MIN = 0.0001
_SCALE_MAX = 99999.9999


def scale_object_name(kind: str, element: int) -> str:
    return f"lineEdit_wt_{kind}_{int(element)}"


def format_scale_factor(value) -> Optional[str]:
    """收成仪器能接受的十进制。空、非法或超出手册范围返回 None。"""
    text = str(value if value is not None else "").strip().replace("，", "")
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    if not math.isfinite(number) or number < _SCALE_MIN or number > _SCALE_MAX:
        return None
    rendered = f"{number:.10f}".rstrip("0").rstrip(".")
    if rendered in ("", "-0"):
        return "0"
    return rendered


def scales_from_mapping(config: Optional[Mapping]) -> Dict[str, str]:
    """从开测参数里取出已填写的 VT/CT。键为 vt1、ct1。"""
    out: Dict[str, str] = {}
    if not isinstance(config, Mapping):
        return out
    for element in SCALE_ELEMENTS:
        for kind in ("vt", "ct"):
            raw = config.get(scale_object_name(kind, element))
            formatted = format_scale_factor(raw)
            if formatted is None:
                continue
            out[f"{kind}{element}"] = formatted
    return out


def merge_scale_fields(params: Dict[str, Any], ui: Any) -> Dict[str, Any]:
    """把界面上的比例系数写进 WT 参数字典，供 SCPI 开测使用。"""
    if not isinstance(params, dict) or ui is None:
        return params
    for element in SCALE_ELEMENTS:
        for kind in ("vt", "ct"):
            name = scale_object_name(kind, element)
            widget = getattr(ui, name, None)
            if widget is None:
                continue
            text = ""
            if hasattr(widget, "text"):
                text = widget.text()
            elif hasattr(widget, "toPlainText"):
                text = widget.toPlainText()
            params[name] = str(text or "").strip() or "1"
    return params


def max_scale_element(style: str = "", config: Optional[Mapping] = None) -> int:
    """按当前试验的分析仪型号决定下发几个元素。连接页固定有 1–7。"""
    probe: Dict[str, Any] = dict(config or {})
    if style and not probe.get("Style"):
        probe["Style"] = style
    try:
        from utils.wt_scpi_items import model_of

        model = model_of(probe)
    except Exception:
        model = ""
    return {"3000": 4, "1800": 6, "1806": 6, "5000": 7}.get(model, 7)


def scale_config_path() -> Path:
    """比例系数配置档。环境变量可改路径，测试不会写到仓库里的真文件。"""
    override = (os.environ.get("SOLARAUTOTEST_WT_SCALE") or "").strip()
    if override:
        return Path(override).expanduser()
    from utils.app_paths import _repo_or_install_root

    return _repo_or_install_root() / "config_files" / "wt_scale.ini"


def load_saved_scales() -> Dict[str, str]:
    """从配置档读出上次填写的 VT/CT。键是界面对象名。"""
    path = scale_config_path()
    if not path.is_file():
        return {}
    parser = configparser.ConfigParser()
    try:
        parser.read(path, encoding="utf-8")
    except Exception:
        return {}
    if not parser.has_section("WT_SCALE"):
        return {}
    out: Dict[str, str] = {}
    for element in SCALE_ELEMENTS:
        for kind in ("vt", "ct"):
            key = f"{kind}{element}"
            if not parser.has_option("WT_SCALE", key):
                continue
            text = parser.get("WT_SCALE", key).strip()
            if text:
                out[scale_object_name(kind, element)] = text
    return out


def save_saved_scales(mapping: Optional[Mapping]) -> None:
    """把连接页上的比例系数写入配置档。"""
    path = scale_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    parser = configparser.ConfigParser()
    section: Dict[str, str] = {}
    source = mapping or {}
    for element in SCALE_ELEMENTS:
        for kind in ("vt", "ct"):
            name = scale_object_name(kind, element)
            raw = source.get(name, source.get(f"{kind}{element}", "1"))
            section[f"{kind}{element}"] = str(raw or "1").strip() or "1"
    parser["WT_SCALE"] = section
    with path.open("w", encoding="utf-8") as handle:
        parser.write(handle)


def scales_from_root(root: Any) -> Dict[str, str]:
    """从连接页或主窗口读出当前填写值。先看挂在对象上的输入框，再搜子控件。"""
    out: Dict[str, str] = {}
    if root is None:
        return out
    line_edit = None
    try:
        from PyQt5.QtWidgets import QLineEdit

        line_edit = QLineEdit
    except Exception:
        line_edit = None
    for element in SCALE_ELEMENTS:
        for kind in ("vt", "ct"):
            name = scale_object_name(kind, element)
            edit = getattr(root, name, None)
            if edit is None and line_edit is not None and hasattr(root, "findChildren"):
                found = root.findChildren(line_edit, name)
                edit = found[0] if found else None
            if edit is None or not hasattr(edit, "text"):
                continue
            text = str(edit.text() or "").strip()
            if text:
                out[name] = text
    return out


def scales_for_run(
    style: str = "",
    config: Optional[Mapping] = None,
    root: Any = None,
    roots: Optional[List[Any]] = None,
) -> Dict[str, str]:
    """开测用的系数只来自连接页，连接页不在时用配置档。"""
    del style, config
    ordered: List[Any] = list(roots or [])
    if root is not None and root not in ordered:
        ordered.insert(0, root)
    for item in ordered:
        live = scales_from_root(item)
        if live:
            return live
    return load_saved_scales()


def scaling_commands(style: str = "", config: Optional[Mapping] = None) -> List[str]:
    """按手册生成比例系数命令。没有任何合法系数时不发 STATE。"""
    scales = scales_from_mapping(config)
    if not scales:
        return []
    limit = max_scale_element(style, config)
    commands: List[str] = []
    for element in SCALE_ELEMENTS:
        if element > limit:
            continue
        vt = scales.get(f"vt{element}")
        ct = scales.get(f"ct{element}")
        if vt is None and ct is None:
            continue
        commands.append(f":INPUT:SCALING:STATE:ELEMENT{element} ON")
        if vt is not None:
            commands.append(f":INPUT:SCALING:VT:ELEMENT{element} {vt}")
        if ct is not None:
            commands.append(f":INPUT:SCALING:CT:ELEMENT{element} {ct}")
    return commands
