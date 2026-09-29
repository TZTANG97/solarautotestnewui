# -*- coding: utf-8 -*-
"""在 SCPITestWave 写 FileNameList 前插入 _finalize_recording_file_names。"""
from __future__ import annotations

import re
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "SCPITestWave.py"

# 变量名 → 在 join 前包一层 finalize
VARS = (
    "file_names",
    "staticqu_file_names",
    "staticcos_file_names",
)


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    out = []
    changed = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        # Skip harmonic block that already has its own run_tag merge
        window_back = "".join(out[-30:]) if out else ""
        is_harmonic = "harmonic_recommended_filenames" in window_back or "[谐波]" in window_back

        m = re.match(
            r'^(\s*)file_list_text\s*=\s*",".join\((%s)\)\s*$' % "|".join(VARS),
            line.rstrip("\n\r"),
        )
        if m and not is_harmonic:
            indent, var = m.group(1), m.group(2)
            # Avoid double-wrap
            if i > 0 and "_finalize_recording_file_names" in lines[i - 1]:
                out.append(line)
                i += 1
                continue
            out.append(f"{indent}{var} = _finalize_recording_file_names({var})\n")
            out.append(line)
            changed += 1
            i += 1
            continue

        # Dewetron: finalize before resolve_dewetron_save_paths / _dew_file_names
        if (
            "resolve_dewetron_save_paths(" in line
            and "file_names=file_names" in "".join(lines[i : i + 6])
        ):
            # insert finalize before this call if not present
            if "_finalize_recording_file_names" not in "".join(out[-8:]):
                indent = re.match(r"^(\s*)", line).group(1)
                out.append(
                    f"{indent}file_names = _finalize_recording_file_names(file_names)\n"
                )
                changed += 1

        out.append(line)
        i += 1

    PATH.write_text("".join(out), encoding="utf-8")
    print("inserted finalize wrappers:", changed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
