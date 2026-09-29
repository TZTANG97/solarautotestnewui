# -*- coding: utf-8 -*-
"""一次性：同项目追加时刷新 WT 配置条件 + need_wt。"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

NEED_OLD = (
    'need_wt = str_add_flag == "0" or (str_add_flag == "1" and project_change == "1")'
)
NEED_NEW = (
    "need_wt = True  # 同项目追加也刷新 WT 文件名，避免多轮覆盖"
)

# SCPITestWave：仅刷新 WT 文件名相关条件（与谐波一致，同项目追加也进分支）
WT_COND_OLD = (
    'strAddTestFlag == "0" or (strAddTestFlag == \'1\' and project_change == \'1\')'
)
WT_COND_NEW = (
    'strAddTestFlag == "0" or strAddTestFlag == "1"  # 同项目追加也刷新录波文件名'
)


def patch_need_wt() -> int:
    n = 0
    for p in sorted((ROOT / "utils").glob("*_commands.py")):
        t = p.read_text(encoding="utf-8")
        if NEED_OLD not in t:
            continue
        p.write_text(t.replace(NEED_OLD, NEED_NEW), encoding="utf-8")
        print("need_wt:", p.name)
        n += 1
    return n


def patch_scpi_wt_conditions() -> int:
    """只改紧挨 WT 配置/文件名逻辑的条件行，避免误伤 test_program 其它分支。"""
    path = ROOT / "SCPITestWave.py"
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    markers = (
        "WT3000E_params_config",
        "WT1800_params_config",
        "WT1806E_params_config",
        "WT5000_params_config",
        "recommended_filenames",
        "apply_filename_list_to_wt_pages",
        "textEdit_FileNameList",
        "FileNameList",
        "overload_recommended",
        "recommended_reconnect",
        "recommended_ovuf",
        "dc_injection_recommended",
        "fixed_pf_recommended",
        "build_antibackflow",
        "build_reactive",
        "build_fixed",
        "build_active",
        "wt_config_dict",
    )
    out = []
    changed = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        if WT_COND_OLD in line and "project_change" in line:
            window = "".join(lines[i : min(len(lines), i + 40)])
            if any(m in window for m in markers):
                line = line.replace(WT_COND_OLD, WT_COND_NEW)
                # also handle double-quote variant of project_change
                changed += 1
        out.append(line)
        i += 1
    if changed:
        path.write_text("".join(out), encoding="utf-8")
    print("SCPITestWave WT cond patches:", changed)
    return changed


def main() -> int:
    print("need_wt files", patch_need_wt())
    print("done cond", patch_scpi_wt_conditions())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
