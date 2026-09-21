# -*- coding: utf-8 -*-
from pathlib import Path
import re

root = Path(r"E:/solarautotestnewui")
for fn in ["Dialog_thailvrt.py", "Dialog_thaiphasejump.py", "Dialog_thaidynamicmppt.py"]:
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
    print("head", t[:300].replace("\n", " | "))
    print("names", names[:30])
