# -*- coding: utf-8 -*-
"""Per-test UI preset: dialog fields + Dewetron export checks (local JSON)."""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, Optional

from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QLineEdit,
    QSpinBox,
    QTextEdit,
    QWidget,
)


def _preset_root() -> str:
    override = (os.environ.get("SOLARAUTOTEST_TEST_PRESET_DIR") or "").strip()
    if override:
        path = os.path.abspath(override)
    else:
        from utils.app_paths import data_subdir

        path = data_subdir("command_save_files", "test_presets")
    os.makedirs(path, exist_ok=True)
    return path


def safe_test_id(test_name: str) -> str:
    safe = re.sub(r"[^\w\-]+", "_", str(test_name or "unknown"), flags=re.UNICODE)
    safe = safe.strip("_") or "unknown"
    return safe[:120]


def preset_path(test_name: str) -> str:
    return os.path.join(_preset_root(), f"{safe_test_id(test_name)}.json")


def _skip_object_name(name: str) -> bool:
    if not name:
        return True
    if name.startswith("log_") or "ReturnMessage" in name:
        return True
    if name in {"textEdit_AC"}:  # device log pane
        return True
    return False


def collect_dialog_fields(root: QWidget) -> Dict[str, Any]:
    """Snapshot editable fields under a test dialog / UI object."""
    if root is None or not hasattr(root, "findChildren"):
        return {}
    out: Dict[str, Any] = {}
    widgets = []
    widgets.extend(root.findChildren(QTextEdit))
    widgets.extend(root.findChildren(QLineEdit))
    widgets.extend(root.findChildren(QComboBox))
    widgets.extend(root.findChildren(QCheckBox))
    widgets.extend(root.findChildren(QSpinBox))
    widgets.extend(root.findChildren(QDoubleSpinBox))
    seen = set()
    for w in widgets:
        wid = id(w)
        if wid in seen:
            continue
        seen.add(wid)
        name = w.objectName() or ""
        if _skip_object_name(name):
            continue
        if isinstance(w, QTextEdit):
            if w.isReadOnly():
                continue
            out[name] = w.toPlainText()
        elif isinstance(w, QLineEdit):
            if w.isReadOnly():
                continue
            out[name] = w.text()
        elif isinstance(w, QComboBox):
            out[name] = w.currentText()
        elif isinstance(w, QCheckBox):
            out[name] = bool(w.isChecked())
        elif isinstance(w, (QSpinBox, QDoubleSpinBox)):
            out[name] = w.value()
    return out


def apply_dialog_fields(root: QWidget, fields: Dict[str, Any]) -> int:
    if root is None or not fields:
        return 0
    n = 0
    for name, value in fields.items():
        if _skip_object_name(name):
            continue
        w = root.findChild(QWidget, name)
        if w is None:
            continue
        try:
            if isinstance(w, QTextEdit) and not w.isReadOnly():
                w.setPlainText(str(value))
                n += 1
            elif isinstance(w, QLineEdit) and not w.isReadOnly():
                w.setText(str(value))
                n += 1
            elif isinstance(w, QComboBox):
                text = str(value)
                idx = w.findText(text)
                if idx >= 0:
                    w.setCurrentIndex(idx)
                else:
                    w.setCurrentText(text)
                n += 1
            elif isinstance(w, QCheckBox):
                w.setChecked(bool(value))
                n += 1
            elif isinstance(w, QSpinBox):
                w.setValue(int(value))
                n += 1
            elif isinstance(w, QDoubleSpinBox):
                w.setValue(float(value))
                n += 1
        except Exception:
            continue
    return n


def save_test_preset(
    test_name: str,
    *,
    fields: Optional[Dict[str, Any]] = None,
    dew_export: Optional[Dict[str, Any]] = None,
    root: Optional[QWidget] = None,
) -> str:
    """Persist per-test UI snapshot. Returns file path."""
    payload: Dict[str, Any] = {"test_name": test_name, "fields": {}, "dew_export": {}}
    path = preset_path(test_name)
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                old = json.load(fh)
            if isinstance(old, dict):
                payload["fields"] = dict(old.get("fields") or {})
                payload["dew_export"] = dict(old.get("dew_export") or {})
        except Exception:
            pass
    if root is not None:
        payload["fields"] = collect_dialog_fields(root)
    elif fields is not None:
        payload["fields"] = dict(fields)
    if dew_export is not None:
        payload["dew_export"] = dict(dew_export)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    return path


def load_test_preset(test_name: str) -> Optional[Dict[str, Any]]:
    path = preset_path(test_name)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    return {
        "test_name": str(data.get("test_name") or test_name),
        "fields": dict(data.get("fields") or {}),
        "dew_export": dict(data.get("dew_export") or {}),
    }


def apply_test_preset(test_name: str, root: QWidget) -> bool:
    """Load preset into dialog + Dewetron panel. Returns True if anything applied."""
    data = load_test_preset(test_name)
    if not data:
        return False
    applied = False
    fields = data.get("fields") or {}
    if fields and apply_dialog_fields(root, fields) > 0:
        applied = True
    dew = data.get("dew_export") or {}
    panel = getattr(root, "dewetronPanel", None)
    if panel is not None and dew:
        try:
            if hasattr(panel, "set_preset_name"):
                panel.set_preset_name(test_name)
            fields_list = dew.get("export_fields")
            if fields_list is not None and hasattr(panel, "set_checked_export_fields"):
                panel.set_checked_export_fields(fields_list)
                applied = True
            rate = str(dew.get("rate_text") or "").strip()
            if rate and hasattr(panel, "comboBox_DEW_MaxRefreshRate"):
                combo = panel.comboBox_DEW_MaxRefreshRate
                idx = combo.findText(rate)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
                else:
                    combo.setEditText(rate)
                applied = True
            if "decimal_places" in dew and hasattr(panel, "spinBox_DEW_DecimalPlaces"):
                panel.spinBox_DEW_DecimalPlaces.setValue(int(dew.get("decimal_places") or 4))
                applied = True
            if "realtime_waveform" in dew and hasattr(panel, "checkBox_DEW_RealtimeWaveform"):
                panel.checkBox_DEW_RealtimeWaveform.setChecked(bool(dew.get("realtime_waveform")))
                applied = True
        except Exception:
            pass
    return applied


def snapshot_and_save_test_preset(test_name: str, root: QWidget) -> str:
    """Collect dialog + dew panel and save under test name."""
    dew_export = None
    panel = getattr(root, "dewetronPanel", None)
    if panel is not None:
        try:
            if hasattr(panel, "set_preset_name"):
                panel.set_preset_name(test_name)
            cfg = panel.get_config() if hasattr(panel, "get_config") else None
            if cfg is not None:
                dew_export = {
                    "export_fields": list(getattr(cfg, "export_fields", []) or []),
                    "rate_text": str(getattr(cfg, "rate_text", "Default") or "Default"),
                    "decimal_places": int(getattr(cfg, "decimal_places", 4) or 4),
                    "realtime_waveform": bool(getattr(cfg, "realtime_waveform", False)),
                }
            elif hasattr(panel, "get_checked_export_fields"):
                dew_export = {"export_fields": list(panel.get_checked_export_fields() or [])}
        except Exception:
            dew_export = None
    return save_test_preset(test_name, root=root, dew_export=dew_export)
