# -*- coding: utf-8 -*-
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
files = {
    "ovuf": "Dialog_thaiguoqianya_pin.py",
    "static_cos": "Dialog_thaistaticcosPhi.py",
    "static_qu": "Dialog_thaistaticQU.py",
    "active_p": "Dialog_thaiactiveP.py",
    "overfreq": "Dialog_thaiguopinjiangzai.py",
    "underfreq": "Dialog_thaiqianpinshengzai.py",
    "fixed_q": "Dialog_thaifixedQ.py",
    "qin": "Dialog_thaireactiveQin.py",
    "qacc": "Dialog_thaireactiveQacc.py",
    "qcap": "Dialog_thaireactiveQcap.py",
    "dyn_cos": "Dialog_thaidynamiccosPhi.py",
    "dyn_qu": "Dialog_thaidynamicQU.py",
    "test_pu": "Dialog_thaitestPU.py",
    "rocof": "Dialog_thairocof.py",
    "freq_adapt": "Dialog_thaifrequencyadaptability.py",
    "volt_adapt": "Dialog_thaivoltageadaptability.py",
    "rapid_volt": "Dialog_thairapidvolt.py",
    "volt10min": "Dialog_thaivoltprotect10min.py",
    "immun": "Dialog_thaiguoqianpin_immun.py",
    "static_mppt": "Dialog_thaistaticmppttest.py",
}
for slug, fn in files.items():
    p = ROOT / fn
    if not p.exists():
        print("MISSING", slug, fn)
        continue
    text = p.read_text(encoding="utf-8", errors="replace")
    print("====", slug)
    m = re.search(r"step_titles\s*=\s*(\[[^\]]+\])", text, re.S)
    if m:
        print(" steps:", " ".join(m.group(1).split())[:220])
    for key in (
        "textEdit_S1_AC_VOLT",
        "textEdit_S1_AC_FR",
        "textEdit_S1_ACWaitTIME",
        "textEdit_S1_TIME",
        "textEdit_S3_TIME",
        "textEdit_S3_TIME_2",
        "textEdit_S3_TIME_3",
    ):
        m = re.search(rf'{key}"\)[\s\S]{{0,120}}?setText\("([^"]*)"\)', text)
        if not m:
            m = re.search(rf'{key}".*?default="([^"]*)"', text)
        if m:
            print(f"  {key}={m.group(1)!r}")
    print()
