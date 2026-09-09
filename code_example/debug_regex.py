# -*- coding: utf-8 -*-
import re
from pathlib import Path

text = Path("SCPITestWave.py").read_text(encoding="utf-8")
m = re.search(r"^def thaiguoqianya_pinSend\(\):(.*?)(?=^def \w+\(\):|\Z)", text, re.M | re.S)
body = m.group(0)
sample = body[body.index("S3Command = \"INST:NSEL 1\"") - 80 : body.index("S3Command = \"INST:NSEL 1\"") + 600]
print(repr(sample[:200]))

_ROW_ASSIGN = r"[ \t]+strArraySingle\[\d+\] = \"[^\"]+\"\n"
pat = re.compile(
    r"([ \t]+)strArraySingle = \[\"\" for _ in range\(10\)\]\n"
    r"\1S3Command = \"INST:NSEL 1\"\n"
    rf"(?:{_ROW_ASSIGN}){{3}}"
    r"\1strArrayTest\.append\(strArraySingle\)\n"
    r"\1strArrayTestStepSingle\.append\(strArraySingle\)\n"
    r"\n"
    r"\1strArraySingle = \[\"\" for _ in range\(10\)\]\n"
    r"\1S3Command = \"VOLT \" \+ step\n",
    re.M,
)
print("partial match", bool(pat.search(body)))
