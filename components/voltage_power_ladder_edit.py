# -*- coding: utf-8 -*-
"""电压 Un% + 功率 Pn% 同行一张表（替代左右两张阶梯表）。"""

from __future__ import annotations

import re

from PyQt5 import QtCore, QtGui, QtWidgets

_ROW_H = 30
_TOOLBAR_H = 36
_HDR_H = 28


def _split_segments(raw: str) -> list:
    return [part.strip() for part in re.split(r"[,，\s]+", str(raw or "")) if part.strip()]


class _CsvColumnProxy(QtWidgets.QWidget):
    """兼容 QTextEdit / CommaSegmentEdit：toPlainText / setText / setObjectName。

    做成隐藏 QWidget，便于 iot_widget_export / handoff 按控件采集。
    """

    textChanged = QtCore.pyqtSignal()

    def __init__(self, owner: "VoltagePowerLadderEdit", kind: str):
        super().__init__(owner)
        self._owner = owner
        self._kind = kind  # "voltage" | "power"
        self.setMaximumSize(0, 0)
        self.hide()

    def toPlainText(self) -> str:
        return self._owner.csv_for(self._kind)

    def setText(self, text: str) -> None:
        self.setPlainText(text)

    def setPlainText(self, text: str) -> None:
        self._owner.set_csv(self._kind, text)

    def setPlaceholderText(self, text: str) -> None:
        self._owner.set_placeholder(self._kind, text)


