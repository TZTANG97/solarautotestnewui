# -*- coding: utf-8 -*-
from pathlib import Path
import re

ROOT = Path(r"E:\solarautotestnewui")

for p in sorted(ROOT.glob("Dialog_thai*.py")):
    lines = p.read_text(encoding="utf-8").splitlines(True)
    out = []
    changed = False
    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        if "te.setFixedSize" in line and i + 1 < len(lines):
            nxt = "".join(lines[i + 1 : i + 4])
            if "setTabChangesFocus" not in nxt:
                m = re.match(r"(\s*)", lines[i + 1])
                indent = m.group(1) if m else "                "
                if "setattr(self, name, te)" in lines[i + 1] or "addWidget(te" in lines[i + 1]:
                    out.append(f'{indent}if hasattr(te, "setTabChangesFocus"):\n')
                    out.append(f"{indent}    te.setTabChangesFocus(True)\n")
                    changed = True
        i += 1
    if changed:
        p.write_text("".join(out), encoding="utf-8")
        print("patched", p.name)
print("done")
