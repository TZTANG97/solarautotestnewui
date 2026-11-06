# -*- coding: utf-8 -*-
"""仅对 thaiguoqianya_pinSend 应用 append_volt_set / append_freq_set。"""
from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "SCPITestWave.py"
_ROW_ASSIGN = r"[ \t]+strArraySingle\[\d+\] = (?:\"[^\"]+\"|\w+)\n"


def _replace_single_volt(body: str) -> tuple[str, int]:
    pat = re.compile(
        r"([ \t]+)strArraySingle = \[\"\" for _ in range\(10\)\]\n"
        r"\1S\dCommand = \"VOLT \" \+ step\n"
        rf"(?:{_ROW_ASSIGN}){{3}}"
        r"\1strArrayTest\.append\(strArraySingle\)\n"
        r"\1strArrayTestStepSingle\.append\(strArraySingle\)\n",
        re.M,
    )
    repl = (
        r"\1_bs = len(strArrayTest)\n"
        r"\1append_volt_set(strArrayTest, S1ACEACHStatus, step)\n"
        r"\1strArrayTestStepSingle.extend(strArrayTest[_bs:])\n"
    )
    return pat.subn(repl, body)


def _replace_single_freq(body: str) -> tuple[str, int]:
    pat = re.compile(
        r"([ \t]+)strArraySingle = \[\"\" for _ in range\(10\)\]\n"
        r"\1S\dCommand = \"FREQ \" \+ step\n"
        rf"(?:{_ROW_ASSIGN}){{3}}"
        r"\1strArrayTest\.append\(strArraySingle\)\n"
        r"\1strArrayTestStepSingle\.append\(strArraySingle\)\n",
        re.M,
    )
    repl = (
        r"\1_bs = len(strArrayTest)\n"
        r"\1append_freq_set(strArrayTest, S1ACEACHStatus, step)\n"
        r"\1strArrayTestStepSingle.extend(strArrayTest[_bs:])\n"
    )
    return pat.subn(repl, body)


def _triple_block(cmd: str, cmd_type: str) -> re.Pattern[str]:
    assert cmd_type in ("VOLT", "FREQ")
    end_extra = (
        r"\1strArrayTestStep\.append\(strArrayTestStepSingle\)\n\n"
        if cmd_type == "FREQ"
        else r"\n"
    )
    p = (
        r"([ \t]+)strArraySingle = \[\"\" for _ in range\(10\)\]\n"
        rf"\1{cmd} = \"INST:NSEL 1\"\n"
        rf"(?:{_ROW_ASSIGN}){{3}}"
        r"\1strArrayTest\.append\(strArraySingle\)\n"
        r"\1strArrayTestStepSingle\.append\(strArraySingle\)\n"
        r"\n"
        r"\1strArraySingle = \[\"\" for _ in range\(10\)\]\n"
        rf"\1{cmd} = \"{cmd_type} \" \+ step\n"
        rf"(?:{_ROW_ASSIGN}){{3}}"
        r"\1strArrayTest\.append\(strArraySingle\)\n"
        r"\1strArrayTestStepSingle\.append\(strArraySingle\)\n"
        r"\n"
        r"\1strArraySingle = \[\"\" for _ in range\(10\)\]\n"
        rf"\1{cmd} = \"INST:NSEL 2\"\n"
        rf"(?:{_ROW_ASSIGN}){{3}}"
        r"\1strArrayTest\.append\(strArraySingle\)\n"
        r"\1strArrayTestStepSingle\.append\(strArraySingle\)\n"
        r"\n"
        r"\1strArraySingle = \[\"\" for _ in range\(10\)\]\n"
        rf"\1{cmd} = \"{cmd_type} \" \+ step\n"
        rf"(?:{_ROW_ASSIGN}){{3}}"
        r"\1strArrayTest\.append\(strArraySingle\)\n"
        r"\1strArrayTestStepSingle\.append\(strArraySingle\)\n"
        + (r"\1strArrayTestStep\.append\(strArrayTestStepSingle\)\n\n" if cmd_type == "FREQ" else r"\n")
        + r"\1strArraySingle = \[\"\" for _ in range\(10\)\]\n"
        rf"\1{cmd} = \"INST:NSEL 3\"\n"
        rf"(?:{_ROW_ASSIGN}){{3}}"
        r"\1strArrayTest\.append\(strArraySingle\)\n"
        r"\1strArrayTestStepSingle\.append\(strArraySingle\)\n"
        r"\n"
        r"\1strArraySingle = \[\"\" for _ in range\(10\)\]\n"
        rf"\1{cmd} = \"{cmd_type} \" \+ step\n"
        rf"(?:{_ROW_ASSIGN}){{3}}"
        r"\1strArrayTest\.append\(strArraySingle\)\n"
        r"\1strArrayTestStepSingle\.append\(strArraySingle\)\n"
        + end_extra
    )
    return re.compile(p, re.M)