class VoltagePowerLadderEdit(QtWidgets.QWidget):
    """
    一表两列：# | 电压 Un% | 功率 Pn%。
    对外仍暴露 .voltage / .power（逗号串 API），供 Send / 存盘沿用。
    """

    changed = QtCore.pyqtSignal()

    def __init__(
        self,
        parent=None,
        *,
        default_power: str = "100",
        visible_rows: int = 14,
        voltage_header: str = "电压 Un%",
        power_header: str = "功率 Pn%",
    ):
        super().__init__(parent)
        self._default_power = str(default_power or "100").strip() or "100"
        self._visible_rows = max(6, int(visible_rows))
        self._block = False
        self._ph_voltage = "Un%"
        self._ph_power = "开测功率%"
        self.setMinimumWidth(420)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(6)

        self._table = QtWidgets.QTableWidget(0, 3)
        self._table.setObjectName("voltagePowerLadderTable")
        self._table.setHorizontalHeaderLabels(
            ["#", f"{voltage_header} (%)", f"{power_header} (%)"]
        )
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self._table.setAlternatingRowColors(True)
        self._table.setShowGrid(True)
        self._table.setWordWrap(False)
        hdr = self._table.horizontalHeader()
        hdr.setStretchLastSection(True)
        hdr.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        hdr.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        hdr.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self._table.setColumnWidth(0, 44)
        self._table.verticalHeader().setDefaultSectionSize(_ROW_H)
        self._table.setStyleSheet(
            "QTableWidget { border: 1px solid #cbd5e1; border-radius: 4px; "
            "background: #ffffff; gridline-color: #e2e8f0; font-size: 13px; }"
            "QHeaderView::section { background: #f8fafc; color: #334155; "
            "border: none; border-bottom: 1px solid #e2e8f0; border-right: 1px solid #e2e8f0; "
            "padding: 5px 8px; font-weight: 600; font-size: 12px; }"
            "QTableWidget::item:selected { background: #e0e7ff; color: #1e293b; }"
        )
        self._table.itemChanged.connect(self._on_item_changed)
        root.addWidget(self._table, 1)

        bar = QtWidgets.QHBoxLayout()
        bar.setContentsMargins(0, 0, 0, 0)
        bar.setSpacing(6)
        self._btn_add = QtWidgets.QPushButton("添加")
        self._btn_add.setCursor(QtCore.Qt.PointingHandCursor)
        self._btn_add.clicked.connect(self._add_row)
        self._btn_del = QtWidgets.QPushButton("删除选中")
        self._btn_del.setCursor(QtCore.Qt.PointingHandCursor)
        self._btn_del.clicked.connect(self._remove_selected)
        self._btn_fill = QtWidgets.QPushButton("功率填默认")
        self._btn_fill.setToolTip(f"把空功率或全部功率填成开测默认 {self._default_power}%")
        self._btn_fill.setCursor(QtCore.Qt.PointingHandCursor)
        self._btn_fill.clicked.connect(self._fill_default_power)
        self._btn_paste = QtWidgets.QPushButton("粘贴电压")
        self._btn_paste.setToolTip("粘贴逗号分隔电压 list；功率自动填开测默认值")
        self._btn_paste.setCursor(QtCore.Qt.PointingHandCursor)
        self._btn_paste.clicked.connect(self._paste_voltage)
        for btn in (self._btn_add, self._btn_del, self._btn_fill, self._btn_paste):
            btn.setFixedHeight(28)
            btn.setStyleSheet(
                "QPushButton { background: #fff; color: #0f172a; border: 1px solid #cbd5e1; "
                "border-radius: 4px; font-size: 12px; padding: 0 10px; }"
                "QPushButton:hover { background: #f1f5f9; }"
            )
        self._count = QtWidgets.QLabel("0 点")
        self._count.setStyleSheet("color: #64748b; font-size: 12px;")
        bar.addWidget(self._btn_add)
        bar.addWidget(self._btn_del)
        bar.addWidget(self._btn_fill)
        bar.addWidget(self._btn_paste)
        bar.addStretch(1)
        bar.addWidget(self._count)
        root.addLayout(bar)

        tip = QtWidgets.QLabel(
            f"同一行：电压 + 对应功率。功率默认 {self._default_power}%（开测功率），可按行改；"
            "留空也按开测功率。"
        )
        tip.setWordWrap(True)
        tip.setStyleSheet("color:#64748b;font-size:11px;")
        root.addWidget(tip)

        self.voltage = _CsvColumnProxy(self, "voltage")
        self.power = _CsvColumnProxy(self, "power")
        self.set_pairs([("100", self._default_power)])

    def set_default_power(self, pct: str) -> None:
        self._default_power = str(pct or "100").strip() or "100"
        self._btn_fill.setToolTip(f"把空功率或全部功率填成开测默认 {self._default_power}%")

    def set_placeholder(self, kind: str, text: str) -> None:
        if kind == "voltage":
            self._ph_voltage = str(text or "")
        else:
            self._ph_power = str(text or "")

    def csv_for(self, kind: str) -> str:
        col = 1 if kind == "voltage" else 2
        parts = []
        for row in range(self._table.rowCount()):
            item = self._table.item(row, col)
            text = (item.text() if item else "").strip()
            if kind == "voltage":
                if text:
                    parts.append(text)
            else:
                # 功率与电压行对齐：电压有值才输出功率（空→默认）
                v_item = self._table.item(row, 1)
                v_text = (v_item.text() if v_item else "").strip()
                if not v_text:
                    continue
                parts.append(text if text else self._default_power)
        return ",".join(parts)

    def set_csv(self, kind: str, text: str) -> None:
        parts = _split_segments(text)
        if kind == "voltage":
            powers = _split_segments(self.csv_for("power"))
            if len(powers) == 1 and len(parts) > 1:
                powers = [powers[0]] * len(parts)
            while len(powers) < len(parts):
                powers.append(self._default_power)
            pairs = [
                (parts[i], powers[i] if i < len(powers) else self._default_power)
                for i in range(len(parts))
            ] or [("", self._default_power)]
            self.set_pairs(pairs)
            return
        # power only
        voltages = _split_segments(self.csv_for("voltage"))
        if not voltages and not parts:
            self.set_pairs([("", self._default_power)])
            return
        if not voltages:
            voltages = [""] * max(1, len(parts))
        if len(parts) == 1 and len(voltages) > 1:
            parts = [parts[0]] * len(voltages)
        while len(parts) < len(voltages):
            parts.append(self._default_power)
        pairs = [
            (voltages[i], parts[i] if i < len(parts) else self._default_power)
            for i in range(len(voltages))
        ]
        self.set_pairs(pairs)

    def set_pairs(self, pairs) -> None:
        self._block = True
        try:
            self._table.setRowCount(0)
            if not pairs:
                pairs = [("", self._default_power)]
            for volt, pwr in pairs:
                self._append_row(str(volt or ""), str(pwr or self._default_power))
            self._refresh_meta()
        finally:
            self._block = False
        self.voltage.textChanged.emit()
        self.power.textChanged.emit()
        self.changed.emit()

    def _append_row(self, voltage: str = "", power: str = "") -> None:
        row = self._table.rowCount()
        self._table.insertRow(row)
        index = QtWidgets.QTableWidgetItem(str(row + 1))
        index.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        index.setTextAlignment(QtCore.Qt.AlignCenter)
        index.setForeground(QtGui.QBrush(QtGui.QColor("#64748b")))
        self._table.setItem(row, 0, index)
        for col, value, ph in (
            (1, voltage, self._ph_voltage),
            (2, power if str(power).strip() else self._default_power, self._ph_power),
        ):
            cell = QtWidgets.QTableWidgetItem(str(value))
            cell.setFlags(
                QtCore.Qt.ItemIsEnabled
                | QtCore.Qt.ItemIsSelectable
                | QtCore.Qt.ItemIsEditable
            )
            if ph:
                cell.setToolTip(ph)
            self._table.setItem(row, col, cell)

    def _renumber(self) -> None:
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 0)
            if item is None:
                item = QtWidgets.QTableWidgetItem()
                item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                item.setForeground(QtGui.QBrush(QtGui.QColor("#64748b")))
                self._table.setItem(row, 0, item)
            item.setText(str(row + 1))

    def _refresh_meta(self) -> None:
        filled = len(_split_segments(self.csv_for("voltage")))
        total = self._table.rowCount()
        self._count.setText(f"{filled} 点" if filled == total else f"{filled}/{total} 点")
        # 最小高度保证看得见几行；实际高度交给外层 QSplitter 拖拽
        rows = max(4, min(8, max(total, 1)))
        height = _HDR_H + rows * _ROW_H + 6
        self._table.setMinimumHeight(height)
        self._table.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.setMinimumHeight(height + _TOOLBAR_H + 28)

    def _on_item_changed(self, _item) -> None:
        if self._block:
            return
        self._refresh_meta()
        self.voltage.textChanged.emit()
        self.power.textChanged.emit()
        self.changed.emit()

    def _add_row(self) -> None:
        self._block = True
        try:
            self._append_row("", self._default_power)
            self._renumber()
            self._refresh_meta()
        finally:
            self._block = False
        last = self._table.rowCount() - 1
        self._table.setCurrentCell(last, 1)
        self._table.editItem(self._table.item(last, 1))
        self.voltage.textChanged.emit()
        self.power.textChanged.emit()
        self.changed.emit()

    def _remove_selected(self) -> None:
        rows = sorted({index.row() for index in self._table.selectedIndexes()}, reverse=True)
        if not rows:
            current = self._table.currentRow()
            if current >= 0:
                rows = [current]
        if not rows:
            return
        self._block = True
        try:
            for row in rows:
                self._table.removeRow(row)
            if self._table.rowCount() == 0:
                self._append_row("", self._default_power)
            self._renumber()
            self._refresh_meta()
        finally:
            self._block = False
        self.voltage.textChanged.emit()
        self.power.textChanged.emit()
        self.changed.emit()

    def _fill_default_power(self) -> None:
        self._block = True
        try:
            for row in range(self._table.rowCount()):
                item = self._table.item(row, 2)
                if item is None:
                    item = QtWidgets.QTableWidgetItem(self._default_power)
                    self._table.setItem(row, 2, item)
                else:
                    item.setText(self._default_power)
            self._refresh_meta()
        finally:
            self._block = False
        self.power.textChanged.emit()
        self.changed.emit()

    def _paste_voltage(self) -> None:
        text = QtWidgets.QApplication.clipboard().text()
        parts = _split_segments(text)
        if not parts:
            return
        self.set_csv("voltage", ",".join(parts))
