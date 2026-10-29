# -*- coding: utf-8 -*-
"""DC1 Chroma 页：Soft Panel Sandia 自算 → 回填 Vmp/Imp/Voc/Isc。

必须挂在 DC1 嵌入页（IV 控件父级 / Timeline），禁止挂主窗口，否则会跨页浮窗且关不掉。
"""
from __future__ import annotations

from typing import Any, Callable, Optional

from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
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
    ("sandia.power_pct", "power_pct", "100"),
)

_PANEL_QSS = """
QGroupBox#groupBox_SandiaIV {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    margin-top: 10px;
    padding: 14px 12px 12px 12px;
    font-size: 13px;
    font-weight: 600;
    color: #1e293b;
}
QGroupBox#groupBox_SandiaIV::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    background-color: #ffffff;
}
QGroupBox#groupBox_SandiaIV QLabel {
    color: #334155;
    font-size: 13px;
    font-weight: 500;
    background: transparent;
    min-width: 110px;
}
QGroupBox#groupBox_SandiaIV QLineEdit {
    color: #0f172a;
    background-color: #ffffff;
    border: 1px solid #94a3b8;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 14px;
    min-height: 32px;
    min-width: 140px;
}
QGroupBox#groupBox_SandiaIV QPushButton {
    color: #1e293b;
    background-color: #e2e8f0;
    border: 1px solid #94a3b8;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 13px;
    min-height: 34px;
}
QGroupBox#groupBox_SandiaIV QPushButton:hover {
    background-color: #cbd5e1;
}
"""


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


def _find_timeline(start: Optional[QWidget]) -> Optional[QWidget]:
    cur = start
    depth = 0
    while cur is not None and depth < 24:
        if cur.__class__.__name__ == "TimelineWidget" or callable(getattr(cur, "addStep", None)):
            return cur
        cur = cur.parentWidget()
        depth += 1
    return None


def _resolve_embed_host(ui: Any, parent: Optional[QWidget]) -> Optional[QWidget]:
    """解析 DC1 嵌入内容宿主。禁止用 .window()（会落到主窗，造成跨页浮窗）。"""
    if parent is not None:
        return parent
    for name in ("textEdit_Vmp", "textEdit_Imp", "textEdit_Voc", "pushButton_SendMessage"):
        w = getattr(ui, name, None)
        if w is None:
            continue
        p = w.parentWidget()
        if p is not None:
            return p
    return None


def _is_orphan_float(panel: QWidget, host: Optional[QWidget]) -> bool:
    """旧版把面板挂到主窗：parent 是顶层窗，且不在 DC1 host 子树内。"""
    if panel is None:
        return False
    try:
        p = panel.parentWidget()
        if p is None:
            return True
        if host is not None:
            cur = panel
            while cur is not None:
                if cur is host:
                    return False
                cur = cur.parentWidget()
            return True
        # 无 host 时：直接子挂在 QMainWindow / 无名顶层窗上视为孤儿
        return p.parentWidget() is None and p is panel.window()
    except Exception:
        return True


def _destroy_widget(w: Optional[QWidget]) -> None:
    if w is None:
        return
    try:
        w.hide()
        w.setParent(None)
        w.deleteLater()
    except Exception:
        pass


def purge_orphan_sandia_panels(ui: Optional[Any] = None) -> int:
    """清理误挂主窗的 Sandia 浮窗（含上一版遗留）。"""
    removed = 0
    host = _resolve_embed_host(ui, None) if ui is not None else None
    app = QApplication.instance()
    if app is None:
        return 0
    for w in list(app.allWidgets()):
        try:
            if w is None or w.objectName() != "groupBox_SandiaIV":
                continue
            if _is_orphan_float(w, host):
                _destroy_widget(w)
                removed += 1
        except Exception:
            continue
    if ui is not None and removed:
        ui._sandia_iv_panel = None
        ui._sandia_iv_edits = None
        ui._sandia_iv_calc = None
    return removed


def _destroy_panel(ui: Any) -> None:
    old = getattr(ui, "_sandia_iv_panel", None)
    _destroy_widget(old)
    ui._sandia_iv_panel = None
    ui._sandia_iv_edits = None
    ui._sandia_iv_calc = None


