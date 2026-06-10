"""
文件管理对话框 — 管理自动化命令文件和 DEWETRON 配置文件。

功能：
- Tab 1: 自动化命令列表（command_data/ 目录）
- Tab 2: DEWETRON 配置列表（dewetron_data/ 目录）
- 批量删除（2日内文件不可删除）
- 文件预览（csv/xlsx 预览、xml 预览）
"""

import os
import re
import fnmatch
import datetime
from PyQt5 import QtCore, QtGui, QtWidgets


def _parse_date_from_filename(filename):
    """从文件名中解析日期。

    支持格式：
    - {type}_commands{YYYY}_{MM}_{DD}_{HH}.csv
    - dewetron_{YYYY}{MM}{DD}_{HH}.xml
    - dewetron_verify_{YYYY}{MM}{DD}_{HH}.xml

    Returns:
        datetime or None
    """
    # command_data 格式: xxx_commands2026_05_11_09.csv
    m = re.search(r'commands(\d{4})_(\d{2})_(\d{2})_(\d{2})', filename)
    if m:
        try:
            return datetime.datetime(int(m.group(1)), int(m.group(2)),
                                     int(m.group(3)), int(m.group(4)))
        except ValueError:
            pass

    # dewetron_data 格式: dewetron_20260609_17.xml
    m = re.search(r'dewetron_(?:verify_)?(\d{4})(\d{2})(\d{2})_(\d{2})', filename)
    if m:
        try:
            return datetime.datetime(int(m.group(1)), int(m.group(2)),
                                     int(m.group(3)), int(m.group(4)))
        except ValueError:
            pass

    return None


def _is_within_days(filename, days=2):
    """判断文件是否在指定天数内。"""
    dt = _parse_date_from_filename(filename)
    if dt is None:
        return False
    return (datetime.datetime.now() - dt) < datetime.timedelta(days=days)


