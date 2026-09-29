# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

dialog = Path(r"E:/solarautotestnewui/Dialog_thaixiebodianliu.py").read_text(encoding="utf-8")
names = set(re.findall(r'setObjectName\(\s*["\']([^"\']+)["\']\s*\)', dialog))


def skip(n: str) -> bool:
    return n.startswith(
        (
            "pushButton_",
            "label_",
            "groupBox_",
            "step_indicator_",
            "treeWidget_",
            "stackedWidget",
            "widget",
        )
    ) or n.startswith("Dialog_")


d_in = sorted(n for n in names if not skip(n))
schema = json.loads(
    Path(r"E:/IOT/iot/app/services/solar_test_schemas/harmonic_fields.json").read_text(
        encoding="utf-8"
    )
)
s_in = {f["name"] for f in schema["fields"]}
out = []
out.append(f"dialog inputs {len(d_in)} schema {len(s_in)}")
out.append("only dialog: " + ", ".join(n for n in d_in if n not in s_in))
out.append("only schema sample: " + ", ".join(sorted(s_in - set(d_in))[:60]))
out.append("groups: " + str(dict(Counter(f.get("group") for f in schema["fields"]))))
step3 = [
    (f["name"], f.get("label"), f.get("hidden"), f.get("default"))
    for f in schema["fields"]
    if "step3" in str(f.get("group") or "")
]
out.append(f"step3 count {len(step3)}")
for row in step3[:40]:
    out.append(repr(row))
# look for harmonic card pattern in dialog
for pat in (
    "谐波",
    "Harmonic",
    "S3",
    "checkBox_S",
    "textEdit_S",
    "card",
    "合并",
    "隐藏",
):
    if pat in dialog:
        out.append(f"dialog contains {pat!r}")
Path(r"E:/solarautotestnewui/code_example/_harmonic_audit.txt").write_text(
    "\n".join(out), encoding="utf-8"
)
print("ok")
