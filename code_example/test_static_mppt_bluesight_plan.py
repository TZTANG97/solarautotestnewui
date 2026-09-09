# -*- coding: utf-8 -*-
"""冒烟：静态 MPPT 蓝电计划含 BLUESIGHT:STC，无 MPPT_stepS。"""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.static_mppt_commands import build_static_mppt_bluesight_plan


class _TE:
    def __init__(self, text=""):
        self._t = str(text)

    def toPlainText(self):
        return self._t


class _CB:
    def __init__(self, checked=False):
        self._c = checked

    def isChecked(self):
        return self._c


class _Combo:
    def __init__(self, text="开启"):
        self._t = text

    def currentText(self):
        return self._t


def _mk_ui():
    ui = SimpleNamespace()
    ui.radio_Mode_Bluesight = _CB(True)
    ui.radio_Mode_SoftPanel = _CB(False)
    ui.checkBox_S1 = _CB(True)
    ui.checkBox_S2 = _CB(True)
    ui.checkBox_S3 = _CB(True)
    ui.checkBox_Analyzer = _CB(True)
    ui.checkBox_S_End = _CB(True)
    ui.checkBox_S_End_DC = _CB(True)
    ui.comboBox_S_End_AC = _Combo("关闭")
    ui.comboBox_S_End_DC = _Combo("关闭")
    ui.comboBox_S1_AC = _Combo("开启")
    ui.comboBox_S1_AC_2 = _Combo("三相")
    ui.comboBox_S1_DC_START = _Combo("开启")
    ui.comboBox_S1_TIME = _Combo("分钟")
    ui.comboBox_S1_ACWaitTIME = _Combo("秒")
    ui.textEdit_S1_TIME = _TE("1")
    ui.textEdit_S1_ACWaitTIME = _TE("3")
    ui.textEdit_S1_AC_VOLT = _TE("230")
    ui.textEdit_S1_AC_VOLT_2 = _TE("230")
    ui.textEdit_S1_AC_VOLT_3 = _TE("230")
    ui.textEdit_S1_AC_FR = _TE("50")
    ui.textEdit_S3_PER_H = _TE("0")
    ui.textEdit_S3_PER_M = _TE("5")
    ui.textEdit_S3_TOTAL_H = _TE("0")
    ui.textEdit_S3_TOTAL_M = _TE("30")
    ui.comboBox_S3_record_mode = SimpleNamespace(currentIndex=lambda: 0)

    for ch in range(1, 5):
        setattr(ui, "checkBox_S1_DC%d" % ch, _CB(ch == 1))
        for band in ("Vmin", "Vnom", "Vmax"):
            setattr(ui, "checkBox_S1_DC%d_%s" % (ch, band), _CB(band == "Vnom" and ch == 1))

    for band, vals in (
        ("Vnom", ("650", "12.3", "800", "13.5")),
        ("Vmin", ("500", "12.3", "650", "13.5")),
        ("Vmax", ("750", "12.3", "900", "13.5")),
    ):
        setattr(ui, "textEdit_BS_%s_Vmp" % band, _TE(vals[0]))
        setattr(ui, "textEdit_BS_%s_Imp" % band, _TE(vals[1]))
        setattr(ui, "textEdit_BS_%s_Voc" % band, _TE(vals[2]))
        setattr(ui, "textEdit_BS_%s_Isc" % band, _TE(vals[3]))

    for name, pct in (
        ("checkBox_S2_Pn_100", True),
        ("checkBox_S2_Pn_75", False),
        ("checkBox_S2_Pn_50", False),
        ("checkBox_S2_Pn_30", False),
        ("checkBox_S2_Pn_25", False),
        ("checkBox_S2_Pn_20", False),
        ("checkBox_S2_Pn_10", False),
        ("checkBox_S2_Pn_5", False),
    ):
        setattr(ui, name, _CB(pct))

    ui.radioButton_S2_WT3000 = _CB(True)
    ui.radioButton_S2_WT1800 = _CB(False)
    ui.radioButton_S2_WT1806E = _CB(False)
    ui.radioButton_S2_WT5000 = _CB(False)
    return ui


def _bluesight_iv(vmp, imp, voc, isc, pf, dc_num):
    scale = float(pf) / 100.0
    pmpp = float(vmp) * float(imp) * scale / 1000.0
    return "ok", [
        "SYST:MODE SAS",
        "BLUESIGHT:STC %.5f %.1f 0.8" % (pmpp, float(vmp)),
    ]


def main():
    ui = _mk_ui()
    plan = build_static_mppt_bluesight_plan(
        ui,
        wt_config_dict={"textEdit_FileNameList": ""},
        str_add_flag="0",
        project_change="0",
        dc_iv_resolver=_bluesight_iv,
        per_dc_factor={"0": "Bluesight"},
    )
    assert plan["ok"], plan.get("error") or plan.get("dc_errors")
    cmds = " | ".join(str(r[2]) for r in plan["commands"] if len(r) > 2)
    joined0 = " | ".join(str(r[0]) for r in plan["commands"])
    assert "BLUESIGHT:STC" in cmds, cmds
    assert "MPPT_stepS" not in joined0, joined0
    assert plan["file_names"] == ["StaticMPPT_BR"], plan["file_names"]
    assert plan["wt_continuous"] is True
    assert plan["wt_rounds"] == 1
    assert any(r[6] == "ASYNC_START" for r in plan["commands"] if len(r) > 6)
    assert any(r[6] == "WAIT_END" for r in plan["commands"] if len(r) > 6)
    # StopTime 余量：1 点 × 5min + 90s = 390s
    stop_sec = int(round(1 * plan["dwell_01s"] / 10.0 + 90))
    assert stop_sec == 390, stop_sec
    print("OK static_mppt bluesight plan")
    print("  points", plan["point_metas"])
    print("  dwell_01s", plan["dwell_01s"], "stop_sec", stop_sec)
    print("  cmd_count", len(plan["commands"]))


if __name__ == "__main__":
    main()
