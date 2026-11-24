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
    """工况表格 + 增删移动 / PEA 示例。

    ``voltage_only=True`` 时只做电压穿越（隐藏频率类型），供低电压穿越复用。
    """

    rows_changed = QtCore.pyqtSignal()

    def __init__(
        self,
        parent=None,
        *,
        voltage_only: bool = False,
        locked_kind: Optional[str] = None,
        tip_text: Optional[str] = None,
        value_header: Optional[str] = None,
        default_value: str = "230",
        show_template: bool = True,
        show_phases: bool = True,
        scan_range: bool = False,
        object_name: str = "ovufConditionList",
    ):
        super().__init__(parent)
        self._scan_range = bool(scan_range)
        self._voltage_only = bool(voltage_only)
        kind_lock = str(locked_kind or "").strip().upper()
        self._locked_kind = kind_lock if kind_lock in ("V", "F") else ""
        if self._locked_kind == "V":
            self._voltage_only = True
        self._default_value = str(default_value or ("50" if self._locked_kind == "F" else "230"))
        self._show_phases = bool(show_phases)
        self.setObjectName(object_name)
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        if tip_text is not None:
            tip_msg = tip_text
        elif self._voltage_only:
            tip_msg = (
                "每行一个电压工况，可多行顺序执行。"
                "勾选相跟设定值，未勾选相保持步骤①额定（PEA 单相/两相故障）。"
                "本表有启用行时优先于上方对称时序表；清空后仍用上方 p.u. 时序。"
                "请至少勾一相（全不勾视为三相同压）。"
            )
        else:
            tip_msg = (
                "每行一个工况，可同时启用多行顺序执行。"
                "电压行：勾选相跟设定值，未勾选相保持步骤①额定（PEA 单相/两相故障）。"
                "频率行：整机改频，相勾选无效。"
                "本表有启用行时只跑列表；清空后请用顶部 ④过压～⑦欠频 的起止+步长（与以前一致）。"
                "电压行请至少勾一相（全不勾视为三相同压）。"
            )
        tip = QtWidgets.QLabel(tip_msg)
        tip.setWordWrap(True)
        tip.setStyleSheet("color: #334155; font-size: 13px;")
        root.addWidget(tip)

        if self._scan_range:
            self.table = QtWidgets.QTableWidget(0, 11)
            headers = [
                "启用",
                "电压起(V)",
                "电压止(V)",
                "频率起(Hz)",
                "频率止(Hz)",
                "步长",
                "L1",
                "L2",
                "L3",
                "每点驻留",
                "单位",
            ]
        else:
            self.table = QtWidgets.QTableWidget(0, 8)
            value_title = value_header or ("电压(V)" if self._locked_kind == "V" else "频率(Hz)" if self._locked_kind == "F" else "设定值")
            headers = ["启用", "类型", value_title, "L1", "L2", "L3", "保持", "单位"]
        self.table.setObjectName("tableWidget_ovuf_conditions")
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setMinimumHeight(220)
        self.table.setStyleSheet(
            "QTableWidget { background: #ffffff; color: #0f172a; gridline-color: #cbd5e1; "
            "border: 1px solid #94a3b8; font-size: 13px; }"
            "QHeaderView::section { background: #e2e8f0; color: #0f172a; padding: 6px; "
            "border: 1px solid #94a3b8; font-weight: bold; }"
            "QTableWidget::item { color: #0f172a; padding: 4px; }"
            "QTableWidget::item:selected { background: #bfdbfe; color: #0f172a; }"
        )
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        header.setMinimumSectionSize(36)
        self.table.verticalHeader().setDefaultSectionSize(36)
        if self._scan_range:
            # 启用、相别、单位不要跟数字列一起平分。单位列太窄时，下拉框会画出格子。
            header.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
            self.table.setColumnWidth(0, 56)
            for col, width in ((6, 44), (7, 44), (8, 44), (10, 108)):
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.Fixed)
                self.table.setColumnWidth(col, width)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        if self._scan_range:
            if not self._show_phases:
                for col in (6, 7, 8):
                    self.table.setColumnHidden(col, True)
        else:
            if self._locked_kind:
                self.table.setColumnHidden(COL_KIND, True)
            if not self._show_phases:
                for col in (COL_L1, COL_L2, COL_L3):
                    self.table.setColumnHidden(col, True)
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
        buttons = [self.btn_add, self.btn_del, self.btn_up, self.btn_down]
        if show_template:
            buttons.append(self.btn_pea)
        else:
            self.btn_pea.hide()
        for b in buttons:
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

    def _make_unit_combo(self, unit_txt: str) -> QtWidgets.QWidget:
        """单位下拉放进带边距的格子，避免按理想宽度画出单元格。"""
        unit = QtWidgets.QComboBox()
        unit.addItems(list(UNITS))
        if unit_txt not in UNITS:
            unit_txt = "秒"
        unit.setCurrentText(unit_txt)
        unit.setMinimumWidth(0)
        unit.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        unit.setStyleSheet("QComboBox { min-width: 0px; padding: 0 4px; margin: 0; }")
        unit.currentIndexChanged.connect(lambda *_: self._emit())
        host = QtWidgets.QWidget()
        lay = QtWidgets.QHBoxLayout(host)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.setSpacing(0)
        lay.addWidget(unit)
        host._unit = unit  # type: ignore[attr-defined]
        return host

    def _unit_text(self, widget) -> str:
        combo = widget
        if widget is not None and not isinstance(widget, QtWidgets.QComboBox):
            combo = getattr(widget, "_unit", None)
        if isinstance(combo, QtWidgets.QComboBox):
            return combo.currentText() or "秒"
        return "秒"

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
        if self._scan_range:
            self._append_scan_row(d)
            return
        r = self.table.rowCount()
        self.table.insertRow(r)

        en = self._make_check(d.get("enabled", True))
        self.table.setCellWidget(r, COL_ENABLED, en)

        kind = QtWidgets.QComboBox()
        if self._locked_kind:
            label = _kind_label(self._locked_kind)
            kind.addItems([label])
            kind.setCurrentText(label)
            kind.setEnabled(False)
        elif self._voltage_only:
            kind.addItems([KIND_V])
            kind.setCurrentText(KIND_V)
            kind.setEnabled(False)
        else:
            kind.addItems(list(KIND_LABELS))
            kind.setCurrentText(_kind_label(str(d.get("kind", "V"))))
        kind.currentIndexChanged.connect(lambda *_: self._emit())
        self.table.setCellWidget(r, COL_KIND, kind)

        val = QtWidgets.QTableWidgetItem(str(d.get("value", self._default_value)))
        self.table.setItem(r, COL_VALUE, val)

        self.table.setCellWidget(r, COL_L1, self._make_check(d.get("l1", True)))
        self.table.setCellWidget(r, COL_L2, self._make_check(d.get("l2", True)))
        self.table.setCellWidget(r, COL_L3, self._make_check(d.get("l3", True)))

        dwell = QtWidgets.QTableWidgetItem(str(d.get("dwell", "3")))
        self.table.setItem(r, COL_DWELL, dwell)

        self.table.setCellWidget(r, COL_UNIT, self._make_unit_combo(str(d.get("unit", "秒")).strip() or "秒"))

    def _cell_text(self, row: dict, *keys: str, default: str) -> str:
        for key in keys:
            if key in row and str(row.get(key) or "").strip():
                return str(row.get(key)).strip()
        return default

    def _append_scan_row(self, d: Dict[str, Any]) -> None:
        """一行一段扫描：电压区间、频率区间、步长、每点驻留。旧的单点 value 仍能读入。"""
        kind = self._locked_kind or "V"
        if "volt_start" in d or "freq_start" in d or "step" in d:
            volt_start = self._cell_text(d, "volt_start", default="230")
            volt_end = self._cell_text(d, "volt_end", default=volt_start)
            freq_start = self._cell_text(d, "freq_start", default="50")
            freq_end = self._cell_text(d, "freq_end", default=freq_start)
            step = self._cell_text(d, "step", default="5")
        else:
            value = self._cell_text(d, "value", default=self._default_value)
            if kind == "F":
                freq_start = freq_end = value
                volt_start = volt_end = "230"
            else:
                volt_start = volt_end = value
                freq_start = freq_end = "50"
            step = self._cell_text(d, "step", default="0")
        r = self.table.rowCount()
        self.table.insertRow(r)
        self.table.setCellWidget(r, 0, self._make_check(d.get("enabled", True)))
        for col, text in (
            (1, volt_start),
            (2, volt_end),
            (3, freq_start),
            (4, freq_end),
            (5, step),
        ):
            self.table.setItem(r, col, QtWidgets.QTableWidgetItem(text))
        self.table.setCellWidget(r, 6, self._make_check(d.get("l1", True)))
        self.table.setCellWidget(r, 7, self._make_check(d.get("l2", True)))
        self.table.setCellWidget(r, 8, self._make_check(d.get("l3", True)))
        self.table.setItem(r, 9, QtWidgets.QTableWidgetItem(self._cell_text(d, "dwell", default="3")))
        unit = self._make_unit_combo(str(d.get("unit", "秒")).strip() or "秒")
        self.table.setCellWidget(r, 10, unit)

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

    def _item_text(self, row: int, col: int, default: str) -> str:
        item = self.table.item(row, col)
        text = item.text().strip() if item is not None else ""
        return text or default

    def get_rows(self, *, include_disabled: bool = False) -> List[Dict[str, Any]]:
        if self._scan_range:
            return self._scan_rows(include_disabled=include_disabled)
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
            unit_txt = self._unit_text(self.table.cellWidget(r, COL_UNIT))
            l1 = self._checkbox_at(r, COL_L1)
            l2 = self._checkbox_at(r, COL_L2)
            l3 = self._checkbox_at(r, COL_L3)
            out.append(
                {
                    "enabled": enabled,
                    "kind": self._locked_kind or _kind_code(kind_txt),
                    "value": (val_item.text().strip() if val_item else "") or self._default_value,
                    "l1": bool(l1.isChecked()) if l1 else True,
                    "l2": bool(l2.isChecked()) if l2 else True,
                    "l3": bool(l3.isChecked()) if l3 else True,
                    "dwell": (dwell_item.text().strip() if dwell_item else "") or "3",
                    "unit": unit_txt or "秒",
                }
            )
        return out

    def _scan_rows(self, *, include_disabled: bool = False) -> List[Dict[str, Any]]:
        kind = self._locked_kind or "V"
        out: List[Dict[str, Any]] = []
        for r in range(self.table.rowCount()):
            en_cb = self._checkbox_at(r, 0)
            enabled = bool(en_cb.isChecked()) if en_cb is not None else True
            if not include_disabled and not enabled:
                continue
            volt_start = self._item_text(r, 1, "230")
            volt_end = self._item_text(r, 2, volt_start)
            freq_start = self._item_text(r, 3, "50")
            freq_end = self._item_text(r, 4, freq_start)
            l1 = self._checkbox_at(r, 6)
            l2 = self._checkbox_at(r, 7)
            l3 = self._checkbox_at(r, 8)
            unit_txt = self._unit_text(self.table.cellWidget(r, 10))
            primary_end = freq_end if kind == "F" else volt_end
            out.append(
                {
                    "enabled": enabled,
                    "kind": kind,
                    "volt_start": volt_start,
                    "volt_end": volt_end,
                    "freq_start": freq_start,
                    "freq_end": freq_end,
                    "step": self._item_text(r, 5, "5"),
                    "value": primary_end,
                    "l1": bool(l1.isChecked()) if l1 else True,
                    "l2": bool(l2.isChecked()) if l2 else True,
                    "l3": bool(l3.isChecked()) if l3 else True,
                    "dwell": self._item_text(r, 9, "3"),
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
