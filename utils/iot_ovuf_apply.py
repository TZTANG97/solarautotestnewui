# -*- coding: utf-8 -*-
"""过欠压_过欠频：IOT widgets → Dialog 强制写入与回读。

途哲台上常见：job.widgets 已是 182 / 2 秒，但 Dialog 仍显示字段记忆旧值（181.7 / 11）。
原因是 ensure 页 polish 会先 restore 历史，后续若再 polish / Soft Panel 干扰会盖掉。
本模块在 handoff 写完后、Append 前再强制对齐关键并回写字段记忆，避免下次再被旧值盖掉。
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

OVUF_CRITICAL_KEYS: Tuple[str, ...] = (
    "textEdit_S3_Step_Size",
    "textEdit_S3_TIME",
    "comboBox_S3_TIME",
    "textEdit_S3_AC_VOLT_Start",
    "textEdit_S3_AC_VOLT_End",
    "textEdit_S3_AC_FR_Start",
    "textEdit_S3_AC_FR_End",
    "textEdit_S4_Step_Size",
    "textEdit_S4_TIME",
    "comboBox_S4_TIME",
    "textEdit_S4_AC_VOLT_Start",
    "textEdit_S4_AC_VOLT_End",
    "textEdit_S4_AC_FR_Start",
    "textEdit_S4_AC_FR_End",
    "textEdit_S5_Step_Size",
    "textEdit_S5_TIME",
    "comboBox_S5_TIME",
    "textEdit_S5_AC_VOLT_Start",
    "textEdit_S5_AC_VOLT_End",
    "textEdit_S5_AC_FR_Start",
    "textEdit_S5_AC_FR_End",
    "textEdit_S6_Step_Size",
    "textEdit_S6_TIME",
    "comboBox_S6_TIME",
    "textEdit_S6_AC_VOLT_Start",
    "textEdit_S6_AC_VOLT_End",
    "textEdit_S6_AC_FR_Start",
    "textEdit_S6_AC_FR_End",
    "textEdit_ovuf_grid_wait",
    "comboBox_ovuf_grid_wait",
    "textEdit_S1_TIME",
    "comboBox_S1_TIME",
)

OVUF_MEMORY_SCOPE = "test:过欠压_过欠频"


def _norm(val: Any) -> str:
    return str(val if val is not None else "").strip()


# IOT/Blockly 常下发 min|sec|ms；Dialog 选项只有 分钟|秒|毫秒
_TIME_UNIT_ALIASES = {
    "min": "分钟",
    "mins": "分钟",
    "minute": "分钟",
    "minutes": "分钟",
    "分钟": "分钟",
    "sec": "秒",
    "secs": "秒",
    "second": "秒",
    "seconds": "秒",
    "s": "秒",
    "秒": "秒",
    "ms": "毫秒",
    "msec": "毫秒",
    "millis": "毫秒",
    "millisecond": "毫秒",
    "milliseconds": "毫秒",
    "毫秒": "毫秒",
}

_TIME_UNIT_KEYS = frozenset(
    {
        "comboBox_S1_TIME",
        "comboBox_S3_TIME",
        "comboBox_S4_TIME",
        "comboBox_S5_TIME",
        "comboBox_S6_TIME",
        "comboBox_S7_TIME",
        "comboBox_S8_TIME",
        "comboBox_ovuf_grid_wait",
    }
)


def normalize_time_unit(val: Any) -> str:
    """把 min/sec/ms 等归一成 Dialog 上的 分钟/秒/毫秒。"""
    s = _norm(val)
    if not s:
        return s
    return _TIME_UNIT_ALIASES.get(s.lower(), _TIME_UNIT_ALIASES.get(s, s))


def time_unit_aliases(val: Any) -> List[str]:
    """供 QComboBox.findText 尝试的候选（含原文与中文）。"""
    raw = _norm(val)
    canon = normalize_time_unit(raw)
    out: List[str] = []
    for x in (raw, canon, "分钟", "秒", "毫秒"):
        if x and x not in out:
            out.append(x)
    return out


def _values_equal(want: str, got: str, *, key: str = "") -> bool:
    """字符串相等；数值字段允许 182 vs 182.0；时间单位允许 min≈分钟。"""
    if want == got:
        return True
    if key in _TIME_UNIT_KEYS or key.endswith("_TIME") or "grid_wait" in key:
        if normalize_time_unit(want) == normalize_time_unit(got):
            return True
    try:
        return abs(float(want) - float(got)) < 1e-9
    except (TypeError, ValueError):
        return False


def read_named_widget(root: Any, name: str) -> str:
    """读 Dialog 控件文本；优先 getattr（Ui 对象），再 findChild。"""
    if root is None or not name:
        return ""
    w = getattr(root, name, None)
    if w is None and hasattr(root, "findChild"):
        try:
            from PyQt5.QtWidgets import QWidget

            w = root.findChild(QWidget, name)
        except Exception:
            w = None
    if w is None:
        return ""
    try:
        from PyQt5.QtWidgets import QCheckBox, QComboBox, QLineEdit, QPlainTextEdit, QTextEdit

        if isinstance(w, (QTextEdit, QPlainTextEdit)):
            return _norm(w.toPlainText())
        if isinstance(w, QLineEdit):
            return _norm(w.text())
        if isinstance(w, QComboBox):
            return _norm(w.currentText())
        if isinstance(w, QCheckBox):
            return "1" if w.isChecked() else "0"
    except Exception:
        return ""
    return ""


def critical_payload(widgets: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    src = widgets if isinstance(widgets, dict) else {}
    out: Dict[str, Any] = {}
    for k in OVUF_CRITICAL_KEYS:
        if k not in src:
            continue
        v = src.get(k)
        if v is None or _norm(v) == "":
            continue
        # 写入前先把 min→分钟，否则 QComboBox.findText("min") 失败，回读永远不一致
        if k in _TIME_UNIT_KEYS:
            v = normalize_time_unit(v)
        out[k] = v
    return out


def readback_mismatch(
    root: Any,
    expected: Dict[str, Any],
    *,
    keys: Optional[Iterable[str]] = None,
) -> Tuple[Dict[str, str], List[str]]:
    """返回 (实际快照, 不一致键列表)。"""
    snap: Dict[str, str] = {}
    bad: List[str] = []
    want_keys = list(keys) if keys is not None else list(expected.keys())
    for k in want_keys:
        if k not in expected:
            continue
        want = _norm(expected.get(k))
        got = read_named_widget(root, k)
        snap[k] = got
        if want and not _values_equal(want, got, key=k):
            bad.append(k)
    return snap, bad


def pin_ovuf_field_memory(widgets: Optional[Dict[str, Any]]) -> int:
    """把 IOT 最终值写入本机字段记忆，避免下次 ensure 页 polish 又 restore 旧 181.7/11。"""
    payload = critical_payload(widgets)
    if not payload:
        return 0
    try:
        from utils.ui_field_helpers import history_key_for_object_name, remember_value
    except Exception:
        return 0
    n = 0
    for name, val in payload.items():
        key = history_key_for_object_name(name, memory_scope=OVUF_MEMORY_SCOPE)
        if not key:
            continue
        remember_value(key, _norm(val))
        n += 1
    return n


def apply_ovuf_critical_widgets(
    root: Any,
    widgets: Optional[Dict[str, Any]],
    *,
    log: Optional[Callable[[str], None]] = None,
    rounds: int = 2,
) -> List[str]:
    """强制写入关键 S1/S3–S6 字段并回读；返回仍不一致的键。"""
    from utils.iot_ui_handoff import apply_widget_values

    payload = critical_payload(widgets)
    if root is None:
        return ["__no_root__"]
    # widgets 有内容却抽不出任何关键键：禁止当成成功（否则会用 Dialog 旧 181.7/11 进命令）
    if not payload:
        _apply_scan_list(root, widgets)
        if isinstance(widgets, dict) and widgets:
            return ["__empty_critical__"]
        return []
    _log = log or (lambda _m: None)
    last_bad: List[str] = []
    for i in range(max(1, int(rounds))):
        apply_widget_values(root, payload)
        snap, bad = readback_mismatch(root, payload)
        _log(
            "过欠压强制写入#%d: %s"
            % (
                i + 1,
                ", ".join("%s=%r" % (k, snap.get(k)) for k in sorted(snap)[:16]),
            )
        )
        if not bad:
            pin_ovuf_field_memory(payload)
            _apply_scan_list(root, widgets)
            return []
        _log("过欠压回读不一致#%d: %s" % (i + 1, bad))
        # 只重写仍错的键
        payload = {k: payload[k] for k in bad if k in payload}
        last_bad = bad
    pin_ovuf_field_memory(widgets)
    _apply_scan_list(root, widgets)
    return last_bad


def _apply_scan_list(root: Any, widgets: Optional[Dict[str, Any]]) -> None:
    """IOT 工况表写入 Dialog。空表或没有该键时不改桌面列表，起止+步长仍有效。"""
    if root is None or not isinstance(widgets, dict):
        return
    raw = widgets.get("OVUF_SCAN_LIST_JSON")
    if raw is None:
        raw = widgets.get("ovuf_scan_list_json")
    if raw is None or raw == "" or raw == {}:
        return
    from utils.ovuf_recording import load_ovuf_scan_lists

    load_ovuf_scan_lists(root, raw)
