# -*- coding: utf-8 -*-
"""国产电源 P0×品牌 软件映射模拟（不连真机）。

覆盖：
- AC Chroma：原生 SCPI 序列可解析
- AC 爱科：ItechTranslator 映射寄存器成功（含单相忽略 INST:EDIT ALL）
- DC Chroma/Itech：模式前缀与主程序 command_list_DC 一致
- DC 蓝点：OUTP / SYST:MODE 基础映射
- P0 六菜单 × AC×DC 矩阵冒烟
"""

from __future__ import annotations

import re
from typing import Any

import pytest

from scpi_to_modbustcp import BluesightTranslator, ItechTranslator
from utils.guochan_sim_matrix import (
    AC_BRANDS,
    DC_BRANDS,
    DC_MODE_PREAMBLE,
    P0_MENUS,
    P2_MENUS,
    ac_smoke_sequence,
    ac_startup_single_phase,
    ac_startup_three_phase,
    dc_bluesight_smoke_sequence,
    p0_matrix_cases,
    p2_matrix_cases,
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
    assert ItechTranslator.REG_PHASE_MODE in addrs  # 单相写独立模式
    assert ItechTranslator.REG_CONTROL in addrs
    assert ItechTranslator.REG_FREQ in addrs


def test_itech_single_phase_ignores_edit_all():
    client = FakeModbusClient()
    tr = ItechTranslator(client)
    assert tr.translate("INST:PHASE SINGLE")[0]
    n_before = len(client.writes)
    ok, _ = tr.translate("INST:EDIT ALL")
    assert ok
    assert len(client.writes) == n_before  # 空操作，不写寄存器


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
    assert freq_writes[0][2][1] == 50500  # ×1000


def test_bluesight_smoke():
    client = _run_bluesight_sequence(dc_bluesight_smoke_sequence())
    addrs = {w[1] for w in client.writes if w[0] == "reg"}
    assert BluesightTranslator.REG_OUTP in addrs
    assert BluesightTranslator.REG_OUTPUT_MODE in addrs


def test_dc_mode_preamble_matches_main():
    # 与 SCPITestWave 初始化块约定一致（避免主程序巨大 import）
    assert DC_MODE_PREAMBLE["Chroma"] == ["OUTP:MODE TABLE", "IVCurve:SELect 1"]
    assert DC_MODE_PREAMBLE["Itech"] == ["SOL 0", "SOL 1"]
    assert DC_MODE_PREAMBLE["Bluesight"] == []


# ----- P0 矩阵 -----


@pytest.mark.parametrize("menu", P0_MENUS)
@pytest.mark.parametrize("ac_brand", AC_BRANDS)
def test_p0_ac_brand_smoke(menu: str, ac_brand: str):
    cmds = ac_smoke_sequence(single_phase=True)
    assert menu  # 绑定菜单名，便于失败报告
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
        assert preamble == []
        _run_bluesight_sequence(dc_bluesight_smoke_sequence())


@pytest.mark.parametrize("case", p0_matrix_cases(), ids=lambda c: f"{c['menu']}|AC={c['ac_brand']}|DC={c['dc_brand']}")
def test_p0_full_matrix(case: dict):
    """6 菜单 × 2 AC × 3 DC = 36 组合：AC 映射 + DC 前缀/蓝点基础。"""
    if case["ac_brand"] == "Chroma":
        _assert_chroma_ac(case["ac_cmds"])
    else:
        _run_itech_sequence(case["ac_cmds"])

    if case["dc_brand"] == "Bluesight":
        assert case["dc_preamble"] == []
        _run_bluesight_sequence(case["dc_bluesight_cmds"])
    else:
        assert case["dc_preamble"] == DC_MODE_PREAMBLE[case["dc_brand"]]


def test_matrix_case_count():
    assert len(p0_matrix_cases()) == len(P0_MENUS) * len(AC_BRANDS) * len(DC_BRANDS)
    assert len(p2_matrix_cases()) == len(P2_MENUS) * len(AC_BRANDS) * len(DC_BRANDS)


@pytest.mark.parametrize(
    "case",
    p2_matrix_cases(),
    ids=lambda c: f"{c['menu']}|AC={c['ac_brand']}|DC={c['dc_brand']}",
)
def test_p2_rapid_volt_matrix(case: dict):
    """快速电压变化 × AC×DC：阶跃 VOLT 映射 + DC 前缀。"""
    assert "VOLT 207" in case["ac_cmds"]
    if case["ac_brand"] == "Chroma":
        _assert_chroma_ac(case["ac_cmds"])
    else:
        _run_itech_sequence(case["ac_cmds"])
    if case["dc_brand"] == "Bluesight":
        assert case["dc_preamble"] == []
        _run_bluesight_sequence(case["dc_bluesight_cmds"])
    else:
        assert case["dc_preamble"] == DC_MODE_PREAMBLE[case["dc_brand"]]
