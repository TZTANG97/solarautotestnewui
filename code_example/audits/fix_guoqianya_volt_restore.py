# -*- coding: utf-8 -*-
"""修复 thaiguoqianya_pinSend 被误替换的 step3~8，并正确应用 append_volt_set。"""
from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "SCPITestWave.py"
DIST = ROOT / "dist" / "SolarAutoTest-Setup" / "app" / "SCPITestWave.py"

_ROW_ASSIGN = r'[ \t]+strArraySingle\[\d+\] = (?:"[^"]+"|\w+)\n'


def _extract_step_exec_block(text: str, step: int) -> str:
    """从 dist 提取某 step 在 test_step_list 构建之后的执行块。"""
    marker = f"# step{step}\n    if uiThaiGuoQianYa_Pin.checkBox_S{step}.isChecked():"
    start = text.index(marker)
    # 找到 FR_loop / VOLT_loop 块结束后的 if S1ACEACHStatus
    sub = text[start:]
    m = re.search(r"\n        if S1ACEACHStatus == \"单相\":", sub)
    if not m:
        raise ValueError(f"step{step} exec not found")
    exec_start = start + m.start() + 1
    # 到 total_test_time 行（含）
    m2 = re.search(
        rf"\n        total_test_time = total_test_time \+ \(len\(S{step}_test_step_list\)",
        text[exec_start:],
    )
    if not m2:
        raise ValueError(f"step{step} total_test_time not found")
    exec_end = exec_start + m2.end()
    return text[exec_start:exec_end]


def _replace_single_volt(body: str) -> tuple[str, int]:
    pat = re.compile(
        r'([ \t]+)strArraySingle = \["" for _ in range\(10\)\]\n'
        r'\1S\dCommand = "VOLT " \+ step\n'
        rf'(?:{_ROW_ASSIGN}){{3}}'
        r'\1strArrayTest\.append\(strArraySingle\)\n'
        r'\1strArrayTestStepSingle\.append\(strArraySingle\)\n',
        re.M,
    )
    repl = (
        r'\1_bs = len(strArrayTest)\n'
        r'\1append_volt_set(strArrayTest, S1ACEACHStatus, step)\n'
        r'\1strArrayTestStepSingle.extend(strArrayTest[_bs:])\n'
    )
    return pat.subn(repl, body)


def _replace_single_freq(body: str) -> tuple[str, int]:
    pat = re.compile(
        r'([ \t]+)strArraySingle = \["" for _ in range\(10\)\]\n'
        r'\1S\dCommand = "FREQ " \+ step\n'
        rf'(?:{_ROW_ASSIGN}){{3}}'
        r'\1strArrayTest\.append\(strArraySingle\)\n'
        r'\1strArrayTestStepSingle\.append\(strArraySingle\)\n',
        re.M,
    )
    repl = (
        r'\1_bs = len(strArrayTest)\n'
        r'\1append_freq_set(strArrayTest, S1ACEACHStatus, step)\n'
        r'\1strArrayTestStepSingle.extend(strArrayTest[_bs:])\n'
    )
    return pat.subn(repl, body)


def _replace_triple_volt(body: str) -> tuple[str, int]:
    count = 0
    for cmd in ("S3Command", "S4Command", "S5Command", "S6Command", "S7Command", "S8Command"):
        pat = re.compile(
            r'([ \t]+)strArraySingle = \["" for _ in range\(10\)\]\n'
            rf'\1{cmd} = "INST:NSEL 1"\n'
            rf'(?:{_ROW_ASSIGN}){{3}}'
            r'\1strArrayTest\.append\(strArraySingle\)\n'
            r'\1strArrayTestStepSingle\.append\(strArraySingle\)\n'
            r'\n'
            r'\1strArraySingle = \["" for _ in range\(10\)\]\n'
            rf'\1{cmd} = "VOLT " \+ step\n'
            rf'(?:{_ROW_ASSIGN}){{3}}'
            r'\1strArrayTest\.append\(strArraySingle\)\n'
            r'\1strArrayTestStepSingle\.append\(strArraySingle\)\n'
            r'\n'
            r'\1strArraySingle = \["" for _ in range\(10\)\]\n'
            rf'\1{cmd} = "INST:NSEL 2"\n'
            rf'(?:{_ROW_ASSIGN}){{3}}'
            r'\1strArrayTest\.append\(strArraySingle\)\n'
            r'\1strArrayTestStepSingle\.append\(strArraySingle\)\n'
            r'\n'
            r'\1strArraySingle = \["" for _ in range\(10\)\]\n'
            rf'\1{cmd} = "VOLT " \+ step\n'
            rf'(?:{_ROW_ASSIGN}){{3}}'
            r'\1strArrayTest\.append\(strArraySingle\)\n'
            r'\1strArrayTestStepSingle\.append\(strArraySingle\)\n'
            r'\n'
            r'\1strArraySingle = \["" for _ in range\(10\)\]\n'
            rf'\1{cmd} = "INST:NSEL 3"\n'
            rf'(?:{_ROW_ASSIGN}){{3}}'
            r'\1strArrayTest\.append\(strArraySingle\)\n'
            r'\1strArrayTestStepSingle\.append\(strArraySingle\)\n'
            r'\n'
            r'\1strArraySingle = \["" for _ in range\(10\)\]\n'
            rf'\1{cmd} = "VOLT " \+ step\n'
            rf'(?:{_ROW_ASSIGN}){{3}}'
            r'\1strArrayTest\.append\(strArraySingle\)\n'
            r'\1strArrayTestStepSingle\.append\(strArraySingle\)\n',
            re.M,
        )
        body, c = pat.subn(
            r'\1_bs = len(strArrayTest)\n'
            r'\1append_volt_set(strArrayTest, S1ACEACHStatus, step)\n'
            r'\1strArrayTestStepSingle.extend(strArrayTest[_bs:])\n\n',
            body,
        )
        count += c
    return body, count


