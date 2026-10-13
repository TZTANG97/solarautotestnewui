# -*- coding: utf-8 -*-
"""剩余试验国家标准模块冒烟（与 IOT profiles 对齐）。"""
from __future__ import annotations

import importlib
import pytest

STD8 = {
    "thai",
    "de_vde",
    "br_ord140",
    "en50549",
    "as_nzs",
    "it_cei",
    "uk_g99",
    "iec61727",
}

BATCH = (
    "frequencyadaptability",
    "rocof",
    "guoqianpin_immun",
    "rapidvolt",
    "lvrt",
    "phasejump",
    "staticmppt",
    "dynamicmppt",
    "reactiveqcap",
    "fixedq",
    "reactiveqin",
    "reactiveqacc",
    "activep",
    "staticqu",
    "dynamicqu",
    "testpu",
    "staticcosphi",
    "dynamiccosphi",
    "cosphibrazil",
)


@pytest.mark.parametrize("tt", BATCH)
def test_remaining_standard_module_eight_distinct(tt: str):
    mod = importlib.import_module(f"utils.iot_{tt}_standard")
    defaults = getattr(mod, f"{tt.upper()}_STANDARD_DEFAULTS")
    resolve = getattr(mod, f"resolve_{tt}_standard_id")
    apply = getattr(mod, f"apply_{tt}_standard_to_widgets")
    assert set(defaults) == STD8
    assert resolve(widgets={}) == "thai"
    assert resolve(params={"solarStandard": "iec61727"}) == "iec61727"
    assert resolve(widgets={"solarStandard": "de_vde"}) == "de_vde"
    sids = sorted(defaults)
    for i, a in enumerate(sids):
        for b in sids[i + 1 :]:
            assert defaults[a] != defaults[b], f"{tt} {a} vs {b}"
    out = apply({}, "de_vde", force=False)
    assert out.get("solarStandard") == "de_vde"
    assert out.get("comboBox_S1_AC_2") == "三相"
