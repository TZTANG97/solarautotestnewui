# -*- coding: utf-8 -*-
"""蓝点 SAS 曲线 → 实验直流源四点。

实验对话框和 IOT 实验管理用的是 Vmp/Imp/Voc/Isc（textEdit_S1_DC1_*），
不是蓝点页上的 Pmpp/Umpp/填充因子。下发曲线后要写回这些字段。
"""
from __future__ import annotations

from typing import Any, Dict, Mapping

EXPERIMENT_DC1_BY_IV = {
    "vmp": "textEdit_S1_DC1_VOLT",
    "imp": "textEdit_S1_DC1_CURR",
    "voc": "textEdit_S1_DC1_Voc",
    "isc": "textEdit_S1_DC1_Isc",
    "pf": "textEdit_S1_DC1_PF",
}


def experiment_dc1_widgets(iv: Mapping[str, Any] | None) -> Dict[str, str]:
    """蓝点四点 → 实验直流电源1 的控件名。空值不带。"""
    src = iv if isinstance(iv, Mapping) else {}
    out: Dict[str, str] = {}
    for key, widget_name in EXPERIMENT_DC1_BY_IV.items():
        val = str(src.get(key) or "").strip()
        if val:
            out[widget_name] = val
    return out


def overlay_experiment_dc1(widgets: Mapping[str, Any] | None, iv: Mapping[str, Any] | None) -> Dict[str, Any]:
    """上报实验参数时，用蓝点实际四点盖掉对话框里的旧直流值。"""
    out = dict(widgets or {})
    out.update(experiment_dc1_widgets(iv))
    return out


def apply_experiment_dc1_to_open_widgets(iv: Mapping[str, Any] | None) -> int:
    """把四点写进已经打开的实验对话框。返回写了多少个控件。"""
    fields = experiment_dc1_widgets(iv)
    if not fields:
        return 0
    try:
        from PyQt5.QtWidgets import QApplication
    except Exception:
        return 0
    app = QApplication.instance()
    if app is None:
        return 0
    written = 0
    for widget in app.allWidgets():
        name = str(widget.objectName() or "")
        val = fields.get(name)
        if not val:
            continue
        try:
            if hasattr(widget, "setPlainText"):
                widget.setPlainText(val)
            elif hasattr(widget, "setText"):
                widget.setText(val)
            else:
                continue
            written += 1
        except Exception:
            continue
    return written
