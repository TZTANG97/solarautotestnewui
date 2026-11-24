# -*- coding: utf-8 -*-
"""WT 采集模式：宏 (WTViewer) / SCPI 命令。默认宏，兼容旧配置。"""
from __future__ import annotations

from typing import Any, Mapping, Optional

MODE_MACRO = "macro"
MODE_SCPI = "scpi"

MODE_LABEL_MACRO = "宏模式 (WTViewer)"
MODE_LABEL_SCPI = "SCPI 命令模式"

MODE_LABELS = {
    MODE_MACRO: MODE_LABEL_MACRO,
    MODE_SCPI: MODE_LABEL_SCPI,
}

# comboBox_ReplaceRate 与 wt_config_content 一致（四机型统一）
REPLACE_RATE_OPTIONS = (
    "50ms",
    "100ms",
    "250ms",
    "500ms",
    "1s",
    "2s",
    "5s",
    "10s",
    "20s",
)

CONFIG_KEY = "wt_acquire_mode"
COMBO_NAME = "comboBox_wt_acquire_mode"


def normalize_mode(value: Any) -> str:
    text = str(value or "").strip().casefold()
    if text in (MODE_SCPI, "scpi", "command", "命令", "1"):
        return MODE_SCPI
    if text in (
        MODE_MACRO,
        "macro",
        "viewer",
        "wtviewer",
        "宏",
        "0",
        "",
    ):
        return MODE_MACRO
    # combo index from save/open
    if text.isdigit():
        return MODE_SCPI if int(text) == 1 else MODE_MACRO
    # label match
    if "scpi" in text or "命令" in text:
        return MODE_SCPI
    return MODE_MACRO


def mode_to_combo_index(mode: Any) -> int:
    return 1 if normalize_mode(mode) == MODE_SCPI else 0


def combo_index_to_mode(index: Any) -> str:
    try:
        return MODE_SCPI if int(index) == 1 else MODE_MACRO
    except (TypeError, ValueError):
        return MODE_MACRO


def is_scpi_mode(config: Optional[Mapping] = None, mode: Any = None) -> bool:
    if mode is not None:
        return normalize_mode(mode) == MODE_SCPI
    if isinstance(config, Mapping):
        if CONFIG_KEY in config:
            return normalize_mode(config.get(CONFIG_KEY)) == MODE_SCPI
        if COMBO_NAME in config:
            return combo_index_to_mode(config.get(COMBO_NAME)) == MODE_SCPI
    return False


def read_mode_from_ui(ui) -> str:
    """Read mode from combo on a WT page / finder / dialog."""
    try:
        combo = getattr(ui, COMBO_NAME, None)
    except Exception:
        combo = None
    if combo is None:
        return MODE_MACRO
    try:
        data = combo.currentData()
        if data:
            return normalize_mode(data)
    except Exception:
        pass
    try:
        return combo_index_to_mode(combo.currentIndex())
    except Exception:
        return MODE_MACRO


def apply_mode_to_ui(ui, mode: Any) -> None:
    combo = getattr(ui, COMBO_NAME, None)
    if combo is None:
        return
    try:
        combo.setCurrentIndex(mode_to_combo_index(mode))
    except Exception:
        pass


def apply_mode_across(root, mode: Any) -> int:
    """把宏/SCPI 写到每个 WT 型号页的采集模式下拉。返回写中的个数。"""
    idx = mode_to_combo_index(normalize_mode(mode))
    updated = 0
    seen = set()

    def _set(combo) -> None:
        nonlocal updated
        if combo is None:
            return
        ident = id(combo)
        if ident in seen:
            return
        seen.add(ident)
        try:
            combo.setCurrentIndex(idx)
            updated += 1
        except Exception:
            pass

    pages = []
    stacked = getattr(root, "_wtStacked", None)
    try:
        if stacked is not None and hasattr(stacked, "count"):
            pages.extend(stacked.widget(i) for i in range(int(stacked.count())))
    except Exception:
        pass
    pages.append(root)
    for page in pages:
        if page is None:
            continue
        combo = None
        finder = getattr(page, "findChild", None)
        if callable(finder):
            try:
                from PyQt5.QtWidgets import QWidget

                combo = finder(QWidget, COMBO_NAME)
            except Exception:
                combo = None
        if combo is None:
            combo = getattr(page, COMBO_NAME, None)
        _set(combo)
    return updated


def inject_mode_into_params(params_dict: dict, ui) -> dict:
    """Append acquire-mode keys into WT params_dict (runtime + save)."""
    if not isinstance(params_dict, dict):
        return params_dict
    try:
        mode = read_mode_from_ui(ui)
    except Exception:
        mode = MODE_MACRO
    params_dict[CONFIG_KEY] = mode
    params_dict[COMBO_NAME] = mode_to_combo_index(mode)
    return params_dict


def rate_text_from_config(config: Optional[Mapping]) -> str:
    if not isinstance(config, Mapping):
        return "100ms"
    idx = config.get("comboBox_ReplaceRate", 1)
    try:
        i = int(idx)
    except (TypeError, ValueError):
        i = 1
    if 0 <= i < len(REPLACE_RATE_OPTIONS):
        return REPLACE_RATE_OPTIONS[i]
    # already a text?
    raw = str(idx).strip()
    if raw.endswith("ms") or raw.endswith("s"):
        return raw
    return "100ms"


def filename_list_from_config(config: Optional[Mapping]) -> list:
    if not isinstance(config, Mapping):
        return []
    names_raw = str(config.get("textEdit_FileNameList") or "").strip()
    return [n.strip() for n in names_raw.replace("，", ",").split(",") if n.strip()]


def scpi_file_slot(config: Optional[Mapping], now_save_file) -> tuple:
    """本轮 SCPI 应写入的文件名下标和名字。

    调用方必须把名字记到 save_file_name。SCPI 路径原先不记，
    下一档仍看到「序号 0 且文件名为空」，分开录每一档都写进同一个 CSV。
    """
    names = filename_list_from_config(config)
    try:
        idx = int(now_save_file or 0)
    except (TypeError, ValueError):
        idx = 0
    if idx < 0:
        idx = 0
    if not names:
        return idx, ""
    if idx >= len(names):
        idx = len(names) - 1
    return idx, names[idx]


def resolve_csv_path(config: Optional[Mapping], file_index: int = 0) -> str:
    """Build CSV output path from SavePath + FileNameList[+index]."""
    import os

    if not isinstance(config, Mapping):
        return ""
    folder = str(config.get("textEdit_SavePath") or "").strip()
    try:
        from utils.wt_save_path import ensure_wt_save_dir

        folder = ensure_wt_save_dir(folder)
    except Exception:
        if folder:
            try:
                os.makedirs(folder, exist_ok=True)
            except Exception:
                pass
    names = filename_list_from_config(config)
    if not names:
        names = ["WT_SCPI"]
    idx = max(0, min(int(file_index), len(names) - 1))
    name = names[idx]
    if not name.lower().endswith(".csv"):
        name = f"{name}.csv"
    if folder:
        return os.path.join(folder, name)
    return name
