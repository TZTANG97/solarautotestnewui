# -*- coding: utf-8 -*-
"""WT 云任务保存设置：建目录、停机时间、自动命名、录波方式写入。"""
from __future__ import annotations

import os

from utils.wt_job_save import (
    apply_wt_save_to_dialog,
    continuous_filename_for_test,
    prepare_wt_save_widgets,
    record_mode_index,
    validate_stop_time,
    widgets_for_standard_apply,
)


def test_stop_time_accepts_clock_and_seconds():
    assert validate_stop_time("00:05:00")[0] is True
    assert validate_stop_time("05:00")[0] is True
    assert validate_stop_time("90")[0] is True
    assert validate_stop_time("00：01：02")[0] is True
    assert validate_stop_time("")[0] is False
    assert validate_stop_time("abc")[0] is False
    assert validate_stop_time("00:99:00")[0] is False


def test_prepare_creates_dir_and_fills_auto_name(tmp_path):
    folder = tmp_path / "missing" / "wt"
    got = prepare_wt_save_widgets(
        {
            "textEdit_SavePath": str(folder),
            "textEdit_StopTime": "",
            "textEdit_FileNameList": "",
            "checkBox_AutoName": True,
            "comboBox_AutoSave": "OFF",
        },
        "过频降载",
    )
    assert os.path.isdir(got["textEdit_SavePath"])
    assert got["textEdit_StopTime"] == "00:05:00"
    assert got["textEdit_FileNameList"] == "OF_curve"
    assert got["comboBox_AutoSave"] == "自动保存"
    assert continuous_filename_for_test("harmonic") == "Harmonic_BR"


def test_prepare_keeps_explicit_filename(tmp_path):
    folder = tmp_path / "keep"
    got = prepare_wt_save_widgets(
        {
            "textEdit_SavePath": str(folder),
            "textEdit_StopTime": "1:30",
            "textEdit_FileNameList": "Custom_BR",
            "checkBox_AutoName": True,
        },
        "guopinjiangzai",
    )
    assert got["textEdit_FileNameList"] == "Custom_BR"
    assert got["textEdit_StopTime"] == "1:30"
    assert record_mode_index("分开录（多文件/逐点存盘）") == 1
    assert record_mode_index("一条线连续录（单文件）") == 0


def test_split_freq_names_and_dialog_mode():
    from utils.wt_job_save import (
        apply_split_freq_filenames,
        dialog_recording_is_continuous,
        split_freq_filenames,
    )

    class _Combo:
        def __init__(self, idx):
            self.idx = idx

        def currentIndex(self):
            return self.idx

    class _Continuous:
        comboBox_S3_record_mode = _Combo(0)

    class _Split:
        comboBox_S3_record_mode = _Combo(1)

    assert dialog_recording_is_continuous(_Continuous()) is True
    assert dialog_recording_is_continuous(_Split()) is False
    assert dialog_recording_is_continuous(object()) is True

    class _PinnedSplit(_Continuous):
        _wt_record_mode_from_job = "split"

    assert dialog_recording_is_continuous(_PinnedSplit()) is False
    text = split_freq_filenames(["50", "50.25", "51.15"], "OF_curve", "OF_curve")
    assert text == "OF_curve_50,OF_curve_50p25,OF_curve_51p15"
    rows = [["Upper_WT_Config", "", "", "", {"textEdit_FileNameList": "OF_curve", "textEdit_StopTime": "00:08:00"}]]

    class _Edit:
        def __init__(self, value):
            self.value = value

        def toPlainText(self):
            return self.value

    class _Ui:
        textEdit_FrequencyLadder = _Edit("50,50.25")
        comboBox_S3_record_mode = _Combo(1)

    got = apply_split_freq_filenames(rows, _Ui(), file_default="OF_curve", log_label="")
    assert got == "OF_curve_50,OF_curve_50p25"
    assert rows[0][4]["textEdit_StopTime"] == "00:08:00"
    assert rows[0][4]["textEdit_FileNameList"] == got


def test_orphan_record_mode_not_marked_missing():
    class _Root:
        pass

    widgets = {"comboBox_S3_record_mode": "一条线连续录（单文件）", "textEdit_StopTime": "00:05:00"}
    slim = widgets_for_standard_apply(_Root(), widgets)
    assert "comboBox_S3_record_mode" not in slim
    assert slim["textEdit_StopTime"] == "00:05:00"


def test_apply_writes_every_wt_page(tmp_path):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PyQt5.QtWidgets import QApplication, QComboBox, QStackedWidget, QTextEdit, QWidget

    app = QApplication.instance() or QApplication([])
    assert app is not None
    root = QWidget()
    stack = QStackedWidget(root)
    root._wtStacked = stack
    edits = []
    modes = []
    for _i in range(2):
        page = QWidget()
        stack.addWidget(page)
        path = QTextEdit(page)
        path.setObjectName("textEdit_SavePath")
        stop = QTextEdit(page)
        stop.setObjectName("textEdit_StopTime")
        names = QTextEdit(page)
        names.setObjectName("textEdit_FileNameList")
        mode = QComboBox(page)
        mode.setObjectName("comboBox_recording_mode")
        mode.addItem("一条线连续录（单文件）")
        mode.addItem("分开录（多文件/逐点存盘）")
        edits.append((path, stop, names))
        modes.append(mode)
    folder = tmp_path / "pages"
    widgets = prepare_wt_save_widgets(
        {
            "textEdit_SavePath": str(folder),
            "textEdit_StopTime": "00:02:00",
            "textEdit_FileNameList": "OF_curve",
            "comboBox_S3_record_mode": "分开录（多文件/逐点存盘）",
            "comboBox_AutoSave": "自动保存",
        },
        "guopinjiangzai",
    )
    apply_wt_save_to_dialog(root, widgets)
    for path, stop, names in edits:
        assert path.toPlainText() == widgets["textEdit_SavePath"]
        assert stop.toPlainText() == "00:02:00"
        assert names.toPlainText() == "OF_curve"
    for mode in modes:
        assert mode.currentIndex() == 1
    assert folder.is_dir()
