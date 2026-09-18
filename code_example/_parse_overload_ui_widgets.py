# -*- coding: utf-8 -*-
"""Parse Dialog_thaioverloads.ui → list input widgets (scratch)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ui = (ROOT / "ui_files" / "Dialog_thaioverloads.ui").read_text(encoding="utf-8", errors="replace")
pat = re.compile(r'<widget\s+class="([^"]+)"\s+name="([^"]+)"')
interesting = {
    "QLineEdit",
    "QCheckBox",
    "QComboBox",
    "QRadioButton",
    "QSpinBox",
    "QDoubleSpinBox",
    "QTextEdit",
    "QPlainTextEdit",
    "QTimeEdit",
    "QDateTimeEdit",
}
by: dict[str, list[str]] = {}
for cls, name in pat.findall(ui):
    if cls in interesting and name and not name.startswith("qt_"):
        by.setdefault(cls, []).append(name)
for cls in sorted(by):
    print(cls, len(by[cls]))
    for n in by[cls]:
        print(" ", n)
print("TOTAL", sum(len(v) for v in by.values()))
