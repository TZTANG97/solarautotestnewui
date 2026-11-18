# -*- coding: utf-8 -*-
"""过欠压_过欠频：可增删的工况列表（每行独立设定值 / L1L2L3 / 保持时间）。"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from PyQt5 import QtCore, QtWidgets

COL_ENABLED = 0
COL_KIND = 1
COL_VALUE = 2
COL_L1 = 3
COL_L2 = 4
COL_L3 = 5
COL_DWELL = 6
COL_UNIT = 7

KIND_V = "电压"
KIND_F = "频率"
KIND_LABELS = (KIND_V, KIND_F)
UNITS = ("秒", "毫秒", "分钟")


def _kind_code(label: str) -> str:
    return "F" if str(label).strip() == KIND_F else "V"


def _kind_label(code: str) -> str:
    return KIND_F if str(code).strip().upper() == "F" else KIND_V


def pea_vfrt_template_rows(un_v: float) -> List[Dict[str, Any]]:
    """按额定 Un 生成 PEA 电压故障穿越示例（三相 + A-B）。"""
    try:
        un = float(un_v)
    except (TypeError, ValueError):
        un = 230.0
    if un <= 0:
        un = 230.0

    def _v(ratio: float) -> str:
        return str(round(un * ratio, 1))

    rows: List[Dict[str, Any]] = []
    # Three-phase under / over (datasheet ~p68)
    for ratio, dwell in (
        (0.90, "120"),
        (0.85, "120"),
        (0.50, "10"),
        (0.00, "0.16"),
        (1.10, "120"),
        (1.15, "120"),
        (1.20, "0.16"),
    ):
        rows.append(
            {
                "enabled": True,
                "kind": "V",
                "value": _v(ratio),
                "l1": True,
                "l2": True,
                "l3": True,
                "dwell": dwell,
                "unit": "秒",
            }
        )
    # Phase A-B faults: L3 stays at Un
    for ratio, dwell in ((0.90, "120"), (0.85, "120"), (0.50, "10")):
        rows.append(
            {
                "enabled": True,
                "kind": "V",
                "value": _v(ratio),
                "l1": True,
                "l2": True,
                "l3": False,
                "dwell": dwell,
                "unit": "秒",
            }
        )
    return rows


class OvufConditionList(QtWidgets.QWidget):
    """工况表格 + 增删移动 / PEA 示例。"""

    rows_changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ovufConditionList")
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        tip = QtWidgets.QLabel(
            "每行一个工况，可同时启用多行顺序执行。"
            "电压行：勾选相跟设定值，未勾选相保持步骤①额定（PEA 单相/两相故障）。"
            "频率行：整机改频，相勾选无效。"
            "本表有启用行时只跑列表；清空后请用顶部 ④过压～⑦欠频 的起止+步长（与以前一致）。"
            "电压行请至少勾一相（全不勾视为三相同压）。"
        )
        tip.setWordWrap(True)
        tip.setStyleSheet("color: #334155; font-size: 13px;")
        root.addWidget(tip)

        self.table = QtWidgets.QTableWidget(0, 8)
        self.table.setObjectName("tableWidget_ovuf_conditions")
        self.table.setHorizontalHeaderLabels(
            ["启用", "类型", "设定值", "L1", "L2", "L3", "保持", "单位"]
        )
        self.table.setMinimumHeight(220)
        self.table.setStyleSheet(
            "QTableWidget { background: #ffffff; color: #0f172a; gridline-color: #cbd5e1; "
            "border: 1px solid #94a3b8; font-size: 13px; }"
            "QHeaderView::section { background: #e2e8f0; color: #0f172a; padding: 6px; "
            "border: 1px solid #94a3b8; font-weight: bold; }"
            "QTableWidget::item { color: #0f172a; padding: 4px; }"
            "QTableWidget::item:selected { background: #bfdbfe; color: #0f172a; }"
        )
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table.itemChanged.connect(lambda *_: self._emit())
        root.addWidget(self.table, 1)

        btn_row = QtWidgets.QHBoxLayout()
        self.btn_add = QtWidgets.QPushButton("添加行")
        self.btn_del = QtWidgets.QPushButton("删除行")
        self.btn_up = QtWidgets.QPushButton("上移")
        self.btn_down = QtWidgets.QPushButton("下移")
        self.btn_pea = QtWidgets.QPushButton("按步骤①额定填 PEA 电压穿越示例")
        _btn_ss = (
            "QPushButton { padding: 6px 12px; font-size: 13px; font-weight: bold; "
            "color: #0f172a; background: #e2e8f0; border: 1px solid #64748b; "
            "border-radius: 4px; min-height: 28px; }"
            "QPushButton:hover { background: #cbd5e1; }"
            "QPushButton:pressed { background: #94a3b8; }"
        )
        for b in (self.btn_add, self.btn_del, self.btn_up, self.btn_down, self.btn_pea):
            b.setStyleSheet(_btn_ss)
            btn_row.addWidget(b)
        btn_row.addStretch()
        root.addLayout(btn_row)

        self.btn_add.clicked.connect(self._on_add)
        self.btn_del.clicked.connect(self._on_del)
        self.btn_up.clicked.connect(lambda: self._move_row(-1))
        self.btn_down.clicked.connect(lambda: self._move_row(1))
        self.btn_pea.clicked.connect(self._on_pea_template)
        self._un_provider = None

    def set_un_provider(self, provider) -> None:
        """provider() -> float Un from S1 rated voltage."""
        self._un_provider = provider

    def _emit(self) -> None:
        self.rows_changed.emit()

    def _make_check(self, checked: bool = True) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        lay = QtWidgets.QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setAlignment(QtCore.Qt.AlignCenter)
        cb = QtWidgets.QCheckBox()
        cb.setChecked(bool(checked))
        cb.stateChanged.connect(lambda *_: self._emit())
        lay.addWidget(cb)
        w._cb = cb  # type: ignore[attr-defined]
        return w

    def _checkbox_at(self, row: int, col: int) -> Optional[QtWidgets.QCheckBox]:
        w = self.table.cellWidget(row, col)
        if w is None:
            return None
        return getattr(w, "_cb", None)

    def _append_row(self, data: Optional[Dict[str, Any]] = None) -> None:
        d = data or {}
        r = self.table.rowCount()
        self.table.insertRow(r)

        en = self._make_check(d.get("enabled", True))
        self.table.setCellWidget(r, COL_ENABLED, en)

        kind = QtWidgets.QComboBox()
        kind.addItems(list(KIND_LABELS))
        kind.setCurrentText(_kind_label(str(d.get("kind", "V"))))
        kind.currentIndexChanged.connect(lambda *_: self._emit())
        self.table.setCellWidget(r, COL_KIND, kind)

        val = QtWidgets.QTableWidgetItem(str(d.get("value", "230")))
        self.table.setItem(r, COL_VALUE, val)

        self.table.setCellWidget(r, COL_L1, self._make_check(d.get("l1", True)))
        self.table.setCellWidget(r, COL_L2, self._make_check(d.get("l2", True)))
        self.table.setCellWidget(r, COL_L3, self._make_check(d.get("l3", True)))

        dwell = QtWidgets.QTableWidgetItem(str(d.get("dwell", "3")))
        self.table.setItem(r, COL_DWELL, dwell)

        unit = QtWidgets.QComboBox()
        unit.addItems(list(UNITS))
        unit_txt = str(d.get("unit", "秒")).strip() or "秒"
        if unit_txt not in UNITS:
            unit_txt = "秒"
        unit.setCurrentText(unit_txt)
        unit.currentIndexChanged.connect(lambda *_: self._emit())
        self.table.setCellWidget(r, COL_UNIT, unit)

    def _on_add(self) -> None:
        self._append_row()
        self._emit()

    def _on_del(self) -> None:
        r = self.table.currentRow()
        if r < 0:
            return
        self.table.removeRow(r)
        self._emit()

    def _move_row(self, delta: int) -> None:
        r = self.table.currentRow()
        if r < 0:
            return
        dest = r + delta
        if dest < 0 or dest >= self.table.rowCount():
            return
        rows = self.get_rows(include_disabled=True)
        rows[r], rows[dest] = rows[dest], rows[r]
        self.set_rows(rows)
        self.table.selectRow(dest)
        self._emit()

    def _on_pea_template(self) -> None:
        un = 230.0
        if callable(self._un_provider):
            try:
                un = float(self._un_provider())
            except Exception:
                un = 230.0
        self.set_rows(pea_vfrt_template_rows(un))
        self._emit()

    def get_rows(self, *, include_disabled: bool = False) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for r in range(self.table.rowCount()):
            en_cb = self._checkbox_at(r, COL_ENABLED)
            enabled = bool(en_cb.isChecked()) if en_cb is not None else True
            if not include_disabled and not enabled:
                continue
            kind_w = self.table.cellWidget(r, COL_KIND)
            kind_txt = kind_w.currentText() if isinstance(kind_w, QtWidgets.QComboBox) else KIND_V
            val_item = self.table.item(r, COL_VALUE)
            dwell_item = self.table.item(r, COL_DWELL)
            unit_w = self.table.cellWidget(r, COL_UNIT)
            unit_txt = unit_w.currentText() if isinstance(unit_w, QtWidgets.QComboBox) else "秒"
            l1 = self._checkbox_at(r, COL_L1)
            l2 = self._checkbox_at(r, COL_L2)
            l3 = self._checkbox_at(r, COL_L3)
            out.append(
                {
                    "enabled": enabled,
                    "kind": _kind_code(kind_txt),
                    "value": (val_item.text().strip() if val_item else "") or "230",
                    "l1": bool(l1.isChecked()) if l1 else True,
                    "l2": bool(l2.isChecked()) if l2 else True,
                    "l3": bool(l3.isChecked()) if l3 else True,
                    "dwell": (dwell_item.text().strip() if dwell_item else "") or "3",
                    "unit": unit_txt or "秒",
                }
            )
        return out

    def set_rows(self, rows: List[Dict[str, Any]]) -> None:
        self.table.blockSignals(True)
        try:
            self.table.setRowCount(0)
            for row in rows or []:
                self._append_row(row)
        finally:
            self.table.blockSignals(False)
        self._emit()

    def clear_rows(self) -> None:
        self.table.blockSignals(True)
        try:
            self.table.setRowCount(0)
        finally:
            self.table.blockSignals(False)
        self._emit()
