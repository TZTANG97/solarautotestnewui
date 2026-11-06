# -*- coding: utf-8 -*-
"""Fix accidental \\\"setTabChangesFocus\\\" syntax corruption."""
from pathlib import Path

ROOT = Path(r"E:\solarautotestnewui")
bad = 'hasattr(te, \\"setTabChangesFocus\\")'
good = 'hasattr(te, "setTabChangesFocus")'
fixed = []
for p in ROOT.rglob("*.py"):
    if ".venv" in p.parts:
        continue
    text = p.read_text(encoding="utf-8")
    if bad not in text:
        continue
    p.write_text(text.replace(bad, good), encoding="utf-8")
    fixed.append(str(p.relative_to(ROOT)))
print("fixed", len(fixed))
for f in fixed:
    print(" ", f)
