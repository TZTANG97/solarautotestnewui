# -*- coding: utf-8 -*-
"""扫描功率族 Dialog 默认值（一次性）。"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(r"E:/solarautotestnewui")
DIALOGS = {
    17: ("cosphibrazil", "Dialog_thaicosPhi_Brazil.py"),
    18: ("staticcosphi", "Dialog_thaistaticcosPhi.py"),
    19: ("staticqu", "Dialog_thaistaticQU.py"),
    20: ("testpu", "Dialog_thaitestPU.py"),
    21: ("dynamiccosphi", "Dialog_thaidynamiccosPhi.py"),
    22: ("dynamicqu", "Dialog_thaidynamicQU.py"),
    23: ("reactiveqcap", "Dialog_thaireactiveQcap.py"),
    24: ("fixedq", "Dialog_thaifixedQ.py"),
    25: ("reactiveqin", "Dialog_thaireactiveQin.py"),
    26: ("reactiveqacc", "Dialog_thaireactiveQacc.py"),
    27: ("activep", "Dialog_thaiactiveP.py"),
}


def main() -> None:
    for seq, (tt, fn) in DIALOGS.items():
        p = ROOT / fn
        if not p.exists():
            print(seq, tt, "MISSING", fn)
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"step_titles\s*=\s*\[(.*?)\]", t, re.S)
        titles = re.findall(r'"([^"]+)"', m.group(1)) if m else None
        print(f"{seq} {tt}: titles={titles}")
        for pat, label in (
            (r'textEdit_PowerLadder.*?set(?:Text|PlainText)\(\s*"([^"]*)"', "PowerLadder"),
            (r'textEdit_VoltageLadder(?!_).*?set(?:Text|PlainText)\(\s*"([^"]*)"', "VoltageLadder"),
            (r'textEdit_S3_TIME_2.*?set(?:Text|PlainText)\(\s*"([^"]*)"', "TIME_2"),
            (r'textEdit_S3_TIME.*?set(?:Text|PlainText)\(\s*"([^"]*)"', "TIME"),
        ):
            mm = re.search(pat, t, re.S)
            if mm:
                print(f"  {label}={mm.group(1)[:80]!r}")


if __name__ == "__main__":
    main()