def _collapse_freq_nsel_triple(body: str) -> tuple[str, int]:
    """过欠频三相同频：NSEL+append_freq_set×3 → 一次 append_freq_set。"""
    pat = re.compile(
        r"([ \t]+)strArraySingle = \[\"\" for _ in range\(10\)\]\n"
        r"\1S\dCommand = \"INST:NSEL 1\"\n"
        rf"(?:{_ROW_ASSIGN}){{3}}"
        r"\1strArrayTest\.append\(strArraySingle\)\n"
        r"\1strArrayTestStepSingle\.append\(strArraySingle\)\n"
        r"\n"
        r"\1_bs = len\(strArrayTest\)\n"
        r"\1append_freq_set\(strArrayTest, S1ACEACHStatus, step\)\n"
        r"\1strArrayTestStepSingle\.extend\(strArrayTest\[_bs:\]\)\n"
        r"\1strArrayTestStep\.append\(strArrayTestStepSingle\)\n"
        r"\n"
        r"\1strArraySingle = \[\"\" for _ in range\(10\)\]\n"
        r"\1S\dCommand = \"INST:NSEL 2\"\n"
        rf"(?:{_ROW_ASSIGN}){{3}}"
        r"\1strArrayTest\.append\(strArraySingle\)\n"
        r"\1strArrayTestStepSingle\.append\(strArraySingle\)\n"
        r"\n"
        r"\1_bs = len\(strArrayTest\)\n"
        r"\1append_freq_set\(strArrayTest, S1ACEACHStatus, step\)\n"
        r"\1strArrayTestStepSingle\.extend\(strArrayTest\[_bs:\]\)\n"
        r"\1strArrayTestStep\.append\(strArrayTestStepSingle\)\n"
        r"\n"
        r"\1strArraySingle = \[\"\" for _ in range\(10\)\]\n"
        r"\1S\dCommand = \"INST:NSEL 3\"\n"
        rf"(?:{_ROW_ASSIGN}){{3}}"
        r"\1strArrayTest\.append\(strArraySingle\)\n"
        r"\1strArrayTestStepSingle\.append\(strArraySingle\)\n"
        r"\n"
        r"\1_bs = len\(strArrayTest\)\n"
        r"\1append_freq_set\(strArrayTest, S1ACEACHStatus, step\)\n"
        r"\1strArrayTestStepSingle\.extend\(strArrayTest\[_bs:\]\)\n"
        r"\1strArrayTestStep\.append\(strArrayTestStepSingle\)\n",
        re.M,
    )
    repl = (
        r"\1_bs = len(strArrayTest)\n"
        r"\1append_freq_set(strArrayTest, S1ACEACHStatus, step)\n"
        r"\1strArrayTestStepSingle.extend(strArrayTest[_bs:])\n"
        r"\1strArrayTestStep.append(strArrayTestStepSingle)\n\n"
    )
    return pat.subn(repl, body)


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    m = re.search(r"^def thaiguoqianya_pinSend\(\):(.*?)(?=^def \w+\(\):|\Z)", text, re.M | re.S)
    body = m.group(0)
    n3 = n4 = 0
    append_fn = {"VOLT": "append_volt_set", "FREQ": "append_freq_set"}
    for cmd in ("S3Command", "S4Command", "S5Command", "S6Command", "S7Command", "S8Command"):
        for ctype in ("VOLT", "FREQ"):
            pat = _triple_block(cmd, ctype)
            repl = (
                r"\1_bs = len(strArrayTest)\n"
                rf"\1{append_fn[ctype]}(strArrayTest, S1ACEACHStatus, step)\n"
                r"\1strArrayTestStepSingle.extend(strArrayTest[_bs:])\n"
            )
            if ctype == "FREQ":
                repl += r"\1strArrayTestStep.append(strArrayTestStepSingle)\n\n"
            else:
                repl += r"\n"
            body, c = pat.subn(repl, body)
            if ctype == "VOLT":
                n3 += c
            else:
                n4 += c
    body, n1 = _replace_single_volt(body)
    body, n2 = _replace_single_freq(body)
    body, n5 = _collapse_freq_nsel_triple(body)
    print(f"single_volt={n1} single_freq={n2} triple_volt={n3} triple_freq={n4} collapse_freq={n5}")
    text = text[: m.start()] + body + text[m.end() :]
    ast.parse(text)
    TARGET.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
