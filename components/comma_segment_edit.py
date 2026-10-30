# -*- coding: utf-8 -*-
"""逗号阶梯：表格逐行填写，读写仍是逗号串（兼容 QTextEdit API）。"""

from __future__ import annotations

import re

from PyQt5 import QtCore, QtGui, QtWidgets

_ROW_H = 28
_VISIBLE_ROWS = 8
_TOOLBAR_H = 34
_HDR_H = 26


def _split_segments(raw: str) -> list:
    return [part.strip() for part in re.split(r"[,，\s]+", str(raw or "")) if part.strip()]


class CommaSegmentEdit(QtWidgets.QWidget):
    """兼容原来的 QTextEdit：toPlainText / setText / setPlainText / textChanged。"""

    textChanged = QtCore.pyqtSignal()

    def __init__(self, parent=None, *, value_header: str = "数值", unit: str = ""):
        super().__init__(parent)
        self._placeholder = "填写"
        self._value_header = str(value_header or "数值")
        self._unit = str(unit or "")
        self._block = False
        self.setMinimumWidth(220)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(6)

        self._table = QtWidgets.QTableWidget(0, 2)
        self._table.setObjectName("commaSegmentTable")
        self._table.setHorizontalHeaderLabels(["#", self._header_text()])
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self._table.setAlternatingRowColors(True)
        self._table.setShowGrid(True)
        self._table.setWordWrap(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        self._table.setColumnWidth(0, 40)
        self._table.verticalHeader().setDefaultSectionSize(_ROW_H)
        self._table.setStyleSheet(
            "QTableWidget { border: 1px solid #cbd5e1; border-radius: 4px; "
            "background: #ffffff; gridline-color: #e2e8f0; font-size: 12px; }"
            "QHeaderView::section { background: #f8fafc; color: #334155; "
            "border: none; border-bottom: 1px solid #e2e8f0; border-right: 1px solid #e2e8f0; "
            "padding: 4px 6px; font-weight: 600; }"
            "QTableWidget::item:selected { background: #e0e7ff; color: #1e293b; }"
        )
        self._table.itemChanged.connect(self._on_item_changed)
        root.addWidget(self._table)

        bar = QtWidgets.QHBoxLayout()
        bar.setContentsMargins(0, 0, 0, 0)
        bar.setSpacing(6)
        self._btn_add = QtWidgets.QPushButton("添加")
        self._btn_add.setObjectName("btnAddSegment")
        self._btn_add.setCursor(QtCore.Qt.PointingHandCursor)
        self._btn_add.clicked.connect(self._add_row)
        self._btn_del = QtWidgets.QPushButton("删除选中")
        self._btn_del.setObjectName("btnRemoveSegment")
        self._btn_del.setCursor(QtCore.Qt.PointingHandCursor)
        self._btn_del.clicked.connect(self._remove_selected)
        self._btn_paste = QtWidgets.QPushButton("粘贴名单")
        self._btn_paste.setToolTip("从剪贴板粘贴逗号/空格分隔的名单，替换当前内容")
        self._btn_paste.setCursor(QtCore.Qt.PointingHandCursor)
        self._btn_paste.clicked.connect(self._paste_list)
        for btn in (self._btn_add, self._btn_del, self._btn_paste):
            btn.setFixedHeight(26)
            btn.setStyleSheet(
                "QPushButton { background: #fff; color: #0f172a; border: 1px solid #cbd5e1; "
                "border-radius: 4px; font-size: 12px; padding: 0 10px; }"
                "QPushButton:hover { background: #f1f5f9; }"
            )
        self._count = QtWidgets.QLabel("0 点")
        self._count.setStyleSheet("color: #64748b; font-size: 12px;")
        bar.addWidget(self._btn_add)
        bar.addWidget(self._btn_del)
        bar.addWidget(self._btn_paste)
        bar.addStretch(1)
        bar.addWidget(self._count)
        root.addLayout(bar)

        self.setPlainText("")

    def setValueHeader(self, text: str, unit: str = "") -> None:
        self._value_header = str(text or "数值")
        self._unit = str(unit or "")
        self._table.setHorizontalHeaderLabels(["#", self._header_text()])

    def _header_text(self) -> str:
        if self._unit:
            return f"{self._value_header} ({self._unit})"
        return self._value_header

    def setPlaceholderText(self, text: str) -> None:
        self._placeholder = str(text or "")

    def toPlainText(self) -> str:
        parts = []
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 1)
            text = (item.text() if item else "").strip()
            if text:
                parts.append(text)
        return ",".join(parts)

    def setText(self, text: str) -> None:
        self.setPlainText(text)

    def setPlainText(self, text: str) -> None:
        parts = _split_segments(text)
        self._rebuild(parts)

    def _rebuild(self, parts) -> None:
        self._block = True
        try:
            self._table.setRowCount(0)
            if not parts:
                parts = [""]
            for value in parts:
                self._append_row(value)
            self._refresh_meta()
        finally:
            self._block = False
        self.textChanged.emit()

    def _append_row(self, value: str = "") -> None:
        row = self._table.rowCount()
        self._table.insertRow(row)
        index = QtWidgets.QTableWidgetItem(str(row + 1))
        index.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        index.setTextAlignment(QtCore.Qt.AlignCenter)
        index.setForeground(QtGui.QBrush(QtGui.QColor("#64748b")))
        self._table.setItem(row, 0, index)
        cell = QtWidgets.QTableWidgetItem(str(value))
        cell.setFlags(
            QtCore.Qt.ItemIsEnabled
            | QtCore.Qt.ItemIsSelectable
            | QtCore.Qt.ItemIsEditable
        )
        if not str(value).strip() and self._placeholder:
            cell.setToolTip(self._placeholder)
        self._table.setItem(row, 1, cell)

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
        filled = len([p for p in self.toPlainText().split(",") if p]) if self.toPlainText() else 0
        total = self._table.rowCount()
        self._count.setText(f"{filled} 点" if filled == total else f"{filled}/{total} 点")
        rows = max(1, min(_VISIBLE_ROWS, max(total, 1)))
        height = _HDR_H + rows * _ROW_H + 4
        self._table.setFixedHeight(height)
        self.setMinimumHeight(height + _TOOLBAR_H)

    def _on_item_changed(self, _item) -> None:
        if self._block:
            return
        self._refresh_meta()
        self.textChanged.emit()

    def _add_row(self) -> None:
        self._block = True
        try:
            self._append_row("")
            self._renumber()
            self._refresh_meta()
        finally:
            self._block = False
        self._table.setCurrentCell(self._table.rowCount() - 1, 1)
        self._table.editItem(self._table.item(self._table.rowCount() - 1, 1))
        self.textChanged.emit()

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
                self._append_row("")
            self._renumber()
            self._refresh_meta()
        finally:
            self._block = False
        self.textChanged.emit()

    def _paste_list(self) -> None:
        text = QtWidgets.QApplication.clipboard().text()
        parts = _split_segments(text)
        if not parts:
            return
        self.setPlainText(",".join(parts))
