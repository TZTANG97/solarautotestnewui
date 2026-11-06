# -*- coding: utf-8 -*-
"""SCPITestWave.py：矩阵中途同压改 VOLT 块 → append_volt_set / append_freq_set。"""
from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "SCPITestWave.py"

SKIP_FUNCS = {"thaidianyashanbianSend"}

TARGET_FUNCS = {
    "thaichonglianSend",
    "thaistaticQUSend",
    "thaivoltprotect10minSend",
    "thaitestPUSend",
    "thaiguoqianya_pinSend",
    "thaiguoqianpin_immunSend",
}

IMPORT_OLD = "from utils.ac_scpi_commands import append_ac_startup_from_ui, append_volt_set"
IMPORT_NEW = (
    "from utils.ac_scpi_commands import append_ac_startup_from_ui, append_volt_set, append_freq_set"
)

_ROW_ASSIGN = r'[ \t]+strArraySingle\[\d+\] = (?:"[^"]+"|\w+)\n'


def _line_indent(line: str) -> int:
    return len(line) - len(line.lstrip(" \t"))


def _split_functions(text: str) -> list[tuple[str | None, str]]:
    parts = re.split(r"(?=^def )", text, flags=re.M)
    out: list[tuple[str | None, str]] = []
    for part in parts:
        m = re.match(r"^def (\w+)\(", part)
        out.append((m.group(1) if m else None, part))
    return out


def _find_block_end(lines: list[str], start: int, base_indent: int) -> int:
    for i in range(start + 1, len(lines)):
        if lines[i].strip() == "":
            continue
        if _line_indent(lines[i]) <= base_indent:
            return i
    return len(lines)


def _replace_volt_only_if_elif(body: str) -> tuple[str, int]:
    lines = body.splitlines(keepends=True)
    n = 0
    i = 0
    while i < len(lines):
        m_if = re.match(r'^([ \t]*)if S1ACEACHStatus == "单相":\s*$', lines[i])
        if not m_if:
            i += 1
            continue
        indent = _line_indent(lines[i])
        elif_i = None
        for j in range(i + 1, min(i + 80, len(lines))):
            if lines[j].strip() == "":
                continue
            ind = _line_indent(lines[j])
            if ind < indent:
                break
            if ind == indent and re.match(r'^[ \t]*elif S1ACEACHStatus == "三相":\s*$', lines[j]):
                elif_i = j
                break
            if ind == indent:
                break
        if elif_i is None:
            i += 1
            continue
        end = _find_block_end(lines, elif_i, indent)
        block = "".join(lines[i:end])
        if "INST:NSEL 1" not in block or "FREQ " in block:
            i += 1
            continue
        vm = re.search(r'"VOLT "\s*\+\s*(\w+)', block)
        if not vm:
            i += 1
            continue
        volt_var = vm.group(1)
        repl = (
            f'{" " * indent}_bs = len(strArrayTest)\n'
            f'{" " * indent}append_volt_set(strArrayTest, S1ACEACHStatus, {volt_var})\n'
            f'{" " * indent}strArrayTestStepSingle.extend(strArrayTest[_bs:])\n'
        )
        lines = lines[:i] + [repl] + lines[end:]
        n += 1
        i += 1
    return "".join(lines), n


def _replace_volt_freq_if_elif(body: str) -> tuple[str, int]:
    lines = body.splitlines(keepends=True)
    n = 0
    i = 0
    while i < len(lines):
        m_if = re.match(r'^([ \t]*)if S1ACEACHStatus == "单相":\s*$', lines[i])
        if not m_if:
            i += 1
            continue
        indent = _line_indent(lines[i])
        elif_i = None
        for j in range(i + 1, min(i + 120, len(lines))):
            if lines[j].strip() == "":
                continue
            ind = _line_indent(lines[j])
            if ind < indent:
                break
            if ind == indent and re.match(r'^[ \t]*elif S1ACEACHStatus == "三相":\s*$', lines[j]):
                elif_i = j
                break
            if ind == indent:
                break
        if elif_i is None:
            i += 1
            continue
        end = _find_block_end(lines, elif_i, indent)
        block = "".join(lines[i:end])
        if "INST:NSEL 1" not in block or block.count("FREQ ") < 2:
            i += 1
            continue
        vm = re.search(r'"VOLT "\s*\+\s*(\w+)', block)
        fm = re.search(r'"FREQ "\s*\+\s*(\w+)', block)
        if not vm or not fm:
            i += 1
            continue
        volt_var, freq_var = vm.group(1), fm.group(1)
        repl: list[str] = []
        if 'print("单相电")' in block:
            repl.append(
                f'{" " * indent}print("单相电" if S1ACEACHStatus == "单相" else "三相电")\n'
            )
        repl.extend(
            [
                f'{" " * indent}_bs = len(strArrayTest)\n',
                f'{" " * indent}append_volt_set(strArrayTest, S1ACEACHStatus, {volt_var})\n',
                f'{" " * indent}strArrayTestStepSingle.extend(strArrayTest[_bs:])\n',
                f'{" " * indent}_bs = len(strArrayTest)\n',
                f'{" " * indent}append_freq_set(strArrayTest, S1ACEACHStatus, {freq_var})\n',
                f'{" " * indent}strArrayTestStepSingle.extend(strArrayTest[_bs:])\n',
            ]
        )
        if "strArrayTestStep.append(strArrayTestStepSingle)" in block:
            repl.append(f'{" " * indent}strArrayTestStep.append(strArrayTestStepSingle)\n')
        lines = lines[:i] + repl + lines[end:]
        n += 1
        i += 1
    return "".join(lines), n


