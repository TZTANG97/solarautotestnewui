# -*- coding: utf-8 -*-
"""功率分析仪页：宏 / SCPI 采集模式选择。"""
from __future__ import annotations

from PyQt5 import QtWidgets

from utils.wt_acquire_mode import (
    COMBO_NAME,
    MODE_LABEL_MACRO,
    MODE_LABEL_SCPI,
    MODE_MACRO,
    MODE_SCPI,
    mode_to_combo_index,
    normalize_mode,
)


class WtAcquireModeRow(QtWidgets.QWidget):
    """可嵌入 WT 基本设置区顶部的采集模式行。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 4)
        layout.setSpacing(8)

        layout.addWidget(QtWidgets.QLabel("采集模式："))
        self.comboBox_wt_acquire_mode = QtWidgets.QComboBox()
        self.comboBox_wt_acquire_mode.setObjectName(COMBO_NAME)
        self.comboBox_wt_acquire_mode.addItem(MODE_LABEL_MACRO, MODE_MACRO)
        self.comboBox_wt_acquire_mode.addItem(MODE_LABEL_SCPI, MODE_SCPI)
        self.comboBox_wt_acquire_mode.setMinimumWidth(200)
        layout.addWidget(self.comboBox_wt_acquire_mode)

        hint = QtWidgets.QLabel("SCPI 需设备管理已连接功率分析仪（建议以太网）")
        hint.setStyleSheet("color: #64748b; font-size: 11px;")
        layout.addWidget(hint)
        layout.addStretch()

    def current_mode(self) -> str:
        data = self.comboBox_wt_acquire_mode.currentData()
        return normalize_mode(data or MODE_MACRO)

    def set_mode(self, mode: str) -> None:
        self.comboBox_wt_acquire_mode.setCurrentIndex(mode_to_combo_index(mode))
