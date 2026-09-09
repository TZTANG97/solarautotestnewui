# -*- coding: utf-8 -*-
"""矩阵试验 Step3：录波方式 + 推荐文件名（连续录 / 分开录）。"""

from __future__ import annotations

from PyQt5 import QtWidgets

from utils.wt_recording_mode import MODE_CONTINUOUS, MODE_LABELS, MODE_SPLIT, combo_index_to_mode
from components.wt_recording_mode_row import install_on_wt_filename_group


def add_record_mode_row(ladder_layout, row: int, dialog) -> None:
    """在 ladder_layout 指定行加入录波方式下拉与填充按钮。"""
    parent = ladder_layout.parentWidget()
    ladder_layout.addWidget(QtWidgets.QLabel("录波方式："), row, 0)
    combo = QtWidgets.QComboBox(parent)
    combo.setObjectName("comboBox_S3_record_mode")
    combo.addItem(MODE_LABELS[MODE_CONTINUOUS], MODE_CONTINUOUS)
    combo.addItem(MODE_LABELS[MODE_SPLIT], MODE_SPLIT)
    combo.setMinimumWidth(220)
    dialog.comboBox_S3_record_mode = combo
    ladder_layout.addWidget(combo, row, 1)
    btn = QtWidgets.QPushButton("填充推荐文件名", parent)
    btn.setObjectName("pushButton_S3_fill_filenames")
    dialog.pushButton_S3_fill_filenames = btn
    ladder_layout.addWidget(btn, row, 2)


def wire_matrix_recording(dialog, recommended_names_fn) -> None:
    """绑定录波方式、WT 文件名区与推荐名填充。"""
    from utils.wt_recording_mode import (
        apply_filename_list_to_wt_pages,
        combo_index_to_mode,
        mode_to_combo_index,
    )

    def _fill_wt_names(names=None):
        if names is None:
            names = recommended_names_fn()
        apply_filename_list_to_wt_pages(dialog._wtStacked, names)

    def _sync_wt_rows(mode=None):
        from components.wt_recording_mode_row import WtRecordingModeRow

        if mode is None:
            mode = combo_index_to_mode(dialog.comboBox_S3_record_mode.currentIndex())
        for page_idx in range(dialog._wtStacked.count()):
            page = dialog._wtStacked.widget(page_idx)
            if page is None:
                continue
            row = page.findChild(WtRecordingModeRow)
            if row is None:
                continue
            row.blockSignals(True)
            row.set_mode(mode)
            row.blockSignals(False)

    def _on_s3_mode(_index=None):
        mode = combo_index_to_mode(dialog.comboBox_S3_record_mode.currentIndex())
        _sync_wt_rows(mode)
        _fill_wt_names()

    def _on_wt_mode(mode):
        s3 = getattr(dialog, "comboBox_S3_record_mode", None)
        if s3 is not None:
            s3.blockSignals(True)
            s3.setCurrentIndex(mode_to_combo_index(mode))
            s3.blockSignals(False)
        _sync_wt_rows(mode)
        # names_filled 已由 WtRecordingModeRow 切模式时自动触发；此处再填一次确保一致

    dialog.pushButton_S3_fill_filenames.clicked.connect(lambda: _fill_wt_names())
    dialog.comboBox_S3_record_mode.currentIndexChanged.connect(_on_s3_mode)

    for page_idx in range(dialog._wtStacked.count()):
        page = dialog._wtStacked.widget(page_idx)
        row = install_on_wt_filename_group(page, recommended_names_fn)
        if row is not None:
            if not getattr(row, "_matrix_names_connected", False):
                row.names_filled.connect(_fill_wt_names)
                row.mode_changed.connect(_on_wt_mode)
                row._matrix_names_connected = True

    _sync_wt_rows()
    _fill_wt_names()


def make_recommended_fn(dialog, builder):
    """builder(mode_str) -> list of filenames"""

    def _fn():
        mode = combo_index_to_mode(dialog.comboBox_S3_record_mode.currentIndex())
        return builder(mode)

    return _fn