def _nsel_triple_volt_pattern(cmd_var: str) -> re.Pattern[str]:
    p = (
        r'([ \t]+)strArraySingle = \["" for _ in range\(10\)\]\n'
        rf'\1{cmd_var} = "INST:NSEL 1"\n'
        rf'(?:{_ROW_ASSIGN}){{3}}'
        r'\1strArrayTest\.append\(strArraySingle\)\n'
        r'\1strArrayTestStepSingle\.append\(strArraySingle\)\n'
        r'\n'
        r'\1strArraySingle = \["" for _ in range\(10\)\]\n'
        rf'\1{cmd_var} = "VOLT " \+ step\n'
        rf'(?:{_ROW_ASSIGN}){{3}}'
        r'\1strArrayTest\.append\(strArraySingle\)\n'
        r'\1strArrayTestStepSingle\.append\(strArraySingle\)\n'
        r'\n'
        r'\1strArraySingle = \["" for _ in range\(10\)\]\n'
        rf'\1{cmd_var} = "INST:NSEL 2"\n'
        rf'(?:{_ROW_ASSIGN}){{3}}'
        r'\1strArrayTest\.append\(strArraySingle\)\n'
        r'\1strArrayTestStepSingle\.append\(strArraySingle\)\n'
        r'\n'
        r'\1strArraySingle = \["" for _ in range\(10\)\]\n'
        rf'\1{cmd_var} = "VOLT " \+ step\n'
        rf'(?:{_ROW_ASSIGN}){{3}}'
        r'\1strArrayTest\.append\(strArraySingle\)\n'
        r'\1strArrayTestStepSingle\.append\(strArraySingle\)\n'
        r'\n'
        r'\1strArraySingle = \["" for _ in range\(10\)\]\n'
        rf'\1{cmd_var} = "INST:NSEL 3"\n'
        rf'(?:{_ROW_ASSIGN}){{3}}'
        r'\1strArrayTest\.append\(strArraySingle\)\n'
        r'\1strArrayTestStepSingle\.append\(strArraySingle\)\n'
        r'\n'
        r'\1strArraySingle = \["" for _ in range\(10\)\]\n'
        rf'\1{cmd_var} = "VOLT " \+ step\n'
        rf'(?:{_ROW_ASSIGN}){{3}}'
        r'\1strArrayTest\.append\(strArraySingle\)\n'
        r'\1strArrayTestStepSingle\.append\(strArraySingle\)\n'
    )
    return re.compile(p, re.M)


def _replace_guoqianya_same_volt_loop(body: str) -> tuple[str, int]:
    repl_tpl = (
        r'\1_bs = len(strArrayTest)\n'
        r'\1append_volt_set(strArrayTest, S1ACEACHStatus, step)\n'
        r'\1strArrayTestStepSingle.extend(strArrayTest[_bs:])\n\n'
    )
    count = 0
    for cmd in ("S3Command", "S4Command", "S5Command", "S6Command", "S7Command", "S8Command"):
        body, c = _nsel_triple_volt_pattern(cmd).subn(repl_tpl, body)
        count += c
    return body, count


