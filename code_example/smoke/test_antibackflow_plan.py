# -*- coding: utf-8 -*-
"""防逆流 UNE 217001 命令计划冒烟（无硬件）。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PyQt5 import QtWidgets

from dialogs.Dialog_thaantibackflow import Ui_Dialog_thaantibackflow
from utils.antibackflow_commands import (
    antibackflow_recommended_filenames,
    build_antibackflow_plan,
    collect_scenario_points,
)
from utils.wt_recording_mode import MODE_CONTINUOUS


class _DummyApp:
    pass


def main():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    dlg = QtWidgets.QDialog()
    ui = Ui_Dialog_thaantibackflow()
    ui.setupUi(dlg)

    # 短时间便于冒烟
    ui.textEdit_S3_TIME_2.setText("2")
    ui.comboBox_S3_TIME_2.setCurrentText("秒")
    ui.textEdit_OpWait.setText("1")
    ui.comboBox_OpWait.setCurrentText("秒")
    ui.checkBox_S1.setChecked(True)
    ui.checkBox_S2.setChecked(True)
    ui.checkBox_S3.setChecked(True)
    ui.checkBox_S_END.setChecked(True)
    # 只跑 5.1 缩短点数
    ui.checkBox_S5_1.setChecked(True)
    ui.checkBox_S5_2.setChecked(False)
    ui.checkBox_S5_3.setChecked(False)
    ui.checkBox_S5_4.setChecked(False)
    ui.textEdit_PowerLadder.setText("100,0")

    pts = collect_scenario_points(ui, dwell_01s=20, op_wait_01s=10)
    assert len(pts) == 2, pts
    names = antibackflow_recommended_filenames(ui, MODE_CONTINUOUS)
    assert names == ["AntiBackflow_BR"], names

    plan = build_antibackflow_plan(
        ui,
        wt_config_dict={"textEdit_FileNameList": ""},
        str_add_flag="0",
        project_change="0",
        existing_commands=[],
    )
    assert plan["ok"], plan.get("error")
    assert plan["file_names"] == ["AntiBackflow_BR"], plan["file_names"]
    assert any(r and r[0] == "Upper_WT_Config" for r in plan["commands"])
    assert any(r and r[0] == "AC" for r in plan["commands"])
    print("OK points=%d cmds=%d files=%s dwell_01s=%s" % (
        len(pts), len(plan["commands"]), plan["file_names"], plan["dwell_01s"]
    ))

    # 全段勾选也要能出点
    ui.checkBox_S5_2.setChecked(True)
    ui.checkBox_S5_3.setChecked(True)
    ui.checkBox_S5_4.setChecked(True)
    pts2 = collect_scenario_points(ui, 20, 10)
    assert len(pts2) > 10, len(pts2)
    print("OK full scenarios=%d" % len(pts2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
