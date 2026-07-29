"""DEWETRON 数据查看对话框。

显示本批次的实时数据，支持 version 切换和导出 CSV。
"""

import json
import os
import csv
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
    QFileDialog, QMessageBox, QGroupBox
)


class DialogDEWETRONDataViewer(QDialog):
    """DEWETRON 数据查看对话框。

    功能：
    - 显示当前批次的所有 version 下拉框
    - 表格展示选中 version 的实时数据
    - 导出按钮，选择路径导出 CSV
    """

    def __init__(self, collector, parent=None):
        """初始化对话框。

        Args:
            collector: DewetronDataCollector 实例
            parent: 父窗口
        """
        super().__init__(parent)
        self._collector = collector
        self._current_batch_id = None
        self._header = []

        self._init_ui()

    def _init_ui(self):
        """初始化 UI。"""
        self.setWindowTitle("DEWETRON 数据查看")
        self.setMinimumSize(800, 500)

        layout = QVBoxLayout(self)

        # 顶部工具栏
        toolbar_layout = QHBoxLayout()

        # 批次信息
        self._lbl_batch = QLabel("批次: --")
        self._lbl_batch.setStyleSheet("font-weight: bold; font-size: 12px;")
        toolbar_layout.addWidget(self._lbl_batch)

        toolbar_layout.addStretch()

        # Version 下拉框
        toolbar_layout.addWidget(QLabel("版本:"))
        self._combo_version = QComboBox()
        self._combo_version.setMinimumWidth(150)
        self._combo_version.currentIndexChanged.connect(self._on_version_changed)
        toolbar_layout.addWidget(self._combo_version)

        # 刷新按钮
        self._btn_refresh = QPushButton("刷新")
        self._btn_refresh.clicked.connect(self._refresh_data)
        toolbar_layout.addWidget(self._btn_refresh)

        # 导出按钮
        self._btn_export = QPushButton("导出 CSV")
        self._btn_export.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px 15px;")
        self._btn_export.clicked.connect(self._export_csv)
        toolbar_layout.addWidget(self._btn_export)

        layout.addLayout(toolbar_layout)

        # 数据表格
        self._table = QTableWidget()
        self._table.setAlternatingRowColors(True)
        self._table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f5f5f5;
                gridline-color: #ddd;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: black;
            }
        """)
        layout.addWidget(self._table)

        # 底部状态栏
        status_layout = QHBoxLayout()
        self._lbl_status = QLabel("就绪")
        status_layout.addWidget(self._lbl_status)
        self._lbl_count = QLabel("共 0 条")
        status_layout.addWidget(self._lbl_count)
        layout.addLayout(status_layout)

    def showEvent(self, event):
        """窗口显示时刷新数据。"""
        super().showEvent(event)
        self._refresh_batch_info()

    def _refresh_batch_info(self):
        """刷新批次信息。"""
        if not self._collector or not self._collector._conn:
            self._lbl_batch.setText("批次: 未连接数据库")
            return

        batch_uid = self._collector.get_batch_uid()
        batch_id = self._collector._batch_id

        if batch_uid:
            self._lbl_batch.setText(f"批次: {batch_uid}")
            self._current_batch_id = batch_id
        else:
            # 获取最近的批次
            batches = self._collector.list_batches()
            if batches:
                latest = batches[0]  # 最新的批次
                self._current_batch_id = latest[0]
                self._lbl_batch.setText(f"批次: {latest[1]}")
            else:
                self._lbl_batch.setText("批次: 无")
                self._current_batch_id = None

        self._refresh_version_list()

    def _refresh_version_list(self):
        """刷新 version 下拉框。"""
        self._combo_version.blockSignals(True)
        self._combo_version.clear()

        if not self._current_batch_id or not self._collector._conn:
            self._combo_version.blockSignals(False)
            return

        runs = self._collector.get_batch_runs(self._current_batch_id)
        for run in runs:
            # run: (id, version, start_time, end_time, total_rows)
            run_id, version, start_time, end_time, total_rows = run
            label = f"v{version} ({total_rows}条) {start_time or ''}"
            self._combo_version.addItem(label, run_id)

        self._combo_version.blockSignals(False)

        if self._combo_version.count() > 0:
            self._on_version_changed()

    def _on_version_changed(self):
        """version 下拉框变化时刷新数据。"""
        run_id = self._combo_version.currentData()
        if run_id:
            self._load_data(run_id)

    def _refresh_data(self):
        """刷新当前 version 的数据。"""
        self._refresh_batch_info()

    def _load_data(self, run_id):
        """加载指定 run_id 的数据到表格。"""
        if not self._collector._conn:
            return

        self._lbl_status.setText("加载中...")
        self._table.setRowCount(0)

        # 获取表头
        row = self._collector._conn.execute(
            "SELECT csv_header FROM de_test_runs WHERE id = ?", (run_id,)
        ).fetchone()
        if not row or not row[0]:
            self._lbl_status.setText("无表头信息")
            return

        self._header = json.loads(row[0])

        # 获取数据
        rows = self._collector._conn.execute(
            "SELECT time, channel_values FROM de_data WHERE run_id = ? ORDER BY seq",
            (run_id,)
        ).fetchall()

        # 设置表格
        self._table.setColumnCount(len(self._header))
        self._table.setHorizontalHeaderLabels(self._header)
        self._table.setRowCount(len(rows))

        for i, (time_val, values_json) in enumerate(rows):
            values = json.loads(values_json)
            # 时间列
            self._table.setItem(i, 0, QTableWidgetItem(f"{time_val:.4f}"))
            # 数据列
            for j, val in enumerate(values):
                self._table.setItem(i, j + 1, QTableWidgetItem(f"{val:.7f}"))

        # 自适应列宽
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self._lbl_status.setText("就绪")
        self._lbl_count.setText(f"共 {len(rows)} 条")

    def _export_csv(self):
        """导出当前 version 的数据到 CSV。"""
        run_id = self._combo_version.currentData()
        if not run_id:
            QMessageBox.warning(self, "提示", "请先选择一个版本")
            return

        # 选择保存路径
        batch_uid = self._lbl_batch.text().replace("批次: ", "")
        default_name = f"{batch_uid}_v{self._combo_version.currentIndex() + 1}.csv"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出 CSV", default_name,
            "CSV Files (*.csv);;All Files (*)"
        )

        if not file_path:
            return

        try:
            # 获取表头
            row = self._collector._conn.execute(
                "SELECT csv_header FROM de_test_runs WHERE id = ?", (run_id,)
            ).fetchone()
            header = json.loads(row[0])

            # 获取数据
            rows = self._collector._conn.execute(
                "SELECT time, channel_values FROM de_data WHERE run_id = ? ORDER BY seq",
                (run_id,)
            ).fetchall()

            # 写入 CSV
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                for time_val, values_json in rows:
                    values = json.loads(values_json)
                    writer.writerow([f"{time_val:.4f}"] + [f"{v:.7f}" for v in values])

            QMessageBox.information(self, "导出成功", f"已导出 {len(rows)} 条数据到:\n{file_path}")
            self._lbl_status.setText(f"已导出: {file_path}")

        except Exception as e:
            QMessageBox.warning(self, "导出失败", f"导出异常: {e}")
