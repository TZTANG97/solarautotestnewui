# -*- coding: utf-8 -*-
"""Smoke: 是德(Keysight) DC 品牌接线。"""
from __future__ import annotations

import ast
from pathlib import Path

from utils.dc_brand_cmd_guard import has_keysight_iv_cmds, validate_dc_cmds_for_brand
from utils.device_discovery import FoundDevice, connect_plan
from utils.iot_device_ready import KNOWN_DC_BRANDS

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    for brand in ("keysight", "Keysight", "agilent"):
        p = connect_plan(
            "dc1",
            FoundDevice(resource="USB0::0x0957::x::INSTR", brand_hint=brand),
        )
        assert p["device_type"] == "keysight", p
        print("plan", brand, "->", p["device_type"])

    assert (
        connect_plan("dc1", FoundDevice(resource="x", brand_hint="chroma"))[
            "device_type"
        ]
        == "chroma"
    )
    assert "Keysight" in KNOWN_DC_BRANDS
    assert has_keysight_iv_cmds(["SAS:MODE TABL", "SAS:TABL:ACT 1"])
    ok, reason = validate_dc_cmds_for_brand(
        "Keysight", ["SAS:MODE TABL", "OUTP:MODE TABLE"]
    )
    assert ok is False and "Chroma" in reason, (ok, reason)
    ok2, reason2 = validate_dc_cmds_for_brand("Keysight", ["SAS:MODE TABL"])
    assert ok2 is True and reason2 == "", (ok2, reason2)

    src = (ROOT / "SCPITestWave.py").read_text(encoding="utf-8")
    assert "是德(Keysight)" in src
    assert "_DC1_STACK_INDEX" in src
    assert "keysight" in src
    ast.parse(src)
    print("SCPITestWave ast ok")
    print("SMOKE_OK")


if __name__ == "__main__":
    main()
