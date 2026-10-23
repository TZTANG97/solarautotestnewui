# -*- coding: utf-8 -*-
"""Chroma Soft Panel 主从并联电流/功率上限。

双台并联：1 主 + 1 从 → NUMSLV=1 → 单元数=2 → 15.75×2=31.5A。
注意：*RST 会清掉 MSTSLV，必须在复位前查询主从状态。
"""
from __future__ import annotations

import re
from typing import Any, Optional, Tuple

_BASE_CURR_A = 15.75
_BASE_POW_W = 15750.0


def parse_mstslv_on(raw: Any) -> bool:
    s = str(raw or "").strip().upper()
    if not s:
        return False
    if s in ("ON", "1", "MASTER", "MAS", "MST"):
        return True
    if "OFF" in s or s in ("0", "SLAVE", "SLV"):
        return False
    return "ON" in s


def parse_numslv(raw: Any) -> int:
    """从机数量（不含主机）。"""
    m = re.search(r"\d+", str(raw or ""))
    if not m:
        return 0
    try:
        return max(0, int(m.group(0)))
    except ValueError:
        return 0


def parallel_unit_count(*, mstslv_on: bool, numslv: int) -> int:
    """并联单元数：独立=1；主从开启时 = 从机数 + 1。"""
    if not mstslv_on:
        return 1
    return max(1, int(numslv) + 1)


def scale_limits(units: int, *, base_curr: float = _BASE_CURR_A, base_pow: float = _BASE_POW_W) -> Tuple[float, float]:
    n = max(1, int(units or 1))
    return float(base_curr) * n, float(base_pow) * n


def probe_parallel_units(handle: Any) -> int:
    """在 *RST 之前调用：读 CONF:MSTSLV? / CONF:MSTSLV:NUMSLV? → 并联台数。"""
    if handle is None:
        return 1
    try:
        mst = handle.query("CONF:MSTSLV?")
    except Exception:
        mst = ""
    try:
        nsl = handle.query("CONF:MSTSLV:NUMSLV?")
    except Exception:
        nsl = ""
    on = parse_mstslv_on(mst)
    slaves = parse_numslv(nsl)
    units = parallel_unit_count(mstslv_on=on, numslv=slaves)
    print(
        f"[DC上限] Soft Panel 主从探测 MSTSLV={str(mst).strip()!r} "
        f"NUMSLV={str(nsl).strip()!r} → units={units}",
        flush=True,
    )
    return units


def resolve_curr_limit_after_max(handle: Any, planned: float) -> float:
    """:sour:curr:prot:high max 后读回，取 max(计划值, 读回值)。"""
    base = float(planned) if planned and float(planned) > 0 else _BASE_CURR_A
    if handle is None:
        return base
    try:
        raw = handle.query(":SOUR:CURR:PROT:HIGH?")
        m = re.search(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", str(raw or ""))
        if not m:
            return base
        qv = float(m.group(0))
        if qv > 0:
            return max(base, qv)
    except Exception as exc:
        print(f"[DC上限] Soft Panel 读回 OCP 失败: {exc}", flush=True)
    return base


def probe_and_scale_limits(handle: Any) -> Tuple[float, float, int]:
    """RST 前探测并联 → (电流上限A, 功率上限W, 台数)。"""
    units = probe_parallel_units(handle)
    curr, pow_w = scale_limits(units)
    return curr, pow_w, units
