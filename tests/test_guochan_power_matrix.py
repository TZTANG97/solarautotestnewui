# -*- coding: utf-8 -*-
"""国产电源按品牌交叉模拟（不连真机）。

覆盖：
- AC Chroma：原生 SCPI 序列可解析
- AC 爱科：ItechTranslator 严格映射（拒绝 VOLT:OFFS 等误匹配）
- DC Chroma/Itech：模式前缀与主程序 command_list_DC 一致
- DC 蓝点：OUTP / SYST:MODE；拒绝致茂 IVC 命令
- P0/P2/P3 菜单 × AC×DC 矩阵
"""

from __future__ import annotations

import re
from typing import Any

import pytest

from scpi_to_modbustcp import BluesightTranslator, ItechTranslator
from utils.guochan_sim_matrix import (
    AC_BRANDS,
    CHROMA_ONLY_AC_CMDS,
    CHROMA_ONLY_DC_CMDS,
    DC_BRANDS,
    DC_MODE_PREAMBLE,
    P0_MENUS,
    P2_MENUS,
    P3_MENUS,
    ac_sequence_for_menu,
    ac_smoke_sequence,
    ac_startup_three_phase,
    ac_three_phase_nsel_sequence,
    bluesight_stc_from_iv,
    dc_bluesight_smoke_sequence,
    dc_iv_shape_for_brand,
    is_chroma_only_ac,
    is_chroma_only_dc,
    p0_matrix_cases,
    p2_matrix_cases,
    p3_matrix_cases,
)


class _Ok:
    def isError(self) -> bool:
        return False


class FakeModbusClient:
    """记录 write_register / write_registers，供 Translator 离线映射。"""

    def __init__(self) -> None:
        self.writes: list[tuple[str, int, Any]] = []

    def write_register(self, address: int, value: int, device_id: int = 1, **_kw) -> _Ok:
        self.writes.append(("reg", address, value))
        return _Ok()

    def write_registers(self, address: int, values: list[int], device_id: int = 1, **_kw) -> _Ok:
        self.writes.append(("regs", address, list(values)))
        return _Ok()


_SCPI_OK = re.compile(
    r"^(?:\*RST|\*CLS|OUTP (?:ON|OFF)|SYST:(?:RUN|STANDBY|POWER ON|POWER OFF)|"
    r"INST:PHASE (?:SINGLE|THREE)|INST:EDIT (?:ALL|EACH)|INST:NSEL \d+|"
    r"VOLT [0-9.]+|FREQ [0-9.]+)$",
    re.I,
)


def _assert_chroma_ac(cmds: list[str]) -> None:
    for c in cmds:
        assert _SCPI_OK.match(c.strip()), f"Chroma AC 非法 SCPI: {c!r}"


def _run_itech_sequence(cmds: list[str]) -> FakeModbusClient:
    client = FakeModbusClient()
    tr = ItechTranslator(client)
    for c in cmds:
        ok, trace = tr.translate(c)
        assert ok, f"爱科映射失败: {c!r} trace={trace}"
    return client


def _run_bluesight_sequence(cmds: list[str]) -> FakeModbusClient:
    client = FakeModbusClient()
    tr = BluesightTranslator(client, device_id=1)
    for c in cmds:
        ok, msg = tr.translate(c)
        assert ok, f"蓝点映射失败: {c!r} -> {msg}"
    return client


# ----- 基础 Translator -----


def test_itech_single_phase_smoke():
    client = _run_itech_sequence(ac_smoke_sequence(single_phase=True))
    addrs = {w[1] for w in client.writes}
    assert ItechTranslator.REG_PHASE_MODE in addrs
    assert ItechTranslator.REG_CONTROL in addrs
    assert ItechTranslator.REG_FREQ in addrs


def test_itech_single_phase_ignores_edit_all():
    client = FakeModbusClient()
    tr = ItechTranslator(client)
    assert tr.translate("INST:PHASE SINGLE")[0]
    n_before = len(client.writes)
    ok, _ = tr.translate("INST:EDIT ALL")
    assert ok
    assert len(client.writes) == n_before


def test_itech_three_phase_edit_all_writes_linked_mode():
    """三相 EDIT ALL 须写 0x0C48=0x0001（联动），否则残留 EACH 的 0x0002 会像只有一相动。"""
    client = FakeModbusClient()
    tr = ItechTranslator(client)
    assert tr.translate("INST:PHASE THREE")[0]
    assert tr.translate("INST:EDIT EACH")[0]
    assert any(
        w[0] == "reg" and w[1] == ItechTranslator.REG_PHASE_MODE and w[2] == 0x0002
        for w in client.writes
    )
    ok, _ = tr.translate("INST:EDIT ALL")
    assert ok
    assert tr.edit_mode == "ALL"
    assert any(
        w[0] == "reg" and w[1] == ItechTranslator.REG_PHASE_MODE and w[2] == 0x0001
        for w in client.writes
    )


