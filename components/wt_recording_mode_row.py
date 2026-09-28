# -*- coding: utf-8 -*-
"""功率分析仪页：录波方式 + 推荐文件名填充。"""

from __future__ import annotations

from typing import Callable, List, Optional

from PyQt5 import QtCore, QtWidgets

from utils.wt_recording_mode import MODE_LABELS, MODE_CONTINUOUS, MODE_SPLIT, mode_to_combo_index


class WtRecordingModeRow(QtWidgets.QWidget):
    """可嵌入 WT groupBox_7 或试验 step 的录波方式行。"""

    mode_changed = QtCore.pyqtSignal(str)

    def __init__(
        self,
        parent=None,
        *,
        fill_callback: Optional[Callable[[], List[str]]] = None,
    ):
        super().__init__(parent)
        self._fill_callback = fill_callback
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 4)
        layout.setSpacing(8)

        layout.addWidget(QtWidgets.QLabel("录波方式："))
        self.comboBox_recording_mode = QtWidgets.QComboBox()
        self.comboBox_recording_mode.setObjectName("comboBox_recording_mode")
        self.comboBox_recording_mode.addItem(MODE_LABELS[MODE_CONTINUOUS], MODE_CONTINUOUS)
        self.comboBox_recording_mode.addItem(MODE_LABELS[MODE_SPLIT], MODE_SPLIT)
        self.comboBox_recording_mode.setProperty("_ui_design_min_w", 260)
        try:
            from components import ui_theme as theme

            self.comboBox_recording_mode.setMinimumWidth(theme.px(260))
        except Exception:
            self.comboBox_recording_mode.setMinimumWidth(260)
        layout.addWidget(self.comboBox_recording_mode)

        self.pushButton_fill_recommended_names = QtWidgets.QPushButton("填充推荐文件名")
        self.pushButton_fill_recommended_names.setObjectName("pushButton_fill_recommended_names")
        layout.addWidget(self.pushButton_fill_recommended_names)
        layout.addStretch()

        self.comboBox_recording_mode.currentIndexChanged.connect(self._emit_mode)
        self.pushButton_fill_recommended_names.clicked.connect(self._on_fill)

    def current_mode(self) -> str:
        idx = self.comboBox_recording_mode.currentIndex()
        return self.comboBox_recording_mode.itemData(idx) or MODE_CONTINUOUS

    def set_mode(self, mode: str) -> None:
        self.comboBox_recording_mode.setCurrentIndex(mode_to_combo_index(mode))

    def _emit_mode(self, _index=None):
        self.mode_changed.emit(self.current_mode())
        # 切换录波方式时自动按当前模式填充推荐文件名（连续录→试验单文件）
        if self._fill_callback is not None:
            try:
                self.names_filled.emit(self._fill_callback())
            except Exception:
                pass

    def _on_fill(self):
        if self._fill_callback is None:
            return
        self.names_filled.emit(self._fill_callback())

    names_filled = QtCore.pyqtSignal(list)

    def set_fill_callback(self, callback: Callable[[], List[str]]) -> None:
        self._fill_callback = callback


def install_on_wt_filename_group(
    wt_page: QtWidgets.QWidget,
    fill_callback: Callable[[], List[str]],
) -> Optional[WtRecordingModeRow]:
    """在 WT 页的 groupBox_7 顶部插入录波方式行；已有则复用，避免重复。"""
    gb = wt_page.findChild(QtWidgets.QGroupBox, "groupBox_7")
    if gb is None or gb.layout() is None:
        return None
    row = gb.findChild(WtRecordingModeRow)
    if row is None:
        row = WtRecordingModeRow(gb, fill_callback=fill_callback)
        gb.layout().insertWidget(0, row)
    else:
        row.set_fill_callback(fill_callback)
    return row
