# -*- coding: utf-8 -*-
"""无功能力范围：功率阶梯 × 极限 cosφ 命令构建（无 UI）。"""

from types import SimpleNamespace

from utils.reactive_qcap_commands import (
    build_reactive_qcap_plan,
    default_dc_iv_resolver,
    parse_power_ladder,
    selected_cos_labels,
)


def test_parse_power_ladder_comma_and_space():
    assert parse_power_ladder("10,20, 30，40") == [10.0, 20.0, 30.0, 40.0]
    assert parse_power_ladder("10% 20%") == [10.0, 20.0]
    assert parse_power_ladder("") == []
    assert parse_power_ladder("# comment\n50") == [50.0]


def test_default_dc_iv_resolver_chroma_chain():
    code, cmds = default_dc_iv_resolver("400", "10", "450", "12", "50", 0)
    assert code == "ok"
    assert cmds[0] == "OUTP:MODE TABLE"
    assert "IVC:IT" in cmds[1]
    assert "IVC:VT" in cmds[2]
    assert cmds[3] == "IVCurve:SELect 1"
    assert "5.000" in cmds[1]
    assert "6.000" in cmds[1]


def test_default_dc_iv_resolver_errors():
    assert default_dc_iv_resolver("400", "12", "450", "10", "100", 0)[0] == "err1"
    assert default_dc_iv_resolver("400", "10", "450", "2000", "100", 0)[0] == "err2"


class _FakeCB:
    def __init__(self, checked):
        self._c = checked

    def isChecked(self):
        return self._c


def test_selected_cos_labels():
    ui = type(
        "U",
        (),
        {
            "checkBox_cos_pos09": _FakeCB(True),
            "checkBox_cos_neg09": _FakeCB(True),
            "checkBox_cos_1": _FakeCB(False),
        },
    )()
    assert selected_cos_labels(ui) == ["cos0.9", "cos-0.9"]


def _qcap_ui(*, dew_radio, stale_wt_mode=False):
    """S2 开、S1/S3 关。页内 WT3000 单选默认勾着，用来交叉德威创模式。"""
    return SimpleNamespace(
        checkBox_S1=_FakeCB(False),
        checkBox_S2=_FakeCB(True),
        checkBox_S3=_FakeCB(False),
        checkBox_S_END=_FakeCB(False),
        radio_dewetron=_FakeCB(dew_radio),
        radio_wt=_FakeCB(False),
        radio_wt3000=_FakeCB(not dew_radio),
        radioButton_S2_WT3000=_FakeCB(True),
        comboBox_S1_AC_2=SimpleNamespace(currentText=lambda: "三相"),
        analyzerModeSection=SimpleNamespace(
            is_dewetron_mode=lambda: False,
            current_mode=lambda: "wt3000" if stale_wt_mode or not dew_radio else "dewetron",
        ),
    )


def test_dewetron_plan_skips_wt_soft_panel_even_if_wt3000_radio_stays_checked():
    plan = build_reactive_qcap_plan(
        _qcap_ui(dew_radio=True, stale_wt_mode=True),
        str_add_flag="0",
        project_change="0",
    )
    assert plan["ok"]
    assert all(row[0] != "Upper_WT_Config" for row in plan["commands"])
    assert plan["wt_type"] is None
    assert plan["test_program"] == []
    assert plan["wt_is_checked"] == "1"


def test_wt_plan_still_starts_with_soft_panel_config():
    plan = build_reactive_qcap_plan(
        _qcap_ui(dew_radio=False),
        str_add_flag="0",
        project_change="0",
    )
    assert plan["ok"]
    assert plan["commands"][0][0] == "Upper_WT_Config"
    assert plan["wt_type"] == "WT3000"
