# -*- coding: utf-8 -*-
"""Collect / export UI widget values for IOT templates."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLineEdit,
    QPlainTextEdit,
    QRadioButton,
    QTextEdit,
    QWidget,
)


def _read_one(w) -> Any:
    try:
        if isinstance(w, (QTextEdit, QPlainTextEdit)):
            return w.toPlainText()
        if isinstance(w, QLineEdit):
            return w.text()
        if isinstance(w, QCheckBox):
            return bool(w.isChecked())
        if isinstance(w, QRadioButton):
            return bool(w.isChecked())
        if isinstance(w, QComboBox):
            return w.currentText()
        if hasattr(w, "toPlainText"):
            return w.toPlainText()
        if hasattr(w, "text") and callable(w.text):
            return w.text()
        if hasattr(w, "isChecked") and callable(w.isChecked):
            return bool(w.isChecked())
        if hasattr(w, "currentText") and callable(w.currentText):
            return w.currentText()
    except Exception:
        return None
    return None


def collect_widget_values(root) -> Dict[str, Any]:
    """Collect named child widgets under root (objectName -> value)."""
    out: Dict[str, Any] = {}
    if root is None:
        return out
    widgets = []
    if hasattr(root, "findChildren"):
        try:
            widgets = list(root.findChildren(QWidget)) or []
        except Exception:
            widgets = []
    for name in dir(root):
        if name.startswith("_"):
            continue
        try:
            attr = getattr(root, name)
        except Exception:
            continue
        if isinstance(attr, QWidget):
            widgets.append(attr)
    seen = set()
    for w in widgets:
        try:
            name = str(w.objectName() or "").strip()
        except Exception:
            continue
        if not name or name in seen:
            continue
        if name.startswith("qt_") or name in ("centralwidget", "menubar", "statusbar"):
            continue
        seen.add(name)
        val = _read_one(w)
        if val is None:
            continue
        out[name] = val
    return out


def export_widgets_json(root, path, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Write widgets (+ optional meta) to JSON file; return payload."""
    payload: Dict[str, Any] = {"widgets": collect_widget_values(root)}
    if meta:
        for k, v in meta.items():
            if k == "widgets":
                continue
            payload[k] = v
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload
