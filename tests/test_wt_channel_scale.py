# -*- coding: utf-8 -*-
"""WT 比例系数在连接页填写，并写入配置档。"""
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def test_scale_commands_follow_the_manual(tmp_path, monkeypatch):
    monkeypatch.setenv("SOLARAUTOTEST_WT_SCALE", str(tmp_path / "wt_scale.ini"))
    from utils.wt_channel_scale import (
        format_scale_factor,
        load_saved_scales,
        max_scale_element,
        save_saved_scales,
        scaling_commands,
    )

    assert format_scale_factor("100.0") == "100"
    assert format_scale_factor("1") == "1"
    assert format_scale_factor("") is None
    assert format_scale_factor("0") is None
    assert scaling_commands("Thai_WT5000_Config", {}) == []
    assert max_scale_element("Thai_WT3000E_Config") == 4
    assert max_scale_element("Thai_WT1800_Config") == 6
    assert max_scale_element("Thai_WT5000_Config") == 7

    commands = scaling_commands(
        "Thai_WT3000E_Config",
        {
            "lineEdit_wt_vt_1": "100",
            "lineEdit_wt_ct_2": "20",
            "lineEdit_wt_vt_3": "bad",
            "lineEdit_wt_vt_5": "8",
        },
    )
    assert commands == [
        ":INPUT:SCALING:STATE:ELEMENT1 ON",
        ":INPUT:SCALING:VT:ELEMENT1 100",
        ":INPUT:SCALING:STATE:ELEMENT2 ON",
        ":INPUT:SCALING:CT:ELEMENT2 20",
    ]
    assert all("ELEMENT5" not in cmd for cmd in commands)
    assert all(not cmd.startswith(":SCALING:") for cmd in commands)

    save_saved_scales({"lineEdit_wt_vt_1": "100", "lineEdit_wt_ct_1": "20"})
    saved = load_saved_scales()
    assert saved["lineEdit_wt_vt_1"] == "100"
    assert saved["lineEdit_wt_ct_1"] == "20"
    assert (tmp_path / "wt_scale.ini").is_file()


def test_connection_page_remembers_scale_and_experiment_pages_do_not(tmp_path, monkeypatch):
    monkeypatch.setenv("SOLARAUTOTEST_WT_SCALE", str(tmp_path / "wt_scale.ini"))
    pytest.importorskip("PyQt5")
    from PyQt5.QtWidgets import QApplication, QWidget

    from components.wt_config_content import build_wt3000_content, build_wt5000_content
    from components.wt_scale_group import build_connection_scale_panel
    from utils.ui_field_helpers import history_key_for_object_name
    from utils.wt_channel_scale import load_saved_scales, scales_for_run, scaling_commands

    app = QApplication.instance() or QApplication([])
    assert app is not None
    assert history_key_for_object_name("lineEdit_WT3000_IP") == "wt.ip"
    assert history_key_for_object_name("lineEdit_wt_vt_1") is None

    host = QWidget()
    panel = build_connection_scale_panel(host)
    assert host.lineEdit_wt_vt_1.text() == "1"
    assert host.lineEdit_wt_ct_7.text() == "1"
    # 下发按钮挂在 host 上，由时间线单独一行展示（不嵌在 panel 子树里）
    assert getattr(host, "pushButton_wt_scale_apply", None) is not None
    assert host.pushButton_wt_scale_apply.objectName() == "pushButton_wt_scale_apply"
    assert host.pushButton_wt_scale_probe.objectName() == "pushButton_wt_scale_probe"
    assert host.pushButton_wt_scale_once.objectName() == "pushButton_wt_scale_once"
    host.lineEdit_wt_vt_1.setText("100")
    host.lineEdit_wt_ct_2.setText("20")
    panel.persist_scales()
    assert load_saved_scales()["lineEdit_wt_vt_1"] == "100"

    host2 = QWidget()
    panel2 = build_connection_scale_panel(host2)
    assert host2.lineEdit_wt_vt_1.text() == "100"
    assert host2.lineEdit_wt_ct_2.text() == "20"
    assert scales_for_run(
        "Thai_WT3000E_Config",
        {"lineEdit_wt_vt_1": "999"},
        host2,
    )["lineEdit_wt_vt_1"] == "100"
    assert scales_for_run("", {"lineEdit_wt_vt_1": "999"})["lineEdit_wt_vt_1"] == "100"
    commands = scaling_commands("Thai_WT5000_Config", load_saved_scales())
    assert ":INPUT:SCALING:VT:ELEMENT1 100" in commands
    assert ":INPUT:SCALING:CT:ELEMENT2 20" in commands
    panel.deleteLater()
    panel2.deleteLater()
    host.deleteLater()
    host2.deleteLater()

    experiment = QWidget()
    page = build_wt5000_content(experiment)
    assert getattr(experiment, "lineEdit_wt_vt_1", None) is None
    page.deleteLater()
    experiment.deleteLater()

    wt3000 = QWidget()
    page3000 = build_wt3000_content(wt3000)
    assert getattr(wt3000, "lineEdit_wt_vt_1", None) is None
    page3000.deleteLater()
    wt3000.deleteLater()
