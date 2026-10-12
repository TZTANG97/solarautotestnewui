# -*- coding: utf-8 -*-
"""国家标准 → Dialog 控件回填（闪变/谐波等共用，避免循环导入 handoff）。"""
from __future__ import annotations

from typing import Any


def set_ui_control_value(ctrl: Any, value: Any) -> bool:
    """按控件类型写值。"""
    if ctrl is None:
        return False
    try:
        from PyQt5.QtWidgets import (
            QCheckBox,
            QComboBox,
            QDoubleSpinBox,
            QLineEdit,
            QSpinBox,
            QTextEdit,
        )
    except Exception:
        return False
    if isinstance(ctrl, QCheckBox):
        ctrl.setChecked(
            value in (True, "1", 1, "true", "True", "on", "ON", "yes", "YES")
        )
        return True
    if isinstance(ctrl, (QSpinBox, QDoubleSpinBox)):
        try:
            ctrl.setValue(int(float(value)))
            return True
        except (TypeError, ValueError):
            return False
    if isinstance(ctrl, QComboBox):
        text = str(value)
        idx = ctrl.findText(text)
        if idx >= 0:
            ctrl.setCurrentIndex(idx)
            return True
        for i in range(ctrl.count()):
            if str(ctrl.itemText(i)).strip() == text.strip():
                ctrl.setCurrentIndex(i)
                return True
        return False
    if isinstance(ctrl, QTextEdit):
        ctrl.setPlainText(str(value))
        return True
    if isinstance(ctrl, QLineEdit):
        ctrl.setText(str(value))
        return True
    if hasattr(ctrl, "setPlainText"):
        ctrl.setPlainText(str(value))
        return True
    if hasattr(ctrl, "setText"):
        ctrl.setText(str(value))
        return True
    if hasattr(ctrl, "setValue"):
        try:
            ctrl.setValue(int(float(value)))
            return True
        except Exception:
            return False
    return False


def sync_standard_combo(ui: Any, sid: str) -> None:
    """同步 comboBox_SolarStandard 选中项（阻信号，避免二次回填）。"""
    combo = getattr(ui, "comboBox_SolarStandard", None)
    if combo is None or not hasattr(combo, "findData"):
        return
    idx = combo.findData(sid)
    if idx < 0:
        for i in range(combo.count()):
            if combo.itemData(i) == sid:
                idx = i
                break
    if idx >= 0 and combo.currentIndex() != idx:
        blocked = combo.blockSignals(True)
        try:
            combo.setCurrentIndex(idx)
        finally:
            combo.blockSignals(blocked)


def apply_defaults_dict_to_ui(
    ui: Any,
    defaults: dict,
    *,
    force: bool = True,
) -> None:
    """把 defaults 字典写到 Dialog；跳过 _ 元数据与 solarStandard。"""
    for key, val in (defaults or {}).items():
        sk = str(key)
        if sk.startswith("_") or sk in ("solarStandard", "solar_standard", "standard"):
            continue
        ctrl = getattr(ui, sk, None)
        if ctrl is None:
            continue
        if not force:
            try:
                if hasattr(ctrl, "toPlainText") and str(ctrl.toPlainText() or "").strip():
                    continue
                if hasattr(ctrl, "text") and not hasattr(ctrl, "currentText"):
                    t = ctrl.text() if callable(ctrl.text) else ""
                    if str(t or "").strip():
                        continue
            except Exception:
                pass
        set_ui_control_value(ctrl, val)
