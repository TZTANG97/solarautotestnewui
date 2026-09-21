# -*- coding: utf-8 -*-
from pathlib import Path
import re

root = Path(r"E:/solarautotestnewui")
for fn in [
    "Dialog_thaireactiveQcap.py",
    "Dialog_thaifixedQ.py",
    "Dialog_thaistaticQU.py",
    "Dialog_thaistaticcosPhi.py",
    "Dialog_thaicosPhi_Brazil.py",
    "Dialog_thaitestPU.py",
]:
    t = (root / fn).read_text(encoding="utf-8")
    names = sorted(
        set(
            re.findall(
                r"self\.(checkBox_\w+|comboBox_\w+|textEdit_\w+|radioButton_\w+|radio_\w+)\s*=",
                t,
            )
        )
    )
    m = re.search(r"step_titles\s*=\s*\[(.*?)\]", t, re.S)
    steps = re.findall(r"['\"]([^'\"]+)['\"]", m.group(1)) if m else []
    odd = [
        n
        for n in names
        if not any(x in n for x in ("S1", "S2", "S_End", "radio", "WT", "Analyzer"))
    ]
    print("===", fn, "n=", len(names), "steps=", steps)
    print("odd", odd[:40])
