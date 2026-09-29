# -*- coding: utf-8 -*-
import json
from pathlib import Path

IOT = Path(r"E:/IOT/iot/app/services/solar_test_schemas")

d = json.loads((IOT / "staticmppt_fields.json").read_text(encoding="utf-8"))
print("=== staticmppt key ===")
for f in d["fields"]:
    n = f["name"]
    if (
        f.get("group") in ("step1_dc", "step1_ac", "step3_power", "step4_mppt", "step5_off")
        or "dcPrefix" in n
        or "PATH" in n
        or "Bluesight" in n
        or "Pn_" in n
    ):
        print(
            f"{n:40} g={f.get('group'):12} lbl={f.get('label')!r:30} "
            f"def={f.get('default')!r} hid={f.get('hidden')}"
        )

for n in ("reconnect", "ovuf", "guoqianpin_immun"):
    d = json.loads((IOT / f"{n}_fields.json").read_text(encoding="utf-8"))
    print("===", n, "end/off ===")
    for f in d["fields"]:
        if "End" in f["name"] or str(f.get("group", "")).endswith("_off"):
            print(
                f"{f['name']:28} g={f.get('group')} lbl={f.get('label')!r} def={f.get('default')!r}"
            )
