# -*- coding: utf-8 -*-
from pathlib import Path
import py_compile

root = Path(r"E:\solarautotestnewui")
errs = []
for p in sorted(root.glob("Dialog_thai*.py")):
    try:
        py_compile.compile(str(p), doraise=True)
    except Exception as e:
        errs.append((p.name, str(e)))

# literal bad pattern: backslash before quote inside hasattr
needle = 'hasattr(te, \\"setTabChangesFocus\\")'
bad_files = []
for p in root.glob("Dialog_*.py"):
    text = p.read_text(encoding="utf-8")
    if needle in text:
        bad_files.append(p.name)

print("compile_errors", len(errs))
for n, e in errs:
    print(n, e)
print("bad_escape_files", bad_files)
print("chonglian_ok", "Dialog_thaichonglian.py" not in {n for n, _ in errs})
