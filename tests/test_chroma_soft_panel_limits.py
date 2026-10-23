# -*- coding: utf-8 -*-
from utils.chroma_soft_panel_limits import (
    parallel_unit_count,
    parse_mstslv_on,
    parse_numslv,
    probe_and_scale_limits,
    resolve_curr_limit_after_max,
    scale_limits,
)


def test_parse_mstslv_on():
    assert parse_mstslv_on("ON") is True
    assert parse_mstslv_on("MASTER") is True
    assert parse_mstslv_on("OFF") is False
    assert parse_mstslv_on("0") is False


def test_parallel_dual_is_31_5():
    assert parallel_unit_count(mstslv_on=True, numslv=1) == 2
    curr, pow_w = scale_limits(2)
    assert curr == 31.5
    assert pow_w == 31500.0


def test_parallel_off_is_single():
    assert parallel_unit_count(mstslv_on=False, numslv=1) == 1
    curr, _ = scale_limits(1)
    assert curr == 15.75


def test_parse_numslv():
    assert parse_numslv("1") == 1
    assert parse_numslv(" 2\n") == 2
    assert parse_numslv("") == 0


class _FakeHandle:
    def __init__(self, mst="ON", nsl="1", ocp="15.75"):
        self.mst = mst
        self.nsl = nsl
        self.ocp = ocp

    def query(self, cmd: str):
        c = str(cmd).upper()
        if "NUMSLV" in c:
            return self.nsl
        if "MSTSLV" in c:
            return self.mst
        if "CURR:PROT:HIGH" in c:
            return self.ocp
        return ""


def test_probe_and_scale_dual():
    curr, pow_w, units = probe_and_scale_limits(_FakeHandle("ON", "1"))
    assert units == 2
    assert curr == 31.5
    assert pow_w == 31500.0


def test_resolve_keeps_planned_when_readback_lower():
    # RST 后单机读回 15.75，但计划已是并联 31.5 → 保留 31.5
    assert resolve_curr_limit_after_max(_FakeHandle(ocp="15.75"), 31.5) == 31.5


def test_resolve_raises_to_readback():
    assert resolve_curr_limit_after_max(_FakeHandle(ocp="31.5"), 15.75) == 31.5