def _replace_triple_freq(body: str) -> tuple[str, int]:
    count = 0
    for cmd in ("S3Command", "S4Command", "S5Command", "S6Command", "S7Command", "S8Command"):
        pat = re.compile(
            r'([ \t]+)strArraySingle = \["" for _ in range\(10\)\]\n'
            rf'\1{cmd} = "INST:NSEL 1"\n'
            rf'(?:{_ROW_ASSIGN}){{3}}'
            r'\1strArrayTest\.append\(strArraySingle\)\n'
            r'\1strArrayTestStepSingle\.append\(strArraySingle\)\n'
            r'\n'
            r'\1strArraySingle = \["" for _ in range\(10\)\]\n'
            rf'\1{cmd} = "FREQ " \+ step\n'
            rf'(?:{_ROW_ASSIGN}){{3}}'
            r'\1strArrayTest\.append\(strArraySingle\)\n'
            r'\1strArrayTestStepSingle\.append\(strArraySingle\)\n'
            r'\1strArrayTestStep\.append\(strArrayTestStepSingle\)\n'
            r'\n'
            r'\1strArraySingle = \["" for _ in range\(10\)\]\n'
            rf'\1{cmd} = "INST:NSEL 2"\n'
            rf'(?:{_ROW_ASSIGN}){{3}}'
            r'\1strArrayTest\.append\(strArraySingle\)\n'
            r'\1strArrayTestStepSingle\.append\(strArraySingle\)\n'
            r'\n'
            r'\1strArraySingle = \["" for _ in range\(10\)\]\n'
            rf'\1{cmd} = "FREQ " \+ step\n'
            rf'(?:{_ROW_ASSIGN}){{3}}'
            r'\1strArrayTest\.append\(strArraySingle\)\n'
            r'\1strArrayTestStepSingle\.append\(strArraySingle\)\n'
            r'\1strArrayTestStep\.append\(strArrayTestStepSingle\)\n'
            r'\n'
            r'\1strArraySingle = \["" for _ in range\(10\)\]\n'
            rf'\1{cmd} = "INST:NSEL 3"\n'
            rf'(?:{_ROW_ASSIGN}){{3}}'
            r'\1strArrayTest\.append\(strArraySingle\)\n'
            r'\1strArrayTestStepSingle\.append\(strArraySingle\)\n'
            r'\n'
            r'\1strArraySingle = \["" for _ in range\(10\)\]\n'
            rf'\1{cmd} = "FREQ " \+ step\n'
            rf'(?:{_ROW_ASSIGN}){{3}}'
            r'\1strArrayTest\.append\(strArraySingle\)\n'
            r'\1strArrayTestStepSingle\.append\(strArraySingle\)\n'
            r'\1strArrayTestStep\.append\(strArrayTestStepSingle\)\n',
            re.M,
        )
        body, c = pat.subn(
            r'\1_bs = len(strArrayTest)\n'
            r'\1append_freq_set(strArrayTest, S1ACEACHStatus, step)\n'
            r'\1strArrayTestStepSingle.extend(strArrayTest[_bs:])\n'
            r'\1strArrayTestStep.append(strArrayTestStepSingle)\n\n',
            body,
        )
        count += c
    return body, count


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    dist = DIST.read_text(encoding="utf-8")

    # 1) AC_CHANGE_LIST[k]
    text = text.replace(
        "append_volt_set(strArrayTest, S1ACEACHStatus, AC_CHANGE_LIST)",
        "append_volt_set(strArrayTest, S1ACEACHStatus, AC_CHANGE_LIST[k])",
    )

    # 2) 恢复 thaiguoqianya step3~8 执行块
    fn = "thaiguoqianya_pinSend"
    m = re.search(rf"^def {fn}\(\):(.*?)(?=^def \w+\(\):|\Z)", text, re.M | re.S)
    if not m:
        raise SystemExit(f"{fn} not found")
    body = m.group(0)

    for step in range(3, 9):
        dist_exec = _extract_step_exec_block(dist, step)
        step_marker = f"# step{step}\n    if uiThaiGuoQianYa_Pin.checkBox_S{step}.isChecked():"
        si = body.index(step_marker)
        sub = body[si:]
        # 已破坏：test list 后直接 _bs = len(strArrayTest)
        m_broken = re.search(
            r"\n        _bs = len\(strArrayTest\)\n        append_volt_set\(strArrayTest, S1ACEACHStatus, step\)",
            sub,
        )
        m_ok = re.search(r"\n        if S1ACEACHStatus == \"单相\":", sub)
        if m_broken:
            exec_si = si + m_broken.start() + 1
        elif m_ok:
            exec_si = si + m_ok.start() + 1
        else:
            print(f"step{step}: skip (no exec block)")
            continue
        m_tot = re.search(
            rf"\n        total_test_time = total_test_time \+ \(len\(S{step}_test_step_list\)",
            body[exec_si:],
        )
        if not m_tot:
            raise ValueError(f"step{step} total_test_time not found")
        exec_ei = exec_si + m_tot.end()
        body = body[:exec_si] + dist_exec + body[exec_ei:]

    text = text[: m.start()] + body + text[m.end() :]
    ast.parse(text)
    TARGET.write_text(text, encoding="utf-8")
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
