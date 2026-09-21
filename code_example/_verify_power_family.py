# -*- coding: utf-8 -*-
import re
import subprocess
import sys
from pathlib import Path

r1 = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_solar_power_family_schema.py", "-q", "--tb=line"],
    cwd=r"E:/IOT/iot",
)
print("iot exit", r1.returncode)

r2 = subprocess.run(
    ["uv", "run", "python", "-m", "pytest", "tests/test_agent_runner_fixedpf.py", "-q", "--tb=line"],
    cwd=r"E:/solarautotestnewui",
)
print("solar exit", r2.returncode)

sys.path.insert(0, r"E:/IOT/iot")
from app.services.solar_blockly_catalog import normalize_test_type
from app.services.solar_test_schemas import list_supported_test_types, load_test_schema

sc = Path(r"E:/solarautotestnewui/SCPITestWave.py").read_text(encoding="utf-8")
m = re.search(r"projectSecondList = \[(.*?)\]", sc, re.S)
items = re.findall(r"'([^']+)'", m.group(1))
print("QUEUE", len(items))
for it in items:
    print(" ", it, "->", normalize_test_type(it))
print("SUPPORTED", len(list_supported_test_types()))

# verify Cos aliases load
for t in ["静态Cos(φ)", "定无功", "无功能力范围", "Test_PU", "Cos(φ)_Brazil"]:
    load_test_schema.cache_clear()
    try:
        s = load_test_schema(t)
        print("load", t, "OK", s["testType"])
    except Exception as e:
        print("load", t, "FAIL", e)