def wire_sandia_iv_panel(
    ui: Any,
    parent: Optional[QWidget] = None,
    *,
    resolve_test_ui: Optional[Callable[[], Any]] = None,
    force: bool = False,
) -> Optional[QWidget]:
    """在 DC1 Chroma 嵌入页挂 Sandia 自算区。"""
    if ui is None:
        return None

    host = _resolve_embed_host(ui, parent)
    purge_orphan_sandia_panels(ui)

    existing = getattr(ui, "_sandia_iv_panel", None)
    if existing is not None and not force and not _is_orphan_float(existing, host):
        return existing
    if existing is not None:
        _destroy_panel(ui)

    if host is None:
        return None

    labels = {
        "vmp": "Vmp (V)",
        "pmax_w": "Pmax (W)",
        "ff": "FF",
        "beta_pct_per_c": "Beta (%/°C)",
        "irr_wm2": "Irr (W/m²)",
        "irr_ref_wm2": "IrrRef (W/m²)",
        "tc_c": "TC (°C)",
        "tc_ref_c": "Tref (°C)",
        "power_pct": "功率% (Power Level)",
    }

    content = QWidget()
    content.setObjectName("sandia_iv_content")
    content.setStyleSheet("background: transparent;")
    grid = QGridLayout(content)
    grid.setContentsMargins(4, 4, 4, 4)
    grid.setHorizontalSpacing(16)
    grid.setVerticalSpacing(10)

    edits: dict[str, QLineEdit] = {}
    for i, (mem_key, field, default) in enumerate(_SANDIA_KEYS):
        le = QLineEdit()
        le.setObjectName(f"lineEdit_Sandia_{field}")
        le.setText(last_value(mem_key, default))
        le.setMinimumHeight(32)
        le.setMinimumWidth(140)
        le.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        edits[field] = le
        row, col = divmod(i, 2)
        grid.addWidget(QLabel(labels[field]), row, col * 2)
        grid.addWidget(le, row, col * 2 + 1)

    vmp_ui = _plain(getattr(ui, "textEdit_Vmp", None))
    if vmp_ui:
        edits["vmp"].setText(vmp_ui)

    btn = QPushButton("计算并回填")
    btn.setObjectName("pushButton_SandiaCalc")
    btn_hide = QPushButton("收起")
    btn_hide.setObjectName("pushButton_SandiaHide")
    btn_hide.setToolTip("收起面板（仅隐藏本 DC1 页内区域）")
    hint = QLabel("")
    hint.setWordWrap(True)
    hint.setStyleSheet("color:#475569; font-size:12px; font-weight:400;")

    btn_row = QHBoxLayout()
    btn_row.addWidget(btn)
    btn_row.addWidget(btn_hide)
    btn_row.addWidget(hint, 1)

    box = QGroupBox("Sandia 自算（对齐 Soft Panel）")
    box.setObjectName("groupBox_SandiaIV")
    box.setCheckable(True)
    box.setChecked(True)
    box.setToolTip("用 Irr/TC/Pmax/FF/Beta/Vmp 自算 Voc/Isc/Imp，回填后仍走现有 IVC 下发")
    box.setStyleSheet(_PANEL_QSS)
    box.setMinimumWidth(520)
    box.setMinimumHeight(260)
    box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    root = QVBoxLayout(box)
    root.setContentsMargins(10, 18, 10, 10)
    root.setSpacing(8)
    root.addWidget(content)
    root.addLayout(btn_row)

    def _on_toggled(on: bool) -> None:
        content.setVisible(on)
        btn.setVisible(on)
        btn_hide.setVisible(on)
        hint.setVisible(on)

    box.toggled.connect(_on_toggled)
    btn_hide.clicked.connect(lambda: box.setChecked(False))

    def _on_calc() -> None:
        raw = {k: edits[k].text() for k in edits}
        try:
            args = sandia_inputs_from_mapping(raw)
            pts = calc_sandia_iv(**args)
        except Exception as exc:
            QMessageBox.warning(box, "Sandia 自算", f"计算失败：{exc}")
            return
        for mem_key, field, _default in _SANDIA_KEYS:
            remember_value(mem_key, edits[field].text().strip())
        fill_iv_widgets(ui, pts)
        # 电流已按功率%缩放时，通道功率%置 100，避免 IVC 下发再乘一次。
        # 功率%本就是 100 时不动原有功率档，后面的工况点仍按自己的百分比缩放这组四点。
        scaled = abs(float(pts.get("power_pct") or 100) - 100.0) > 1e-6
        if scaled:
            _set_plain(getattr(ui, "textEdit_PF", None), "100")
        try:
            test_ui = resolve_test_ui() if resolve_test_ui else None
            fill_test_dialog_dc(test_ui, pts)
            if scaled and test_ui is not None:
                for ch in (1, 2, 3, 4):
                    cb = getattr(test_ui, f"checkBox_S1_DC{ch}", None)
                    enabled = True
                    if cb is not None:
                        try:
                            enabled = bool(cb.isChecked())
                        except Exception:
                            enabled = True
                    if enabled:
                        _set_plain(getattr(test_ui, f"textEdit_S1_DC{ch}_PF", None), "100")
        except Exception:
            pass
        extra = "；功率%已置 100，避免下发再乘" if scaled else ""
        hint.setText(
            f"已按功率 {pts.get('power_pct', 100):g}% 回填 "
            f"Imp={pts['imp']:g} Voc={pts['voc']:g} Isc={pts['isc']:g} "
            f"Pmp={pts['pmp']:g}{extra}"
        )
        box.setChecked(True)

    btn.clicked.connect(_on_calc)

    placed = False
    timeline = _find_timeline(host)
    if timeline is not None and callable(getattr(timeline, "addStep", None)):
        try:
            # 时间线步骤已有标题，GroupBox 不再重复大标题
            box.setTitle("展开 / 收起")
            timeline.addStep("Sandia 自算（对齐 Soft Panel）", box)
            try:
                timeline.finalize()
            except Exception:
                pass
            placed = True
        except Exception:
            placed = False

    if not placed:
        lay = host.layout()
        if lay is not None:
            lay.addWidget(box)
        else:
            box.setParent(host)
            box.move(8, max(8, int(getattr(host, "height", lambda: 240)()) - 300))
            box.resize(max(520, int(getattr(host, "width", lambda: 560)()) - 24), 300)
        box.show()

    ui._sandia_iv_panel = box
    ui._sandia_iv_edits = edits
    ui._sandia_iv_calc = _on_calc
    return box
