# -*- coding: utf-8 -*-
from pathlib import Path
import re

root = Path(r"E:/solarautotestnewui")
sc = (root / "SCPITestWave.py").read_text(encoding="utf-8")

remaining = [
    ("无功控制范围", "reactiveQcap", "thaireactiveQcapAppend", "Dialog_thaireactiveQcap.py"),
    ("固无功", "fixedQ", "thaifixedQAppend", "Dialog_thaifixedQ.py"),
    ("无功注入", "reactiveQin", "thaireactiveQinAppend", "Dialog_thaireactiveQin.py"),
    ("无功精度", "reactiveQacc", "thaireactiveQaccAppend", "Dialog_thaireactiveQacc.py"),
    ("有功控制", "activeP", "thaiactivePAppend", "Dialog_thaiactiveP.py"),
    ("静态QU", "staticQU", "thaistaticQUAppend", "Dialog_thaistaticQU.py"),
    ("动态QU", "dynamicQU", "thaidynamicQUAppend", "Dialog_thaidynamicQU.py"),
    ("Test_PU", "testPU", "thaitestPUAppend", "Dialog_thaitestPU.py"),
    ("静态Cos(φ)", "staticcosPhi", "thaistaticcosPhiAppend", "Dialog_thaistaticcosPhi.py"),
    ("动态Cos(φ)", "dynamiccosPhi", "thaidynamiccosPhiAppend", "Dialog_thaidynamiccosPhi.py"),
    ("Cos(φ)_Brazil", "cosPhiBrazil", "thaicosPhiBrazilAppend", "Dialog_thaicosPhi_Brazil.py"),
]

for label, key, append, dialog in remaining:
    p = root / dialog
    lines = len(p.read_text(encoding="utf-8").splitlines()) if p.exists() else -1
    # ui global
    uis = re.findall(r"uiThai\w+", sc)
    # find resolve-like near append
    has_append = append in sc
    # map entry
    mapped = re.search(rf"['\"]{re.escape(label)}['\"]\s*:\s*\(([^)]+)\)", sc)
    print(f"{key:14} exists={p.exists()} lines={lines:4} append={has_append} map={bool(mapped)}")
    if mapped:
        print("  ", mapped.group(1)[:80])

# also 电压闪变?
print("---")
print("电压闪变 dialog", (root / "Dialog_thaiguodianyashanbian.py").exists())
print("flicker already in supported")