def _patch_append_ov_ac_volt(body: str) -> tuple[str, int]:
    old = '''    def _append_ov_ac_volt(v1, v2=None, v3=None):
        """按 step1 相数写 AC 电压。"""
        step_cmds = []
        if S1ACEACHStatus == "单相":
            row = ["" for _ in range(10)]
            row[0] = "AC"
            row[1] = "write"
            row[2] = "VOLT " + str(v1)
            strArrayTest.append(row)
            step_cmds.append(row)
        else:
            for nsel, vv in ((1, v1), (2, v2 if v2 is not None else v1), (3, v3 if v3 is not None else v1)):
                row = ["" for _ in range(10)]
                row[0] = "AC"
                row[1] = "write"
                row[2] = f"INST:NSEL {nsel}"
                strArrayTest.append(row)
                step_cmds.append(row)
                row = ["" for _ in range(10)]
                row[0] = "AC"
                row[1] = "write"
                row[2] = "VOLT " + str(vv)
                strArrayTest.append(row)
                step_cmds.append(row)
        return step_cmds'''
    new = '''    def _append_ov_ac_volt(v1, v2=None, v3=None):
        """按 step1 相数写 AC 电压。"""
        step_cmds = []
        v2 = v2 if v2 is not None else v1
        v3 = v3 if v3 is not None else v1
        if S1ACEACHStatus == "单相":
            _bs = len(strArrayTest)
            append_volt_set(strArrayTest, S1ACEACHStatus, v1)
            step_cmds.extend(strArrayTest[_bs:])
        elif v1 == v2 == v3:
            _bs = len(strArrayTest)
            append_volt_set(strArrayTest, S1ACEACHStatus, v1)
            step_cmds.extend(strArrayTest[_bs:])
        else:
            for nsel, vv in ((1, v1), (2, v2), (3, v3)):
                row = ["" for _ in range(10)]
                row[0] = "AC"
                row[1] = "write"
                row[2] = f"INST:NSEL {nsel}"
                strArrayTest.append(row)
                step_cmds.append(row)
                row = ["" for _ in range(10)]
                row[0] = "AC"
                row[1] = "write"
                row[2] = "VOLT " + str(vv)
                strArrayTest.append(row)
                step_cmds.append(row)
        return step_cmds'''
    if old not in body:
        return body, 0
    return body.replace(old, new, 1), 1


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    if IMPORT_OLD in text and "append_freq_set" not in text.split("\n", 140)[128]:
        text = text.replace(IMPORT_OLD, IMPORT_NEW, 1)

    stats: dict[str, list[str]] = {}
    out_parts: list[str] = []

    for name, part in _split_functions(text):
        if name is None:
            out_parts.append(part)
            continue
        if name in SKIP_FUNCS or name not in TARGET_FUNCS:
            out_parts.append(part)
            continue

        new_part = part
        counts: list[str] = []

        c1, n1 = _replace_volt_only_if_elif(new_part)
        new_part = c1
        if n1:
            counts.append(f"volt_only×{n1}")

        c2, n2 = _replace_volt_freq_if_elif(new_part)
        new_part = c2
        if n2:
            counts.append(f"volt+freq×{n2}")

        if name == "thaiguoqianya_pinSend":
            c3, n3 = _replace_guoqianya_same_volt_loop(new_part)
            new_part = c3
            if n3:
                counts.append(f"ov_same_step×{n3}")

        if name == "thaivoltprotect10minSend":
            c4, n4 = _patch_append_ov_ac_volt(new_part)
            new_part = c4
            if n4:
                counts.append(f"_append_ov_ac_volt×{n4}")

        if counts:
            stats[name] = counts
        out_parts.append(new_part)

    new_text = "".join(out_parts)
    ast.parse(new_text)
    TARGET.write_text(new_text, encoding="utf-8")

    print("=== 改动统计 ===")
    total_blocks = 0
    for fn, cs in sorted(stats.items()):
        print(f"  {fn}: {', '.join(cs)}")
        for c in cs:
            total_blocks += int(re.search(r"×(\d+)", c).group(1))
    print(f"合计约 {total_blocks} 块")

    print("\n=== Send 内残留 INST:NSEL ===")
    for m in re.finditer(r"^def (\w+Send)\(", new_text, re.M):
        start = m.start()
        nxt = re.search(r"^def ", new_text[m.end() :], re.M)
        end = m.end() + (nxt.start() if nxt else len(new_text) - m.end())
        body = new_text[start:end]
        cnt = body.count("INST:NSEL")
        if cnt:
            reason = []
            if m.group(1) == "thaidianyashanbianSend":
                reason.append("闪变异压启机")
            if "_append_ladder_volt" in body:
                reason.append("电压阶梯异压")
            if "_append_ov_ac_volt" in body and "v1 == v2 == v3" in body:
                reason.append("10min异压仍用NSEL")
            if "phase_check_list" in body:
                reason.append("过欠压/频单相选通")
            print(f"  {m.group(1)}: {cnt} — {', '.join(reason) or '待查'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
