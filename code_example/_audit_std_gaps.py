# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

DESK = Path(__file__).resolve().parents[1]
MAPPING = {
    "flicker": "Dialog_thaiguodianyashanbian.py",  # may differ
    "frequencyadaptability": "Dialog_thaifrequencyadaptability.py",
    "rocof": "Dialog_thairocof.py",
    "guoqianpin_immun": "Dialog_thaiguoqianpin_immun.py",
    "rapidvolt": "Dialog_thairapidvolt.py",
    "lvrt": "Dialog_thailvrt.py",
    "phasejump": "Dialog_thaiphasejump.py",
    "staticmppt": "Dialog_thaistaticmppttest.py",
    "dynamicmppt": "Dialog_thaidynamicmppt.py",
    "reactiveqcap": "Dialog_thaireactiveQcap.py",
    "fixedq": "Dialog_thaifixedQ.py",
    "reactiveqin": "Dialog_thaireactiveQin.py",
    "reactiveqacc": "Dialog_thaireactiveQacc.py",
    "activep": "Dialog_thaiactiveP.py",
    "staticqu": "Dialog_thaistaticQU.py",
    "dynamicqu": "Dialog_thaidynamicQU.py",
    "testpu": "Dialog_thaitestPU.py",
    "staticcosphi": "Dialog_thaistaticcosPhi.py",
    "dynamiccosphi": "Dialog_thaidynamiccosPhi.py",
    "cosphibrazil": "Dialog_thaicosPhi_Brazil.py",
    "qianpinshengzai": "Dialog_thaiqianpinshengzai.py",
    "guopinjiangzai": "Dialog_thaiguopinjiangzai.py",
    "voltageadaptability": "Dialog_thaivoltageadaptability.py",
    "voltprotect10min": "Dialog_thaivoltprotect10min.py",
    "antibackflow": "Dialog_thaantibackflow.py",
    "overload": "Dialog_thaioverloads.py",
    "reconnect": "Dialog_thaichonglian.py",
    "ovuf": "Dialog_thaiguoqianya_pin.py",
    "fixedpf": "Dialog_thaifixedPF.py",
    "dccomponent": "Dialog_thaizhiliufenliang.py",
    "harmonic": "Dialog_thaixiebodianliu.py",
}

handoff = (DESK / "utils" / "iot_ui_handoff.py").read_text(encoding="utf-8")
mods = {p.stem.replace("iot_", "").replace("_standard", "") for p in (DESK / "utils").glob("iot_*_standard.py")}
print("modules", len(mods))

gaps = []
for tt, fn in MAPPING.items():
    path = DESK / "dialogs" / fn
    if not path.exists():
        gaps.append((tt, "dialog-missing", fn))
        continue
    text = path.read_text(encoding="utf-8")
    has_combo = "comboBox_SolarStandard" in text
    has_mod = f"iot_{tt}_standard" in text
    has_tt = f'SOLAR_STANDARD_TT = "{tt}"' in text
    dlg_ok = (has_combo and has_mod) or has_tt
    # flicker dialog name may be wrong
    if tt == "flicker" and not path.exists():
        pass
    ho = f'== "{tt}":' in handoff
    mod_ok = tt in mods or (tt == "staticmppt" and "staticmppt" in mods)
    if not dlg_ok or not ho or not mod_ok:
        gaps.append(
            (
                tt,
                "dlg" if not dlg_ok else "",
                "ho" if not ho else "",
                "mod" if not mod_ok else "",
            )
        )

print("gaps", len(gaps))
for g in gaps:
    print(" ", g)

# handoff apply branches for all mods
for tt in sorted(mods):
    if f'== "{tt}":' not in handoff:
        print("handoff-missing-branch", tt)
