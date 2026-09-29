# -*- coding: utf-8 -*-
from pathlib import Path
import re
import sys
sys.path.insert(0, r"E:/IOT/iot")

sc = Path(r"E:/solarautotestnewui/SCPITestWave.py").read_text(encoding="utf-8")
# find Auto_Test project list
m = re.search(
    r"(项目列表|Auto_Test|strArrayProject|project_list).*?=.*?\[(.*?)\]",
    sc,
    re.S,
)
# better: the line with 静态MPPT
for i, line in enumerate(sc.splitlines()):
    if "'静态MPPT测试'" in line and "频率适应性" in line:
        # collect multi-line list
        chunk = "\n".join(sc.splitlines()[max(0, i - 8) : i + 2])
        print("=== QUEUE CHUNK ===")
        print(chunk)
        break

from app.services.solar_test_schemas import list_supported_test_types
from app.services.solar_blockly_catalog import SOLAR_TEST_SPECS

print("SUPPORTED", list_supported_test_types())
print("CATALOG", list(SOLAR_TEST_SPECS.keys()))

# append funcs for remaining
funcs = re.findall(r"def (thai\w+Append)\(", sc)
print("APPENDS", funcs)

# which dialogs exist
root = Path(r"E:/solarautotestnewui")
for p in sorted(root.glob("Dialog_thai*.py")):
    print("DIALOG", p.name)
