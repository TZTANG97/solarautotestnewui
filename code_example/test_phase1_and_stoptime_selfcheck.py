# -*- coding: utf-8 -*-
"""自测：Chroma 启机 EDIT ALL + 扫压无 EDIT ALL + StopTime 墙钟（不连真机）。"""
import os
import sys
from unittest.mock import MagicMock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.modules.setdefault("PyQt5", MagicMock())
sys.modules.setdefault("PyQt5.QtWidgets", MagicMock())
sys.modules.setdefault("pyvisa", MagicMock())
sys.modules.setdefault("modbus_visa", MagicMock())
sys.modules.setdefault("scpi_visa", MagicMock())
sys.modules.setdefault("scpi_to_modbustcp", MagicMock())

from devices.ac_controller import _chroma_three_phase_command_list
from utils.voltage_adaptability_commands import (
    append_chroma_three_phase_setpoints,
    append_volt_band_brazil,
    build_voltage_adaptability_plan,
    estimate_continuous_record_01s,
    recalculate_stoptime_from_band_rows,
    extract_continuous_band_rows,
    _row_wt_async_marker,
    _empty_row,
)


def _fail(msg):
    print("FAIL:", msg)
    sys.exit(1)


def test_chroma_startup_ends_edit_all():
    cmds = _chroma_three_phase_command_list("230", "230", "230", "50")
    if cmds.count("VOLT:AC 230") != 4:
        _fail(f"expected 4x VOLT:AC 230, got {cmds.count('VOLT:AC 230')}")
    if "INST:EDIT ALL" not in cmds:
        _fail("startup missing INST:EDIT ALL")
    # EDIT ALL should be after NSEL loop
    idx_edit = cmds.index("INST:EDIT ALL")
    if cmds.index("INST:NSEL 3") >= idx_edit:
        _fail("INST:EDIT ALL should follow NSEL 3")
    print("OK chroma startup ends with EDIT ALL")


def test_sweep_no_edit_all_after_async():
    rows = []
    append_chroma_three_phase_setpoints(rows, "230", "230", "230", "50")
    append_volt_band_brazil(
        rows,
        "三相",
        "230",
        "253",
        300,
        use_rate=True,
        rate_interval_s=0.05,
        per_second_range=20,
        wt_first_trigger=True,
        chroma_61800=True,
    )
    append_volt_band_brazil(
        rows,
        "三相",
        "253",
        "230",
        300,
        use_rate=True,
        rate_interval_s=0.05,
        per_second_range=20,
        wt_first_trigger=False,
        chroma_61800=True,
    )
    append_volt_band_brazil(
        rows,
        "三相",
        "230",
        "195",
        300,
        use_rate=True,
        rate_interval_s=0.05,
        per_second_range=20,
        wt_first_trigger=False,
        chroma_61800=True,
    )
    rows.append(_row_wt_async_marker("WAIT_END"))

    async_i = next(
        i for i, r in enumerate(rows) if len(r) > 6 and str(r[6]).strip() == "ASYNC_START"
    )
    sweep_writes = [r[2] for r in rows[async_i:] if r[1] == "write"]
    if "INST:EDIT ALL" in sweep_writes:
        _fail("sweep section still has INST:EDIT ALL after ASYNC_START")
    if not any(str(w).startswith("VOLT:AC") for w in sweep_writes):
        _fail("sweep missing VOLT:AC")
    startup_writes = [r[2] for r in rows[:async_i] if r[1] == "write"]
    if startup_writes.count("INST:EDIT ALL") != 1:
        _fail(f"startup should have 1 INST:EDIT ALL, got {startup_writes.count('INST:EDIT ALL')}")
    print("OK sweep has no INST:EDIT ALL; startup has 1 EDIT ALL")


def test_stoptime_covers_20260822_band():
    import csv
    from pathlib import Path

    p = Path(ROOT) / "command_save_files/command_data/voltageadaptability_commands2026_08_22_13.csv"
    if not p.exists():
        print("SKIP stoptime replay (no 13.csv)")
        return
    rows = list(csv.reader(p.open(encoding="utf-8-sig", newline="")))
    band = extract_continuous_band_rows(rows)
    stop_str, stop_sec, wall_01s, _, _, n_dwell = recalculate_stoptime_from_band_rows(band)
    if stop_sec < 310:
        _fail(f"StopTime {stop_str} ({stop_sec}s) < 310s wall clock")
    if n_dwell < 1000:
        _fail(f"dwell steps too low: {n_dwell}")
    print(f"OK StopTime replay {stop_str} ({stop_sec}s) wall={wall_01s/10:.1f}s dwell={n_dwell}")


def test_build_plan_chroma_flags():
    try:
        from PyQt5.QtWidgets import QApplication, QDialog
        from Dialog_thaivoltageadaptability import Ui_Dialog_thaivoltageadaptability
    except ImportError as e:
        print("SKIP build_plan (no PyQt5):", e)
        return

    app = QApplication.instance() or QApplication([])
    ui = Ui_Dialog_thaivoltageadaptability()
    dialog = QDialog()
    ui.setupUi(dialog)
    ui.checkBox_S1.setChecked(True)
    ui.comboBox_S1_AC.setCurrentText("开启")
    ui.comboBox_S1_AC_2.setCurrentText("三相")
    ui.textEdit_S1_AC_VOLT.setPlainText("230")
    ui.textEdit_S1_AC_VOLT_2.setPlainText("230")
    ui.textEdit_S1_AC_VOLT_3.setPlainText("230")
    ui.textEdit_S1_AC_FR.setPlainText("50")
    ui.textEdit_S1_ACWaitTIME.setPlainText("2")
    ui.comboBox_S1_ACWaitTIME.setCurrentText("秒")
    ui.textEdit_S1_TIME.setPlainText("5")
    ui.comboBox_S1_TIME.setCurrentText("秒")
    ui.checkBox_S2.setChecked(True)
    ui.checkBox_S2_update_rate.setChecked(True)
    ui.textEdit_S2_update_rate.setPlainText("50")
    ui.comboBox_S2_update_rate.setCurrentText("毫秒")
    ui.checkBox_guoya_page.setChecked(True)
    ui.checkBox_qianya_page.setChecked(True)
    ui.textEdit_VoltageLadder_guoya.setPlainText("230-253@30")
    ui.textEdit_VoltageLadder_qianya.setPlainText("230-195@30")

    plan = build_voltage_adaptability_plan(
        ui,
        wt_config_dict={"comboBox_AutoSave": 1, "textEdit_FileNameList": "VoltAdapt_BR_5421"},
        chroma_61800=True,
    )
    if not plan.get("ok"):
        _fail(plan.get("error"))
    cmds = plan["commands"]
    async_i = next(
        i for i, r in enumerate(cmds)
        if len(r) > 6 and str(r[6]).strip() == "ASYNC_START"
    )
    writes_after = [r[2] for r in cmds[async_i:] if r[1] == "write"]
    if "INST:EDIT ALL" in writes_after:
        _fail("plan sweep still contains INST:EDIT ALL")
    stop_sec = int(round(int(plan["band_duration_01s"]) / 10.0 + 15))
    if stop_sec < 300:
        _fail(f"plan StopTime too short: {stop_sec}s")
    print(f"OK build_plan StopTime~{stop_sec}s EDIT_ALL_in_sweep=0")


if __name__ == "__main__":
    test_chroma_startup_ends_edit_all()
    test_sweep_no_edit_all_after_async()
    test_stoptime_covers_20260822_band()
    test_build_plan_chroma_flags()
    print("PHASE1_STOPTIME_SELFTEST_ALL_OK")
