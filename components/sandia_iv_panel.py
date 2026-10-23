# -*- coding: utf-8 -*-
"""DC 设置页：Soft Panel Sandia 自算折叠行 → 回填 Vmp/Imp/Voc/Isc。"""
from __future__ import annotations

from typing import Any, Callable, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from utils.chroma_sandia_iv import calc_sandia_iv, sandia_inputs_from_mapping
from utils.ui_field_helpers import last_value, remember_value

_SANDIA_KEYS = (
    ("sandia.vmp", "vmp", "650"),
    ("sandia.pmax", "pmax_w", "7000"),
    ("sandia.ff", "ff", "0.85"),
    ("sandia.beta", "beta_pct_per_c", "-0.38"),
    ("sandia.irr", "irr_wm2", "1000"),
    ("sandia.irr_ref", "irr_ref_wm2", "1000"),
    ("sandia.tc", "tc_c", "50"),
    ("sandia.tc_ref", "tc_ref_c", "50"),
)


def _plain(w: Any) -> str:
    if w is None:
        return ""
    if hasattr(w, "toPlainText"):
        return str(w.toPlainText() or "").strip()
    if hasattr(w, "text"):
        return str(w.text() or "").strip()
    return ""


def _set_plain(w: Any, text: str) -> None:
    if w is None:
        return
    s = str(text)
    if hasattr(w, "setPlainText"):
        w.setPlainText(s)
    elif hasattr(w, "setText"):
        w.setText(s)


def fill_iv_widgets(ui: Any, pts: dict) -> None:
    """回填 DC Soft Panel 四点。"""
    _set_plain(getattr(ui, "textEdit_Vmp", None), f'{pts["vmp"]:g}')
    _set_plain(getattr(ui, "textEdit_Imp", None), f'{pts["imp"]:g}')
    _set_plain(getattr(ui, "textEdit_Voc", None), f'{pts["voc"]:g}')
    _set_plain(getattr(ui, "textEdit_Isc", None), f'{pts["isc"]:g}')
    remember_value("dc.vmp", f'{pts["vmp"]:g}')
    remember_value("dc.imp", f'{pts["imp"]:g}')
    remember_value("dc.voc", f'{pts["voc"]:g}')
    remember_value("dc.isc", f'{pts["isc"]:g}')


def fill_test_dialog_dc(ui_test: Any, pts: dict, *, channels: Optional[list] = None) -> None:
    """若试验 Dialog 勾了 DC 通道，同步 S1_DCn IV。"""
    if ui_test is None:
        return
    chs = channels or [1, 2, 3, 4]
    for ch in chs:
        cb = getattr(ui_test, f"checkBox_S1_DC{ch}", None)
        enabled = True
        if cb is not None:
            try:
                enabled = bool(cb.isChecked())
            except Exception:
                enabled = True
        if not enabled:
            continue
        has_any = any(
            getattr(ui_test, f"textEdit_S1_DC{ch}_{k}", None) is not None
            for k in ("VOLT", "CURR", "Voc", "Isc")
        )
        if not has_any:
            continue
        _set_plain(getattr(ui_test, f"textEdit_S1_DC{ch}_VOLT", None), f'{pts["vmp"]:g}')
        _set_plain(getattr(ui_test, f"textEdit_S1_DC{ch}_CURR", None), f'{pts["imp"]:g}')
        _set_plain(getattr(ui_test, f"textEdit_S1_DC{ch}_Voc", None), f'{pts["voc"]:g}')
        _set_plain(getattr(ui_test, f"textEdit_S1_DC{ch}_Isc", None), f'{pts["isc"]:g}')


