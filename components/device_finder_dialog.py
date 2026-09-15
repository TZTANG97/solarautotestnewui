# -*- coding: utf-8 -*-
"""扫描并勾选连接设备：不自动弹、不自动占槽。"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from components import ui_theme as theme
from utils.device_discovery import (
    FoundDevice,
    SLOT_CHOICES,
    devices_from_last_resources,
    run_discovery,
    summarize_discovery,
    validate_assignments,
)


class _ScanWorker(QThread):
    progressed = pyqtSignal(str)
    finished_ok = pyqtSignal(list)
    failed = pyqtSignal(str)

    def __init__(self, visa_rm, last_resources, scan_lan_enabled, skip_resources=None):
        super().__init__()
        self._rm = visa_rm
        self._last = list(last_resources or [])
        self._lan = bool(scan_lan_enabled)
        self._skip = list(skip_resources or [])
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        try:
            devices = run_discovery(
                visa_rm=self._rm,
                last_resources=self._last,
                scan_lan_enabled=self._lan,
                progress=lambda m: self.progressed.emit(m),
                cancel_flag=lambda: self._cancel,
                skip_resources=self._skip,
            )
            self.finished_ok.emit(devices)
        except Exception as exc:
            self.failed.emit(str(exc))


class DeviceFinderDialog(QDialog):
    def __init__(
        self,
        parent=None,
        visa_rm=None,
        last_resources: Optional[Sequence[str]] = None,
        skip_resources: Optional[Sequence[str]] = None,
    ):
        super().__init__(parent)
        self.setWindowTitle("扫描并连接设备")
        self.resize(920, 520)
        self._rm = visa_rm
        self._last = list(last_resources or [])
        self._skip = list(skip_resources or [])
        self._worker: Optional[_ScanWorker] = None
        self._devices: List[FoundDevice] = []
        self._jobs: List[tuple] = []

        root = QVBoxLayout(self)
        tip = QLabel(
            "打开后不会自动扫描。默认先列本机上次连过的地址；勾选「扫描局域网」会扫当前网段常见端口。"
            "只连接勾选行，且必须人手指定槽位（同型号多台不会自动占用 DC1/DC2）。"
            "开测前请先在仪器面板设好电压/电流/功率输出上限（软件本期不代设）。"
        )
        tip.setWordWrap(True)
        tip.setStyleSheet(f"color: {theme.MUTED};")
        root.addWidget(tip)

        tools = QHBoxLayout()
        self._lan_check = QCheckBox("扫描局域网（较慢）")
        self._scan_btn = QPushButton("开始扫描")
        self._scan_btn.setCursor(Qt.PointingHandCursor)
        self._cancel_btn = QPushButton("停止")
        self._cancel_btn.setEnabled(False)
        self._status = QLabel("未扫描。可先点开始扫描，或直接勾选上次地址后指定槽位。")
        tools.addWidget(self._lan_check)
        tools.addWidget(self._scan_btn)
        tools.addWidget(self._cancel_btn)
        tools.addWidget(self._status, 1)
        root.addLayout(tools)

        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels(
            ["勾选", "地址", "识别信息", "建议类型", "指定槽位", "来源"]
        )
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        root.addWidget(self._table, 1)

        buttons = QDialogButtonBox()
        self._connect_btn = buttons.addButton("连接勾选项", QDialogButtonBox.AcceptRole)
        buttons.addButton("关闭", QDialogButtonBox.RejectRole)
        buttons.accepted.connect(self._on_connect)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

        self._scan_btn.clicked.connect(self._start_scan)
        self._cancel_btn.clicked.connect(self._stop_worker)
        self._fill_table(devices_from_last_resources(self._last, source="上次"))

    def checked_jobs(self) -> List[tuple]:
        return list(self._jobs)

    def closeEvent(self, event):
        self._stop_worker()
        super().closeEvent(event)

    def _snapshot_choices(self) -> Dict[str, Tuple[bool, str]]:
        snap = {}
        for row, dev in enumerate(self._devices):
            item = self._table.item(row, 0)
            checked = bool(item and item.checkState() == Qt.Checked)
            combo = self._table.cellWidget(row, 4)
            slot = combo.currentData() if combo is not None else ""
            snap[dev.resource] = (checked, slot or "")
            if dev.host and dev.port:
                snap[f"{dev.host}:{dev.port}"] = (checked, slot or "")
        return snap

    def _stop_worker(self):
        if self._worker is not None:
            self._worker.cancel()
            self._status.setText("正在停止扫描…")
            self._worker.wait(2500)
            self._worker = None
        self._scan_btn.setEnabled(True)
        self._cancel_btn.setEnabled(False)
        self._connect_btn.setEnabled(True)

    def _start_scan(self):
        if self._worker is not None and self._worker.isRunning():
            return
        self._scan_btn.setEnabled(False)
        self._cancel_btn.setEnabled(True)
        self._connect_btn.setEnabled(False)
        self._status.setText("扫描中…")
        self._worker = _ScanWorker(
            self._rm, self._last, self._lan_check.isChecked(), skip_resources=self._skip
        )
        self._worker.progressed.connect(self._status.setText)
        self._worker.finished_ok.connect(self._on_scan_done)
        self._worker.failed.connect(self._on_scan_fail)
        self._worker.start()

    def _on_scan_done(self, devices: List[FoundDevice]):
        snap = self._snapshot_choices()
        self._scan_btn.setEnabled(True)
        self._cancel_btn.setEnabled(False)
        self._connect_btn.setEnabled(True)
        self._worker = None
        self._status.setText(summarize_discovery(devices) + " 请勾选并指定槽位。")
        self._fill_table(devices, preserve=snap)

    def _on_scan_fail(self, message: str):
        self._scan_btn.setEnabled(True)
        self._cancel_btn.setEnabled(False)
        self._connect_btn.setEnabled(True)
        self._worker = None
        self._status.setText(f"扫描失败：{message}")

    def _fill_table(self, devices: Sequence[FoundDevice], preserve: Optional[dict] = None):
        preserve = preserve or {}
        self._devices = list(devices)
        self._table.setRowCount(len(self._devices))
        for row, dev in enumerate(self._devices):
            prev = preserve.get(dev.resource) or preserve.get(
                f"{dev.host}:{dev.port}" if dev.host and dev.port else ""
            )
            chk = QTableWidgetItem()
            chk.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            chk.setCheckState(Qt.Checked if prev and prev[0] else Qt.Unchecked)
            self._table.setItem(row, 0, chk)
            addr = QTableWidgetItem(dev.resource)
            addr.setFlags(addr.flags() & ~Qt.ItemIsEditable)
            self._table.setItem(row, 1, addr)
            idn_item = QTableWidgetItem(dev.display_idn())
            idn_item.setFlags(idn_item.flags() & ~Qt.ItemIsEditable)
            self._table.setItem(row, 2, idn_item)
            hint = QTableWidgetItem(dev.kind_label())
            hint.setFlags(hint.flags() & ~Qt.ItemIsEditable)
            self._table.setItem(row, 3, hint)
            combo = QComboBox()
            for sid, label in SLOT_CHOICES:
                combo.addItem(label, sid)
            combo.setCurrentIndex(0)
            if prev and prev[1]:
                idx = combo.findData(prev[1])
                if idx >= 0:
                    combo.setCurrentIndex(idx)
            self._table.setCellWidget(row, 4, combo)
            src = QTableWidgetItem(dev.source or "")
            src.setFlags(src.flags() & ~Qt.ItemIsEditable)
            self._table.setItem(row, 5, src)

    def _collect_rows(self):
        rows = []
        for row, dev in enumerate(self._devices):
            item = self._table.item(row, 0)
            checked = bool(item and item.checkState() == Qt.Checked)
            combo = self._table.cellWidget(row, 4)
            slot = combo.currentData() if combo is not None else ""
            rows.append((checked, slot or "", dev))
        return rows

    def _on_connect(self):
        rows = self._collect_rows()
        err = validate_assignments(rows)
        if err:
            QMessageBox.warning(self, "无法连接", err)
            return
        self._jobs = [(slot, dev) for checked, slot, dev in rows if checked]
        self.accept()
