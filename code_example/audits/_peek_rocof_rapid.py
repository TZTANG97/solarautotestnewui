# -*- coding: utf-8 -*-
from pathlib import Path
import re

root = Path(r"E:/solarautotestnewui")
for fn in ["Dialog_thairocof.py", "Dialog_thairapidvolt.py"]:
    t = (root / fn).read_text(encoding="utf-8")
    names = sorted(
        set(
            re.findall(
                r"self\.(checkBox_\w+|comboBox_\w+|textEdit_\w+|radioButton_\w+|radio_\w+)",
                t,
            )
        )
    )
    print("===", fn, "lines", len(t.splitlines()), "widgets", len(names))
    m = re.search(r"step_titles\s*=\s*\[(.*?)\]", t, re.S)
    if m:
        print("steps", re.findall(r"['\"]([^'\"]+)['\"]", m.group(1)))
    print("names:", ", ".join(names[:40]))
    print("...")

sc = (root / "SCPITestWave.py").read_text(encoding="utf-8")
print("funcs", re.findall(r"def (thai\w*(?:rocof|rapidvolt)\w*)\(", sc, re.I))
print(
    "ui",
    sorted(
        set(
            re.findall(
                r"uiThai(?:Rocof|RapidVolt|ROCOF|VoltageAdaptability)\w*",
                sc,
            )
        )
    ),
)
print(
    "append map",
    re.findall(
        r"['\"](?:ROCOF保护|快速电压变化)['\"]\s*:\s*\(([^)]+)\)",
        sc,
    )[:5],
)
