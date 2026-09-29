"""DEWETRON 数据查看对话框。

显示测试批次的实时数据，支持 version 切换和导出 CSV。
"""

import os

from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


class DialogDEWETRONDataViewer(QDialog):
    """通过采集器公共 API 查看和导出 DEWETRON 数据。"""

    def __init__(self, collector, parent=None, test_type=None):
        """初始化对话框，可按 ``test_type`` 选择最近批次。"""
        super().__init__(parent)
        self._collector = collector
        self._test_type = test_type
        self._current_batch_id = None
        self._current_batch_uid = None
        self._header = []
        self._init_ui()

    def _init_ui(self):
        """初始化 UI。"""
        self.setWindowTitle("DEWETRON 数据查看")
        self.setMinimumSize(800, 500)

        layout = QVBoxLayout(self)
        toolbar_layout = QHBoxLayout()

        self._lbl_batch = QLabel("批次: --")
        self._lbl_batch.setStyleSheet("font-weight: bold; font-size: 12px;")
        toolbar_layout.addWidget(self._lbl_batch)
        toolbar_layout.addStretch()

        toolbar_layout.addWidget(QLabel("版本:"))
        self._combo_version = QComboBox()
        self._combo_version.setMinimumWidth(150)
        self._combo_version.currentIndexChanged.connect(self._on_version_changed)
        toolbar_layout.addWidget(self._combo_version)

        self._btn_refresh = QPushButton("刷新")
        self._btn_refresh.clicked.connect(self._refresh_data)
        toolbar_layout.addWidget(self._btn_refresh)

        self._btn_export = QPushButton("导出 CSV")
        self._btn_export.setStyleSheet(
            "background-color: #4CAF50; color: white; padding: 5px 15px;"
        )
        self._btn_export.clicked.connect(self._export_csv)
        toolbar_layout.addWidget(self._btn_export)
        layout.addLayout(toolbar_layout)

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

    @staticmethod
    def _batch_values(batch):
        """Return ``(id, uid, type)`` from the collector public batch state."""
        if isinstance(batch, dict):
            return batch.get('id'), batch.get('batch_uid'), batch.get('test_type')
        if batch and len(batch) >= 3:
            return batch[0], batch[1], batch[2]
        return None, None, None

    def _refresh_batch_info(self):
        """刷新当前或最近的匹配批次。"""
        if not self._collector or not self._collector.has_database():
            self._lbl_batch.setText("批次: 未连接数据库")
            self._current_batch_id = None
            self._current_batch_uid = None
            self._refresh_version_list()
            return

        batch_id = batch_uid = None
        current = self._collector.current_batch()
        current_id, current_uid, current_type = self._batch_values(current)
        if current_id and (self._test_type is None or current_type == self._test_type):
            batch_id, batch_uid = current_id, current_uid
        else:
            batches = self._collector.list_batches(self._test_type)
            if batches:
                batch_id, batch_uid = batches[0][0], batches[0][1]

        self._current_batch_id = batch_id
        self._current_batch_uid = batch_uid
        self._lbl_batch.setText(f"批次: {batch_uid}" if batch_uid else "批次: 无")
        self._refresh_version_list()

    def _refresh_version_list(self):
        """刷新 version 下拉框。"""
        self._combo_version.blockSignals(True)
        self._combo_version.clear()

        if self._current_batch_id and self._collector.has_database():
            for run_id, version, start_time, _end_time, total_rows in (
                self._collector.get_batch_runs(self._current_batch_id)
            ):
                label = f"v{version} ({total_rows}条) {start_time or ''}"
                self._combo_version.addItem(label, run_id)

        self._combo_version.blockSignals(False)
        if self._combo_version.count() > 0:
            self._on_version_changed()
        else:
            self._clear_table("无测试记录")

    def _on_version_changed(self, _index=None):
        """version 下拉框变化时刷新数据。"""
        run_id = self._combo_version.currentData()
        if run_id is not None:
            self._load_data(run_id)

    def _refresh_data(self):
        """刷新当前 version 的数据。"""
        self._refresh_batch_info()

    def _clear_table(self, status):
        """清空表格并更新状态。"""
        self._header = []
        self._table.clear()
        self._table.setRowCount(0)
        self._table.setColumnCount(0)
        self._lbl_status.setText(status)
        self._lbl_count.setText("共 0 条")

    def _load_data(self, run_id):
        """加载指定 run_id 的数据到表格。"""
        if not self._collector.has_database():
            self._clear_table("数据库未连接")
            return

        self._lbl_status.setText("加载中...")
        header = self._collector.get_run_header(run_id)
        if not header:
            self._clear_table("无表头信息")
            return
        rows = self._collector.get_run_rows(run_id)
        self._header = header

        self._table.clear()
        self._table.setColumnCount(len(header))
        self._table.setHorizontalHeaderLabels(header)
        self._table.setRowCount(len(rows))
        for row_index, (time_val, values) in enumerate(rows):
            self._table.setItem(
                row_index, 0, QTableWidgetItem(f"{float(time_val):.4f}")
            )
            for column_index, value in enumerate(values, start=1):
                if column_index >= len(header):
                    break
                self._table.setItem(
                    row_index,
                    column_index,
                    QTableWidgetItem(f"{float(value):.7f}"),
                )

        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self._lbl_status.setText("就绪")
        self._lbl_count.setText(f"共 {len(rows)} 条")

    def _export_csv(self):
        """导出当前 version 的数据到 CSV。"""
        run_id = self._combo_version.currentData()
        if run_id is None:
            QMessageBox.warning(None, "提示", "请先选择一个版本")
            return

        version = self._combo_version.currentIndex() + 1
        batch_uid = self._current_batch_uid or 'dewetron'
        default_name = f"{batch_uid}_v{version}.csv"
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "导出 CSV",
            default_name,
            "CSV Files (*.csv);;All Files (*)",
        )
        if not file_path:
            return
        if not os.path.splitext(file_path)[1]:
            file_path += '.csv'

        exported = self._collector.export_run_to_csv(run_id, file_path)
        if exported:
            count = len(self._collector.get_run_rows(run_id))
            QMessageBox.information(
                None, "导出成功", f"已导出 {count} 条数据到:\n{exported}"
            )
            self._lbl_status.setText(f"已导出: {exported}")
        else:
            QMessageBox.warning(None, "导出失败", "导出数据失败，请检查保存路径")
