# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(r"E:\solarautotestnewui\Dialog_thaiguoqianpin_immun.py")
text = p.read_text(encoding="utf-8")
for i, line in enumerate(text.splitlines(), 1):
    if "S2_RATE_TIME" in line or ("addItems" in line and ("毫秒" in line or "分钟" in line)):
        print(f"{i}: {line!r}")
        if "addItems" in line:
            # show codepoints of items inside brackets
            start = line.find("addItems(")
            print("  codepoints around addItems:", [hex(ord(c)) for c in line[start:start+40]])