def wire_sandia_iv_panel(
    ui: Any,
    parent: Optional[QWidget] = None,
    *,
    resolve_test_ui: Optional[Callable[[], Any]] = None,
) -> Optional[QGroupBox]:
    """在 DC1 设置页挂 Sandia 自算折叠组。可重复调用（已挂则跳过）。"""
    if ui is None:
        return None
    if getattr(ui, "_sandia_iv_panel", None) is not None:
        return ui._sandia_iv_panel

    host = parent
    if host is None:
        host = getattr(ui, "Dialog_DC1_Setting", None) or getattr(ui, "centralwidget", None)
        if host is None:
            for name in ("textEdit_Vmp", "pushButton_SendMessage", "comboBox_DC_Select"):
                w = getattr(ui, name, None)
                if w is not None:
                    host = w.window()
                    break
    if host is None:
        return None

    box = QGroupBox("Sandia 自算（对齐 Soft Panel）", host)
    box.setObjectName("groupBox_SandiaIV")
    box.setCheckable(True)
    box.setChecked(False)
    box.setToolTip("用 Irr/TC/Pmax/FF/Beta/Vmp 自算 Voc/Isc/Imp，回填后仍走现有 IVC 下发")

    form = QFormLayout()
    form.setContentsMargins(8, 8, 8, 8)
    form.setSpacing(4)

    edits: dict[str, QLineEdit] = {}
    labels = {
        "vmp": "Vmp (V)",
        "pmax_w": "Pmax (W)",
        "ff": "FF",
        "beta_pct_per_c": "Beta (%/°C)",
        "irr_wm2": "Irr (W/m²)",
        "irr_ref_wm2": "IrrRef (W/m²)",
        "tc_c": "TC (°C)",
        "tc_ref_c": "Pref TC (°C)",
    }
    for mem_key, field, default in _SANDIA_KEYS:
        le = QLineEdit()
        le.setObjectName(f"lineEdit_Sandia_{field}")
        le.setText(last_value(mem_key, default))
        le.setMaximumWidth(120)
        edits[field] = le
        form.addRow(QLabel(labels[field]), le)

    # 若 Soft Panel 已有 Vmp，优先带入
    vmp_ui = _plain(getattr(ui, "textEdit_Vmp", None))
    if vmp_ui:
        edits["vmp"].setText(vmp_ui)

    btn_row = QHBoxLayout()
    btn = QPushButton("计算并回填")
    btn.setObjectName("pushButton_SandiaCalc")
    hint = QLabel("")
    hint.setWordWrap(True)
    hint.setStyleSheet("color:#555;")
    btn_row.addWidget(btn)
    btn_row.addWidget(hint, 1)

    root = QVBoxLayout(box)
    root.addLayout(form)
    root.addLayout(btn_row)

    # 放在 IV 四点下方（绝对布局对话框）
    try:
        anchor = getattr(ui, "textEdit_PF", None) or getattr(ui, "textEdit_Imp", None)
        if anchor is not None:
            g = anchor.geometry()
            box.setGeometry(350, g.bottom() + 16, 430, 220)
        else:
            box.setGeometry(350, 230, 430, 220)
        box.show()
    except Exception:
        lay = getattr(host, "layout", lambda: None)()
        if lay is not None:
            lay.addWidget(box)
        else:
            box.setParent(host)
            box.move(350, 230)
            box.resize(430, 220)
            box.show()

    def _on_calc() -> None:
        raw = {k: edits[k].text() for k in edits}
        try:
            args = sandia_inputs_from_mapping(raw)
            pts = calc_sandia_iv(**args)
        except Exception as exc:
            QMessageBox.warning(host, "Sandia 自算", f"计算失败：{exc}")
            return
        for mem_key, field, _default in _SANDIA_KEYS:
            remember_value(mem_key, edits[field].text().strip())
        fill_iv_widgets(ui, pts)
        try:
            test_ui = resolve_test_ui() if resolve_test_ui else None
            fill_test_dialog_dc(test_ui, pts)
        except Exception:
            pass
        hint.setText(
            f"已回填 Imp={pts['imp']:g} Voc={pts['voc']:g} Isc={pts['isc']:g} Pmp={pts['pmp']:g}；开测仍走 IVC"
        )
        box.setChecked(True)

    btn.clicked.connect(_on_calc)
    ui._sandia_iv_panel = box
    ui._sandia_iv_edits = edits
    ui._sandia_iv_calc = _on_calc
    return box
