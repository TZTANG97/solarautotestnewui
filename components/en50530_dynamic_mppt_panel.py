# -*- coding: utf-8 -*-
"""Chroma-style EN50530 table editor for dynamic MPPT."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from PyQt5 import QtCore, QtGui, QtWidgets

from utils.en50530_dynamic_mppt import (
    EN50530_TABS,
    apply_softpanel_ramp_times,
    default_en50530_bundle,
    estimate_en50530_total_duration_s,
    row_cycle_duration_s,
    validate_en50530_bundle,
)

_COLUMNS = (
    ("enabled", "Enable"),
    ("repetitions", "Repetitions"),
    ("slope_wm2_s", "Slope (W/m²/s)"),
    ("ramp_up_s", "Ramp UP (S)"),
    ("dwell_up_s", "Dwell Time (S)"),
    ("ramp_dn_s", "Ramp DN (S)"),
    ("dwell_dn_s", "Dwell Time (S)"),
    ("duration_s", "Duration (S)"),
)

_EDITABLE_KEYS = {
    "repetitions",
    "slope_wm2_s",
    "dwell_up_s",
    "dwell_dn_s",
}

_RAMP_KEYS = {"ramp_up_s", "ramp_dn_s"}


class En50530DynamicMpptPanel(QtWidgets.QWidget):
    """Layout aligned with Chroma Dynamic MPPT Test Panel parameter area."""

    profile_changed = QtCore.pyqtSignal()

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("en50530DynamicMpptPanel")
        self._loading = False
        self._tables: Dict[str, QtWidgets.QTableWidget] = {}
        self._table_tab_id: Dict[QtWidgets.QTableWidget, str] = {}

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        stc_group = QtWidgets.QGroupBox("Test Setup（与 Chroma 左栏一致；IV 以本栏为准）")
        stc_group.setStyleSheet(
            "QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px;"
            " margin-top: 8px; padding-top: 10px; font-weight: bold; }"
        )
        stc_grid = QtWidgets.QGridLayout(stc_group)
        self.textEdit_S3_initial_setup_s = self._line_edit("textEdit_S3_initial_setup_s", "300")
        self.textEdit_S3_vmp = self._line_edit("textEdit_S3_vmp", "100.0")
        self.textEdit_S3_pmpp = self._line_edit("textEdit_S3_pmpp", "600.0")
        self.comboBox_S3_ff = QtWidgets.QComboBox()
        self.comboBox_S3_ff.setObjectName("comboBox_S3_ff")
        self.comboBox_S3_ff.addItems(["c-Si", "a-Si", "Thin Film"])
        stc_grid.addWidget(QtWidgets.QLabel("Initial Setup Time (S)"), 0, 0)
        stc_grid.addWidget(self.textEdit_S3_initial_setup_s, 0, 1)
        stc_grid.addWidget(QtWidgets.QLabel("Vmp (V)"), 1, 0)
        stc_grid.addWidget(self.textEdit_S3_vmp, 1, 1)
        stc_grid.addWidget(QtWidgets.QLabel("Pmpp (W)"), 2, 0)
        stc_grid.addWidget(self.textEdit_S3_pmpp, 2, 1)
        stc_grid.addWidget(QtWidgets.QLabel("FF"), 3, 0)
        stc_grid.addWidget(self.comboBox_S3_ff, 3, 1)
        root.addWidget(stc_group)

        hint = QtWidgets.QLabel(
            "对齐 Chroma SoftPanel：全带宽 Gmin↔Gmax；Ramp=(Gmax−Gmin)/Slope 自动联动；"
            "启机后从 Gmax 先 DN 再 UP。仅执行当前页签 Enable 行。"
            "默认表为 EN50530 SoftPanel 标准斜率（总时长很长，可按需取消勾选）。"
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #64748b; font-weight: normal;")
        root.addWidget(hint)

        self.tabWidget_EN50530 = QtWidgets.QTabWidget()
        self.tabWidget_EN50530.setObjectName("tabWidget_EN50530")
        bundle = default_en50530_bundle()
        for tab_id, tab_label in EN50530_TABS:
            page = QtWidgets.QWidget()
            page_layout = QtWidgets.QVBoxLayout(page)
            table = self._make_table(tab_id)
            self._set_table_rows(table, bundle.tabs.get(tab_id) or [])
            page_layout.addWidget(table)
            toolbar = QtWidgets.QHBoxLayout()
            add_btn = QtWidgets.QPushButton("新增行")
            add_btn.clicked.connect(lambda _=False, t=table: self._add_row(t))
            del_btn = QtWidgets.QPushButton("删除行")
            del_btn.clicked.connect(lambda _=False, t=table: self._delete_row(t))
            sync_btn = QtWidgets.QPushButton("按 Slope 重算 Ramp")
            sync_btn.clicked.connect(lambda _=False, t=table: self._sync_ramps(t))
            toolbar.addWidget(add_btn)
            toolbar.addWidget(del_btn)
            toolbar.addWidget(sync_btn)
            toolbar.addStretch()
            page_layout.addLayout(toolbar)
            self.tabWidget_EN50530.addTab(page, tab_label)
            self._tables[tab_id] = table
        self.tabWidget_EN50530.setCurrentIndex(1)
        self.tabWidget_EN50530.currentChanged.connect(lambda _i: self._emit_changed())
        root.addWidget(self.tabWidget_EN50530, 1)

        self.textEdit_S3_wt_filename = QtWidgets.QLineEdit("DynamicMPPT_BR")
        self.textEdit_S3_wt_filename.setObjectName("textEdit_S3_wt_filename")
        fn_row = QtWidgets.QHBoxLayout()
        fn_row.addWidget(QtWidgets.QLabel("WT 连续录文件名"))
        fn_row.addWidget(self.textEdit_S3_wt_filename, 1)
        root.addLayout(fn_row)

        self.label_total_duration = QtWidgets.QLabel("")
        self.label_total_duration.setObjectName("label_EN50530_total_duration")
        self.label_total_duration.setStyleSheet("color: #0f766e; font-weight: bold;")
        root.addWidget(self.label_total_duration)

        for edit in (
            self.textEdit_S3_initial_setup_s,
            self.textEdit_S3_vmp,
            self.textEdit_S3_pmpp,
        ):
            edit.textChanged.connect(lambda _t=None: self._emit_changed())
        self.comboBox_S3_ff.currentIndexChanged.connect(lambda _i: self._emit_changed())
        self.textEdit_S3_wt_filename.textChanged.connect(lambda _t=None: self._emit_changed())
        self._refresh_total_duration()

    def _emit_changed(self) -> None:
        self._refresh_total_duration()
        self.profile_changed.emit()

    def _refresh_total_duration(self) -> None:
        try:
            bundle = validate_en50530_bundle(self.get_bundle_dict())
            total = estimate_en50530_total_duration_s(bundle)
            tab_label = dict(EN50530_TABS).get(bundle.active_tab, bundle.active_tab)
            n = len(bundle.enabled_rows_for_active_tab())
            hours = total / 3600.0
            self.label_total_duration.setText(
                "预计总时长 ≈ %.0f s（%.2f h）= Initial Setup + 当前页签「%s」%d 行 Enable"
                % (total, hours, tab_label, n)
            )
        except Exception as exc:
            self.label_total_duration.setText("预计总时长：%s" % exc)

    def _line_edit(self, name: str, default: str) -> QtWidgets.QLineEdit:
        edit = QtWidgets.QLineEdit(default)
        edit.setObjectName(name)
        return edit

    def _make_table(self, tab_id: str) -> QtWidgets.QTableWidget:
        table = QtWidgets.QTableWidget(0, len(_COLUMNS))
        table.setObjectName("tableWidget_EN50530_%s" % tab_id)
        for col, (_key, label) in enumerate(_COLUMNS):
            table.setHorizontalHeaderItem(col, QtWidgets.QTableWidgetItem(label))
        table.horizontalHeader().setStretchLastSection(True)
        table.itemChanged.connect(self._on_item_changed)
        self._table_tab_id[table] = tab_id
        return table

    def _on_item_changed(self, item: QtWidgets.QTableWidgetItem) -> None:
        if self._loading or item is None:
            return
        table = item.tableWidget()
        if table is None:
            return
        key = _COLUMNS[item.column()][0]
        if key == "slope_wm2_s":
            self._sync_row_ramp_from_slope(table, item.row())
        if key in _EDITABLE_KEYS or key in _RAMP_KEYS or key == "enabled":
            self._refresh_duration_cell(table, item.row())
        self._emit_changed()

    def _sync_row_ramp_from_slope(self, table: QtWidgets.QTableWidget, row: int) -> None:
        tab_id = self._table_tab_id.get(table) or "30_100"
        data = self._read_row(table, row)
        if not data.get("enabled", True):
            return
        synced = apply_softpanel_ramp_times(data, tab_id=tab_id, irr_stc_wm2=1000.0)
        self._loading = True
        try:
            for key in ("ramp_up_s", "ramp_dn_s"):
                col = next(i for i, (k, _) in enumerate(_COLUMNS) if k == key)
                text = "%.3g" % float(synced[key])
                item = table.item(row, col)
                if item is None:
                    item = QtWidgets.QTableWidgetItem(text)
                    table.setItem(row, col, item)
                else:
                    item.setText(text)
                item.setBackground(QtGui.QColor("#ecfdf5"))
        finally:
            self._loading = False

    def _sync_ramps(self, table: QtWidgets.QTableWidget) -> None:
        for row in range(table.rowCount()):
            self._sync_row_ramp_from_slope(table, row)
            self._refresh_duration_cell(table, row)
        self._emit_changed()

    def _refresh_duration_cell(self, table: QtWidgets.QTableWidget, row: int) -> None:
        data = self._read_row(table, row)
        duration = row_cycle_duration_s(data) if data.get("enabled", True) else 0.0
        col = next(i for i, (k, _) in enumerate(_COLUMNS) if k == "duration_s")
        self._loading = True
        try:
            item = table.item(row, col)
            text = ("%.0f" % duration) if duration else "0"
            if item is None:
                item = QtWidgets.QTableWidgetItem(text)
                item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                table.setItem(row, col, item)
            else:
                item.setText(text)
            item.setBackground(QtGui.QColor("#f1f5f9"))
        finally:
            self._loading = False

    def _add_row(self, table: QtWidgets.QTableWidget) -> None:
        tab_id = self._table_tab_id.get(table) or "30_100"
        row = table.rowCount()
        table.insertRow(row)
        data = apply_softpanel_ramp_times(
            {
                "enabled": True,
                "repetitions": 1,
                "slope_wm2_s": 10,
                "dwell_up_s": 10,
                "dwell_dn_s": 10,
            },
            tab_id=tab_id,
            irr_stc_wm2=1000.0,
        )
        self._fill_row(table, row, data)
        self._emit_changed()

    def _delete_row(self, table: QtWidgets.QTableWidget) -> None:
        row = table.currentRow()
        if row >= 0:
            table.removeRow(row)
            self._emit_changed()

    def _fill_row(self, table: QtWidgets.QTableWidget, row: int, data: Dict[str, Any]) -> None:
        self._loading = True
        try:
            duration = row_cycle_duration_s(data) if data.get("enabled", True) else 0.0
            for col, (key, _label) in enumerate(_COLUMNS):
                if key == "enabled":
                    item = QtWidgets.QTableWidgetItem("")
                    item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                    item.setCheckState(
                        QtCore.Qt.Checked if data.get("enabled", True) else QtCore.Qt.Unchecked
                    )
                elif key == "duration_s":
                    item = QtWidgets.QTableWidgetItem("%.0f" % duration)
                    item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    item.setBackground(QtGui.QColor("#f1f5f9"))
                elif key in _RAMP_KEYS:
                    val = data.get(key, "")
                    try:
                        text = "%.3g" % float(val)
                    except (TypeError, ValueError):
                        text = str(val)
                    item = QtWidgets.QTableWidgetItem(text)
                    item.setBackground(QtGui.QColor("#ecfdf5"))
                else:
                    item = QtWidgets.QTableWidgetItem(str(data.get(key, "")))
                table.setItem(row, col, item)
        finally:
            self._loading = False

    def _set_table_rows(self, table: QtWidgets.QTableWidget, rows: List[Dict[str, Any]]) -> None:
        table.setRowCount(0)
        tab_id = self._table_tab_id.get(table) or "30_100"
        for data in rows:
            row = table.rowCount()
            table.insertRow(row)
            synced = apply_softpanel_ramp_times(data, tab_id=tab_id, irr_stc_wm2=1000.0)
            self._fill_row(table, row, synced)

    def _read_row(self, table: QtWidgets.QTableWidget, row: int) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        for col, (key, _label) in enumerate(_COLUMNS):
            item = table.item(row, col)
            if item is None:
                continue
            if key == "enabled":
                data[key] = item.checkState() == QtCore.Qt.Checked
            elif key == "duration_s":
                continue
            else:
                text = item.text().strip()
                if text:
                    data[key] = text
        return data

    def _read_table_rows(self, table: QtWidgets.QTableWidget) -> List[Dict[str, Any]]:
        return [self._read_row(table, row) for row in range(table.rowCount())]

    def get_bundle_dict(self) -> Dict[str, Any]:
        tab_ids = [tab_id for tab_id, _ in EN50530_TABS]
        active = tab_ids[self.tabWidget_EN50530.currentIndex()]
        ff_label = self.comboBox_S3_ff.currentText()
        ff_map = {"c-Si": 0.8, "a-Si": 0.75, "Thin Film": 0.7}
        return {
            "active_tab": active,
            "stc": {
                "initial_setup_s": self.textEdit_S3_initial_setup_s.text().strip() or "300",
                "vmp": self.textEdit_S3_vmp.text().strip() or "100",
                "pmpp": self.textEdit_S3_pmpp.text().strip() or "600",
                "ff": ff_map.get(ff_label, 0.8),
                "ff_label": ff_label,
                "irr_stc_wm2": 1000,
            },
            "tabs": {tab_id: self._read_table_rows(self._tables[tab_id]) for tab_id in tab_ids},
            "wt_filename": self.textEdit_S3_wt_filename.text().strip() or "DynamicMPPT_BR",
        }

    def set_bundle_dict(self, payload: Dict[str, Any]) -> None:
        self._loading = True
        try:
            stc = payload.get("stc") or {}
            self.textEdit_S3_initial_setup_s.setText(str(stc.get("initial_setup_s", 300)))
            self.textEdit_S3_vmp.setText(str(stc.get("vmp", 100)))
            self.textEdit_S3_pmpp.setText(str(stc.get("pmpp", 600)))
            ff_label = str(stc.get("ff_label") or "c-Si")
            idx = self.comboBox_S3_ff.findText(ff_label)
            if idx >= 0:
                self.comboBox_S3_ff.setCurrentIndex(idx)
            tabs = payload.get("tabs") or {}
            for tab_id, _ in EN50530_TABS:
                self._set_table_rows(self._tables[tab_id], list(tabs.get(tab_id) or []))
            active = str(payload.get("active_tab") or "30_100")
            for index, (tab_id, _label) in enumerate(EN50530_TABS):
                if tab_id == active:
                    self.tabWidget_EN50530.setCurrentIndex(index)
                    break
            self.textEdit_S3_wt_filename.setText(str(payload.get("wt_filename") or "DynamicMPPT_BR"))
        finally:
            self._loading = False
        self._refresh_total_duration()

    def get_bundle_json(self) -> str:
        return json.dumps(self.get_bundle_dict(), ensure_ascii=False)

    def set_bundle_json(self, raw: str) -> None:
        if not str(raw or "").strip():
            return
        self.set_bundle_dict(json.loads(raw))

    def validated_bundle(self):
        return validate_en50530_bundle(self.get_bundle_dict())
