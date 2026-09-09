# -*- coding: utf-8 -*-
"""Batch: DC headers get units + Tab focus for common Dialog_thai*.py builders."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(r"E:\solarautotestnewui")

OLD_HEADERS = [
    '["通道", "开关", "Vmp", "Imp", "Voc", "Isc", "功率"]',
    "['通道', '开关', 'Vmp', 'Imp', 'Voc', 'Isc', '功率']",
    '["通道", "开关", "Vmp", "Imp", "Voc", "Isc", "功率"]',
]
NEW_HEADER = '["通道", "开关", "Vmp(V)", "Imp(A)", "Voc(V)", "Isc(A)", "功率(%)"]'

# also _dc_headers variants
OLD_DC = [
    '_dc_headers = ["通道", "开关", "Vmp", "Imp", "Voc", "Isc", "功率"]',
    'dc_headers = ["通道", "开关", "Vmp", "Imp", "Voc", "Isc", "功率"]',
    'headers = ["通道", "开关", "Vmp", "Imp", "Voc", "Isc", "功率"]',
]
NEW_MAP = {
    '_dc_headers = ["通道", "开关", "Vmp", "Imp", "Voc", "Isc", "功率"]':
        '_dc_headers = ["通道", "开关", "Vmp(V)", "Imp(A)", "Voc(V)", "Isc(A)", "功率(%)"]',
    'dc_headers = ["通道", "开关", "Vmp", "Imp", "Voc", "Isc", "功率"]':
        'dc_headers = ["通道", "开关", "Vmp(V)", "Imp(A)", "Voc(V)", "Isc(A)", "功率(%)"]',
    'headers = ["通道", "开关", "Vmp", "Imp", "Voc", "Isc", "功率"]':
        'headers = ["通道", "开关", "Vmp(V)", "Imp(A)", "Voc(V)", "Isc(A)", "功率(%)"]',
}

TAB_SNIPPET_OLD = """                te.setFixedSize(80, 28)
                g2Layout.addWidget(te, r, c)
                setattr(self, name, te)"""

TAB_SNIPPET_NEW = """                te.setFixedSize(80, 28)
                if hasattr(te, "setTabChangesFocus"):
                    te.setTabChangesFocus(True)
                g2Layout.addWidget(te, r, c)
                setattr(self, name, te)"""

# more size variants
TAB_PATTERNS = [
    (
        re.compile(
            r"(te\.setFixedSize\(\s*\d+\s*,\s*\d+\s*\))\n(\s*)(g2Layout\.addWidget\(te)",
            re.M,
        ),
        r'\1\n\2if hasattr(te, "setTabChangesFocus"):\n\2    te.setTabChangesFocus(True)\n\2\3',
    ),
    (
        re.compile(
            r"(te\.setFixedSize\(\s*\d+\s*,\s*\d+\s*\))\n(\s*)(setattr\(self, name, te\))\n(\s*)(g2Layout\.addWidget\(te)",
            re.M,
        ),
        r'\1\n\2if hasattr(te, "setTabChangesFocus"):\n\2    te.setTabChangesFocus(True)\n\2\3\n\4\5',
    ),
]


def main():
    changed = []
    for path in sorted(ROOT.glob("Dialog_thai*.py")):
        text = path.read_text(encoding="utf-8")
        orig = text
        for old, new in NEW_MAP.items():
            if old in text and "Vmp(V)" not in text.split(old)[0][-80:]:
                text = text.replace(old, new)
        # avoid double-adding tab
        if "setTabChangesFocus" not in text or text.count("setTabChangesFocus") < 2:
            for cre, repl in TAB_PATTERNS:
                text2, n = cre.subn(repl, text)
                if n:
                    text = text2
        if text != orig:
            path.write_text(text, encoding="utf-8")
            changed.append(path.name)
    print("updated", len(changed), "files")
    for n in changed:
        print(" ", n)


if __name__ == "__main__":
    main()