def test_itech_three_phase_volt_writes_abc():
    client = _run_itech_sequence(ac_startup_three_phase(220, 50))
    volt_bases = {
        w[1]
        for w in client.writes
        if w[0] == "regs"
        and w[1]
        in (
            ItechTranslator.REG_VOLT_A,
            ItechTranslator.REG_VOLT_B,
            ItechTranslator.REG_VOLT_C,
        )
    }
    assert volt_bases == {
        ItechTranslator.REG_VOLT_A,
        ItechTranslator.REG_VOLT_B,
        ItechTranslator.REG_VOLT_C,
    }


def test_itech_freq_scale_x1000():
    client = FakeModbusClient()
    tr = ItechTranslator(client)
    tr.auto_save = False
    assert tr.translate("FREQ 50.5")[0]
    freq_writes = [w for w in client.writes if w[0] == "regs" and w[1] == ItechTranslator.REG_FREQ]
    assert freq_writes
    assert freq_writes[0][2][1] == 50500


def test_itech_rejects_chroma_volt_extensions():
    """致茂 VOLT:* / LIST 等不得被误解析为设压（曾误把 VOLT:OFFS 0 写成 0V）。"""
    client = FakeModbusClient()
    tr = ItechTranslator(client)
    tr.auto_save = False
    for cmd in CHROMA_ONLY_AC_CMDS:
        ok, _ = tr.translate(cmd)
        assert not ok, f"爱科应拒绝: {cmd!r}"
    volt_writes = [
        w
        for w in client.writes
        if w[0] == "regs"
        and w[1]
        in (
            ItechTranslator.REG_VOLT_A,
            ItechTranslator.REG_VOLT_B,
            ItechTranslator.REG_VOLT_C,
        )
    ]
    assert volt_writes == []


@pytest.mark.parametrize(
    "cmd",
    [
        "VOLT:OFFS 0",
        "VOLT:MODE LIST",
        "VOLT",
        "VOLT 230 1",
        "FREQ:MODE LIST",
        "FREQ",
        "INST:NSEL",
        "INST:NSEL 4",
        "INST:NSEL ABC",
    ],
)
def test_itech_strict_reject(cmd: str):
    tr = ItechTranslator(FakeModbusClient())
    ok, _ = tr.translate(cmd)
    assert not ok


@pytest.mark.parametrize("cmd", ["VOLT 230", "VOLTAGE 230.5", "FREQ 50", "FREQUENCY 50.2"])
def test_itech_accepts_canonical_setpoints(cmd: str):
    tr = ItechTranslator(FakeModbusClient())
    ok, _ = tr.translate(cmd)
    assert ok


def test_itech_three_phase_nsel_path():
    _run_itech_sequence(ac_three_phase_nsel_sequence())


def test_bluesight_smoke():
    client = _run_bluesight_sequence(dc_bluesight_smoke_sequence())
    addrs = {w[1] for w in client.writes if w[0] == "reg"}
    assert BluesightTranslator.REG_OUTP in addrs
    assert BluesightTranslator.REG_OUTPUT_MODE in addrs


@pytest.mark.parametrize("cmd", CHROMA_ONLY_DC_CMDS)
def test_bluesight_rejects_chroma_iv(cmd: str):
    tr = BluesightTranslator(FakeModbusClient(), device_id=1)
    ok, msg = tr.translate(cmd)
    assert not ok, f"蓝点应拒绝致茂命令: {cmd!r} msg={msg}"


def test_dc_mode_preamble_matches_main():
    assert DC_MODE_PREAMBLE["Chroma"] == ["OUTP:MODE TABLE", "IVCurve:SELect 1"]
    assert DC_MODE_PREAMBLE["Itech"] == ["SOL 0", "SOL 1"]
    assert DC_MODE_PREAMBLE["Bluesight"] == ["SYST:MODE SAS"]


