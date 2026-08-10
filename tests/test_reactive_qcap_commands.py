# -*- coding: utf-8 -*-
"""无功能力范围：功率阶梯 × 极限 cosφ 命令构建（无 UI）。"""

from utils.reactive_qcap_commands import (
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