class FileListWidget(QtWidgets.QWidget):
    """单个文件列表面板，带复选框、预览和批量删除。"""

    def __init__(self, directory, file_filter, preview_type, parent=None):
        super().__init__(parent)
        self._directory = directory
        self._file_filter = file_filter  # ('*.csv',) or ('*.xml',)
        self._preview_type = preview_type  # 'csv' or 'xml'
        self._checkboxes = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # 工具栏
        toolbar = QtWidgets.QHBoxLayout()
        self._label = QtWidgets.QLabel(f"共 0 个文件")
        self._label.setFont(QtGui.QFont("Microsoft YaHei", 9))
        toolbar.addWidget(self._label)
        toolbar.addStretch()

        self._btn_select_all = QtWidgets.QPushButton("全选")
        self._btn_select_all.setFixedSize(60, 28)
        self._btn_select_all.clicked.connect(self._select_all)
        toolbar.addWidget(self._btn_select_all)

        self._btn_delete = QtWidgets.QPushButton("删除选中")
        self._btn_delete.setFixedSize(80, 28)
        self._btn_delete.setStyleSheet("color: red;")
        self._btn_delete.clicked.connect(self._delete_selected)
        toolbar.addWidget(self._btn_delete)

        self._btn_refresh = QtWidgets.QPushButton("刷新")
        self._btn_refresh.setFixedSize(60, 28)
        self._btn_refresh.clicked.connect(self.refresh)
        toolbar.addWidget(self._btn_refresh)

        layout.addLayout(toolbar)

        # 文件列表（带滚动条）
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QtWidgets.QWidget()
        self._list_layout = QtWidgets.QVBoxLayout(scroll_widget)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(2)
        self._list_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        self.refresh()

    def refresh(self):
        """刷新文件列表。"""
        # 清除旧的列表项（保留末尾的 stretch）
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self._checkboxes.clear()

        # 获取文件列表
        if not os.path.isdir(self._directory):
            self._label.setText("目录不存在")
            return

        files = []
        for f in os.listdir(self._directory):
            if any(fnmatch.fnmatch(f, pat) for pat in self._file_filter):
                files.append(f)
        # 按日期排序（最新的在前），无日期的排最后
        def _sort_key(fname):
            dt = _parse_date_from_filename(fname)
            return dt if dt else datetime.datetime.min
        files.sort(key=_sort_key, reverse=True)

        self._label.setText(f"共 {len(files)} 个文件")

        for f in files:
            file_path = os.path.join(self._directory, f)
            file_size = os.path.getsize(file_path)
            dt = _parse_date_from_filename(f)
            date_str = dt.strftime("%Y-%m-%d %H:%M") if dt else "未知日期"

            within_2days = _is_within_days(f, days=2)

            item_widget = QtWidgets.QWidget()
            item_layout = QtWidgets.QHBoxLayout(item_widget)
            item_layout.setContentsMargins(4, 2, 4, 2)

            cb = QtWidgets.QCheckBox()
            cb._filename = f
            cb._filepath = file_path
            if within_2days:
                cb.setEnabled(False)
                cb.setToolTip("2日内文件不可删除")
            self._checkboxes.append(cb)
            item_layout.addWidget(cb)

            # 文件名
            name_label = QtWidgets.QLabel(f)
            name_label.setFont(QtGui.QFont("Consolas", 9))
            if within_2days:
                name_label.setStyleSheet("color: #888;")
            item_layout.addWidget(name_label, 1)

            # 日期
            date_label = QtWidgets.QLabel(date_str)
            date_label.setFont(QtGui.QFont("Microsoft YaHei", 8))
            date_label.setStyleSheet("color: #666;")
            date_label.setFixedWidth(120)
            item_layout.addWidget(date_label)

            # 大小
            if file_size > 1024 * 1024:
                size_str = f"{file_size / 1024 / 1024:.1f} MB"
            elif file_size > 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size} B"
            size_label = QtWidgets.QLabel(size_str)
            size_label.setFont(QtGui.QFont("Microsoft YaHei", 8))
            size_label.setStyleSheet("color: #666;")
            size_label.setFixedWidth(70)
            item_layout.addWidget(size_label)

            # 预览按钮
            preview_btn = QtWidgets.QPushButton("预览")
            preview_btn.setFixedSize(50, 24)
            preview_btn.setFont(QtGui.QFont("Microsoft YaHei", 8))
            preview_btn.clicked.connect(lambda checked, p=file_path: self._preview(p))
            item_layout.addWidget(preview_btn)

            # 插入到 stretch 之前
            self._list_layout.insertWidget(self._list_layout.count() - 1, item_widget)

    def _select_all(self):
        """全选/取消全选可选中的复选框。"""
        all_checked = all(cb.isChecked() or not cb.isEnabled() for cb in self._checkboxes)
        for cb in self._checkboxes:
            if cb.isEnabled():
                cb.setChecked(not all_checked)

    def _delete_selected(self):
        """删除选中的文件。"""
        selected = [cb for cb in self._checkboxes if cb.isChecked() and cb.isEnabled()]
        if not selected:
            QtWidgets.QMessageBox.information(self, "提示", "未选中任何文件")
            return

        count = len(selected)
        names = "\n".join(cb._filename for cb in selected[:10])
        if count > 10:
            names += f"\n... 共 {count} 个文件"

        ret = QtWidgets.QMessageBox.question(
            self, "确认删除",
            f"确定要删除以下 {count} 个文件吗？\n\n{names}",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        if ret != QtWidgets.QMessageBox.Yes:
            return

        deleted = 0
        errors = []
        for cb in selected:
            try:
                os.remove(cb._filepath)
                deleted += 1
            except Exception as e:
                errors.append(f"{cb._filename}: {e}")

        if errors:
            QtWidgets.QMessageBox.warning(
                self, "删除结果",
                f"成功删除 {deleted} 个文件\n删除失败 {len(errors)} 个:\n" + "\n".join(errors[:5])
            )
        else:
            QtWidgets.QMessageBox.information(self, "删除结果", f"成功删除 {deleted} 个文件")

        self.refresh()

    def _preview(self, file_path):
        """预览文件内容。"""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(f"预览 - {os.path.basename(file_path)}")
        dialog.setMinimumSize(700, 500)

        layout = QtWidgets.QVBoxLayout(dialog)

        if self._preview_type == 'csv':
            self._preview_csv(dialog, layout, file_path)
        elif self._preview_type == 'xml':
            self._preview_xml(dialog, layout, file_path)

        close_btn = QtWidgets.QPushButton("关闭")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.exec_()

    def _preview_csv(self, dialog, layout, file_path):
        """预览 CSV 文件，以表格形式展示（含行号）。"""
        table = QtWidgets.QTableWidget()
        table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        table.setFont(QtGui.QFont("Consolas", 9))

        try:
            import csv
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                reader = csv.reader(f)
                all_rows = []
                for i, row in enumerate(reader):
                    if i >= 200:
                        break
                    all_rows.append(row)

            if not all_rows:
                table.setRowCount(1)
                table.setColumnCount(1)
                table.setItem(0, 0, QtWidgets.QTableWidgetItem("(空文件)"))
            else:
                # 第一行作为表头
                headers = all_rows[0]
                data_rows = all_rows[1:] if len(all_rows) > 1 else []
                table.setColumnCount(len(headers))
                table.setHorizontalHeaderLabels(headers)
                table.setRowCount(len(data_rows))
                for r, row in enumerate(data_rows):
                    for c, val in enumerate(row):
                        if c < len(headers):
                            table.setItem(r, c, QtWidgets.QTableWidgetItem(val))

                table.resizeColumnsToContents()
                table.horizontalHeader().setStretchLastSection(True)
                # 行号从 1 开始
                row_labels = [str(i + 1) for i in range(len(data_rows))]
                table.setVerticalHeaderLabels(row_labels)
                table.verticalHeader().setDefaultSectionSize(24)

            if len(all_rows) >= 200:
                label = QtWidgets.QLabel("（显示前 199 行数据）")
                label.setStyleSheet("color: #888;")
                layout.addWidget(label)
        except Exception as e:
            err_label = QtWidgets.QLabel(f"读取失败: {e}")
            layout.addWidget(err_label)

        layout.addWidget(table)

    def _preview_xml(self, dialog, layout, file_path):
        """预览 XML 文件（显示前 500 行）。"""
        text_edit = QtWidgets.QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFont(QtGui.QFont("Consolas", 9))

        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= 500:
                        lines.append("... (超过500行，已截断)")
                        break
                    lines.append(line.rstrip())
                text_edit.setPlainText("\n".join(lines))
        except Exception as e:
            text_edit.setPlainText(f"读取失败: {e}")

        layout.addWidget(text_edit)


class FileManagerDialog(QtWidgets.QDialog):
    """文件管理对话框 — 两个 Tab：自动化命令 + DEWETRON 配置。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("文件管理")
        self.setMinimumSize(750, 520)
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        tabs = QtWidgets.QTabWidget()
        layout.addWidget(tabs)

        # Tab 1: 自动化命令
        cmd_dir = os.path.join(os.path.dirname(__file__),
                               "command_save_files", "command_data")
        cmd_tab = FileListWidget(
            directory=cmd_dir,
            file_filter=('*.csv', '*.xlsx'),
            preview_type='csv'
        )
        tabs.addTab(cmd_tab, "自动化命令")

        # Tab 2: DEWETRON 配置
        dew_dir = os.path.join(os.path.dirname(__file__),
                               "command_save_files", "dewetron_data")
        dew_tab = FileListWidget(
            directory=dew_dir,
            file_filter=('*.xml',),
            preview_type='xml'
        )
        tabs.addTab(dew_tab, "DEWETRON 配置")


def open_file_manager(parent=None):
    """打开文件管理对话框。"""
    dialog = FileManagerDialog(parent)
    dialog.exec_()