def test_dc_iv_shape_brand_policy():
    chroma = dc_iv_shape_for_brand("Chroma")
    assert any(c.upper().startswith("IVC:") for c in chroma)
    itech = dc_iv_shape_for_brand("Itech")
    assert any(c.upper().startswith("SOL:USER") for c in itech)
    assert not any(is_chroma_only_dc(c) for c in itech)
    bs = dc_iv_shape_for_brand("Bluesight")
    assert any(c.upper().startswith("BLUESIGHT:STC") for c in bs)
    assert not any(is_chroma_only_dc(c) for c in bs)


def test_bluesight_stc_from_iv_dialog_points():
    triple = bluesight_stc_from_iv("650", "12.3", "800", "13.5", "100")
    assert triple is not None
    pmpp_kw, umpp, ff = triple
    assert abs(pmpp_kw - 650 * 12.3 / 1000.0) < 1e-9
    assert umpp == 650.0
    assert 0.50 <= ff <= 0.95
    half = bluesight_stc_from_iv("650", "12.3", "800", "13.5", "50")
    assert half is not None
    assert abs(half[0] - pmpp_kw * 0.5) < 1e-9
    assert bluesight_stc_from_iv("0", "10") is None


def test_bluesight_dcgetiv_scales_device_page_cache():
    """设备页缓存为 100% 基准时，工况点功率%必须改写 Pmpp（固定PF/无功阶梯）。"""
    pytest.importorskip("PyQt5.QtWidgets")
    import SCPITestWave as sw

    prev_stc = dict(sw.bluesight_stc_params)
    prev_factor = getattr(sw, "per_dc_factor", None)
    sw.per_dc_factor = {"0": "Bluesight", "1": "", "2": "", "3": ""}
    try:
        sw.bluesight_stc_params[0] = {"pmpp": 7.99955, "umpp": 650.0, "ff": 0.8006539292462277}
        full = sw.DCGetIVValueFunction("650", "12.3", "800", "13.5", "100", 0)
        mid = sw.DCGetIVValueFunction("650", "12.3", "800", "13.5", "75", 0)
        low = sw.DCGetIVValueFunction("650", "12.3", "800", "13.5", "20", 0)
        assert full == ["BLUESIGHT:STC 7.99955 650.0 0.8006539292462277"]
        p_mid = float(mid[0].split()[1])
        p_low = float(low[0].split()[1])
        assert abs(p_mid - 7.99955 * 0.75) < 1e-9
        assert abs(p_low - 7.99955 * 0.20) < 1e-9
        assert sw.bluesight_stc_params[0]["pmpp"] == 7.99955
    finally:
        sw.bluesight_stc_params.clear()
        sw.bluesight_stc_params.update(prev_stc)
        if prev_factor is None:
            delattr(sw, "per_dc_factor")
        else:
            sw.per_dc_factor = prev_factor


# ----- P0 / P2 / P3 矩阵 -----


@pytest.mark.parametrize("menu", P0_MENUS)
@pytest.mark.parametrize("ac_brand", AC_BRANDS)
def test_p0_ac_brand_smoke(menu: str, ac_brand: str):
    cmds = ac_smoke_sequence(single_phase=True)
    assert menu
    if ac_brand == "Chroma":
        _assert_chroma_ac(cmds)
    else:
        _run_itech_sequence(cmds)


@pytest.mark.parametrize("menu", P0_MENUS)
@pytest.mark.parametrize("dc_brand", DC_BRANDS)
def test_p0_dc_brand_smoke(menu: str, dc_brand: str):
    assert menu
    preamble = DC_MODE_PREAMBLE[dc_brand]
    if dc_brand == "Chroma":
        assert "OUTP:MODE TABLE" in preamble
    elif dc_brand == "Itech":
        assert preamble == ["SOL 0", "SOL 1"]
    else:
        assert preamble == ["SYST:MODE SAS"]
        _run_bluesight_sequence(dc_bluesight_smoke_sequence())


def _assert_matrix_case(case: dict) -> None:
    if case["ac_brand"] == "Chroma":
        _assert_chroma_ac(case["ac_cmds"])
        assert not any(is_chroma_only_ac(c) for c in case["ac_cmds"])
    else:
        _run_itech_sequence(case["ac_cmds"])
        for c in case["ac_cmds"]:
            assert not is_chroma_only_ac(c)

    if case["dc_brand"] == "Bluesight":
        assert case["dc_preamble"] == ["SYST:MODE SAS"]
        _run_bluesight_sequence(case["dc_bluesight_cmds"])
        for c in case["dc_iv_shape"]:
            if c.upper().startswith("BLUESIGHT:STC"):
                continue
            if c.upper().startswith("SYST:MODE") or c.upper() in ("OUTP ON", "OUTP OFF"):
                ok, msg = BluesightTranslator(FakeModbusClient(), device_id=1).translate(c)
                assert ok, msg
    else:
        assert case["dc_preamble"] == DC_MODE_PREAMBLE[case["dc_brand"]]


