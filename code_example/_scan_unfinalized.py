# -*- coding: utf-8 -*-
from pathlib import Path
import re

lines = Path("SCPITestWave.py").read_text(encoding="utf-8").splitlines()
for i, l in enumerate(lines):
    if "file_list_text" in l and "join" in l and "=" in l:
        ctx = "\n".join(lines[max(0, i - 20) : i])
        has = "_finalize_recording_file_names" in ctx or "run_tag" in ctx
        if not has:
            print(f"{i+1}: {l.strip()}")
