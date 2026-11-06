# -*- coding: utf-8 -*-
"""为 iot_*_standard.normalize_* 补 iec/cn_gb 别名。"""
from __future__ import annotations

from pathlib import Path

OLD = (
    '    s = str(raw or "").strip().lower().replace("-", "_").replace(" ", "")\n'
    "    if s in "
)
NEW = (
    '    s = str(raw or "").strip().lower().replace("-", "_").replace(" ", "")\n'
    '    aliases = {"iec": "iec61727", "cn_gb": "en50549"}\n'
    "    s = aliases.get(s, s)\n"
    "    if s in "
)


def main() -> None:
    n = 0
    for path in Path("utils").glob("iot_*_standard.py"):
        text = path.read_text(encoding="utf-8")
        if 'aliases = {"iec": "iec61727"' in text:
            continue
        if OLD not in text:
            print("skip pattern", path.name)
            continue
        path.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
        n += 1
        print("patched", path.name)
    print("total", n)


if __name__ == "__main__":
    main()
