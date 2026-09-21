# -*- coding: utf-8 -*-
from pathlib import Path
import re

path = Path(__file__).resolve().parents[1] / "SCPITestWave.py"
text = path.read_text(encoding="utf-8")

# Broken: ... == "1"  # comment:   OR  ... == "1"  # comment):
# Fix mid-line comment that ate the colon
text2, n1 = re.subn(
    r'strAddTestFlag == "0" or strAddTestFlag == "1"\s+# 同项目追加也刷新录波文件名:',
    'strAddTestFlag == "0" or strAddTestFlag == "1":  # 同项目追加也刷新录波文件名',
    text,
)
text2, n2 = re.subn(
    r'strAddTestFlag == "0" or strAddTestFlag == "1"\s+# 同项目追加也刷新录波文件名\):',
    'strAddTestFlag == "0" or strAddTestFlag == "1"):  # 同项目追加也刷新录波文件名',
    text2,
)
# Harmonic mangled block
old_harm = '''    if strAddTestFlag == "0" or strAddTestFlag == "1"  # 同项目追加也刷新录波文件名 or (
        # 同项目再次追加也要换文件名，否则会盖掉上一轮 Harmonic_P*
        strAddTestFlag == "1" and not is_dewetron
    ):'''
new_harm = '''    if strAddTestFlag == "0" or (strAddTestFlag == "1" and not is_dewetron):  # 同项目追加也刷新录波文件名'''
n3 = 0
if old_harm in text2:
    text2 = text2.replace(old_harm, new_harm)
    n3 = 1

path.write_text(text2, encoding="utf-8")
print(f"fixed colon={n1} paren={n2} harmonic={n3}")

# verify remaining broken
bad = []
for i, line in enumerate(text2.splitlines(), 1):
    if "同项目追加也刷新录波文件名" in line and line.rstrip().endswith("文件名"):
        # line ends without colon - problem unless next line continues
        bad.append(i)
    if re.search(r'== "1"\s+# 同项目', line) and not line.rstrip().endswith(":"):
        if "):" not in line and not line.rstrip().endswith("文件名"):
            pass
        elif "#" in line and line.find("#") < line.rfind(":"):
            pass
        else:
            # check if colon after comment
            if "#" in line and (":" not in line.split("#", 1)[0] or not line.split("#", 1)[0].rstrip().endswith((":", ")"))):
                if not re.search(r'\):\s*#', line) and not re.search(r':\s*#', line):
                    bad.append((i, line.strip()[:100]))
print("suspicious", bad[:20], "count", len(bad))
