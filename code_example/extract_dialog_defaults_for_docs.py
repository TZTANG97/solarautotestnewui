# -*- coding: utf-8 -*-
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
files = {
    "flicker": "Dialog_thaiguodianyashanbian.py",
    "harmonic": "Dialog_thaixiebodianliu.py",
    "fixedpf": "Dialog_thaifixedPF.py",
    "dcinj": "Dialog_thaizhiliufenliang.py",
    "reconnect": "Dialog_thaichonglian.py",
}
for slug, fn in files.items():
    text = (ROOT / fn).read_text(encoding="utf-8", errors="replace")
    print("====", slug, fn)
    m = re.search(r"step_titles\s*=\s*(\[[^\]]+\])", text, re.S)
    if m:
        print("steps:", " ".join(m.group(1).split())[:240])
    for m in re.finditer(
        r'setObjectName\("([^"]+)"\)[\s\S]{0,160}?setText\("([^"]*)"\)', text
    ):
        name, val = m.group(1), m.group(2)
        keys = ("VOLT", "FR", "TIME", "Wait", "PF", "CURR", "Voc", "Isc", "S3", "S4", "S5", "FREQ", "Q", "file", "path", "Stop")
        if any(k in name for k in keys):
            print(f"  {name} = {val!r}")
    for m in re.finditer(
        r'setObjectName\("([^"]+)"\)[\s\S]{0,100}?addItems\(\[([^\]]+)\]\)', text
    ):
        name, items = m.group(1), m.group(2)
        if any(k in name for k in ("AC_2", "Wait", "TIME", "record", "Phase")):
            print(f"  {name} items: {items[:100]}")
    print()