@pytest.mark.parametrize(
    "case",
    p0_matrix_cases(),
    ids=lambda c: f"{c['menu']}|AC={c['ac_brand']}|DC={c['dc_brand']}",
)
def test_p0_full_matrix(case: dict):
    _assert_matrix_case(case)


def test_matrix_case_count():
    assert len(p0_matrix_cases()) == len(P0_MENUS) * len(AC_BRANDS) * len(DC_BRANDS)
    assert len(p2_matrix_cases()) == len(P2_MENUS) * len(AC_BRANDS) * len(DC_BRANDS)
    assert len(p3_matrix_cases()) == len(P3_MENUS) * len(AC_BRANDS) * len(DC_BRANDS)


@pytest.mark.parametrize(
    "case",
    p2_matrix_cases(),
    ids=lambda c: f"{c['menu']}|AC={c['ac_brand']}|DC={c['dc_brand']}",
)
def test_p2_rapid_volt_matrix(case: dict):
    assert "VOLT 207" in case["ac_cmds"]
    _assert_matrix_case(case)


@pytest.mark.parametrize(
    "case",
    p3_matrix_cases(),
    ids=lambda c: f"{c['menu']}|AC={c['ac_brand']}|DC={c['dc_brand']}",
)
def test_p3_extended_menu_matrix(case: dict):
    assert case["ac_cmds"] == ac_sequence_for_menu(case["menu"])
    _assert_matrix_case(case)


@pytest.mark.parametrize("ac_brand", AC_BRANDS)
@pytest.mark.parametrize("dc_brand", DC_BRANDS)
def test_brand_cross_policy(ac_brand: str, dc_brand: str):
    """6 种 AC×DC 组合的能力边界摘要（真机联调检查表）。"""
    assert ac_brand in AC_BRANDS
    assert dc_brand in DC_BRANDS
    shape = dc_iv_shape_for_brand(dc_brand)
    if dc_brand == "Bluesight":
        assert DC_MODE_PREAMBLE[dc_brand] == ["SYST:MODE SAS"]
        assert any("BLUESIGHT:STC" in c.upper() for c in shape)
    elif dc_brand == "Itech":
        assert DC_MODE_PREAMBLE[dc_brand][0].startswith("SOL")
        assert any(c.upper().startswith("SOL:USER") for c in shape)
    else:
        assert "OUTP:MODE TABLE" in DC_MODE_PREAMBLE[dc_brand]


def test_bluesight_cv_860v_uint32_le():
    """原载恒压 860V：须写 uint32 LE [0x4FF0, 0x0001]，禁止截成 204.64V。"""
    from scpi_to_modbustcp import BluesightTranslator

    tr = BluesightTranslator(FakeModbusClient(), device_id=1)
    words = tr.build_original_load_param_words(0, voltage_v=860.0, r_internal_ohm=0.0)
    assert words == [0x4FF0, 0x0001, 0x0000, 0x0000]
    ok, msg = tr.write_original_load_params(0, voltage_v=860.0, r_internal_ohm=0.0)
    assert ok, msg
    regs = [w for w in tr.client.writes if w[0] == "regs" and w[1] == 0x0FAA]
    assert regs and regs[0][2] == [0x4FF0, 0x0001, 0x0000, 0x0000]


def test_bluesight_cv_650v_compat_high_word_zero():
    """低电压时高字为 0，兼容旧抓包 [U×100, 0, …]。"""
    from scpi_to_modbustcp import BluesightTranslator

    tr = BluesightTranslator(FakeModbusClient(), device_id=1)
    words = tr.build_original_load_param_words(0, voltage_v=650.0, r_internal_ohm=0.0)
    assert words == [0xFDE8, 0x0000, 0x0000, 0x0000]


def test_bluesight_curve_umpp_860_uint32_le():
    from scpi_to_modbustcp import BluesightCurveSTC, BluesightTranslator

    words = BluesightTranslator.build_curve_words(
        BluesightCurveSTC(pmpp_stc_kw=8.0, umpp_stc_v=860.0, fill_factor=0.8)
    )
    # [0]=mode, [1][2]=Pmpp uint32, [3][4]=Umpp uint32
    assert words[3:5] == [0x4FF0, 0x0001]
    assert words[1:3] == [8000, 0]
