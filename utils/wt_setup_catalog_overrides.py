# -*- coding: utf-8 -*-
"""WT 设置区命令库覆盖（如 comboBox_ReplaceRate → :RATE 前缀/模板）。"""
from __future__ import annotations

from typing import Dict, Optional

_DEFAULT_RATE_PREFIX = ":RATE"

_rate_prefix: str = _DEFAULT_RATE_PREFIX
_rate_template: Optional[str] = None
_setup_overrides: Dict[str, str] = {}


def set_rate_scpi_prefix(value: Optional[str]) -> None:
    """value 为前缀（如 :RATE）或带 {ms} 的完整模板。"""
    global _rate_prefix, _rate_template
    if value is None or not str(value).strip():
        _rate_prefix = _DEFAULT_RATE_PREFIX
        _rate_template = None
        _setup_overrides.pop("comboBox_ReplaceRate", None)
        return
    v = str(value).strip()
    _setup_overrides["comboBox_ReplaceRate"] = v
    if "{ms}" in v:
        _rate_template = v
        _rate_prefix = _DEFAULT_RATE_PREFIX
    else:
        _rate_template = None
        _rate_prefix = v or _DEFAULT_RATE_PREFIX


def get_rate_scpi_prefix() -> str:
    return _rate_prefix


def get_rate_scpi_template() -> Optional[str]:
    return _rate_template


def clear_wt_setup_catalog_overrides() -> None:
    global _rate_prefix, _rate_template
    _rate_prefix = _DEFAULT_RATE_PREFIX
    _rate_template = None
    _setup_overrides.clear()


def get_wt_setup_overrides() -> Dict[str, str]:
    return dict(_setup_overrides)
