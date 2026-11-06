# -*- coding: utf-8 -*-
"""Patch underfreq step1 three-phase to INST:EDIT ALL."""
from pathlib import Path

p = Path(r"E:\solarautotestnewui\SCPITestWave.py")
text = p.read_text(encoding="utf-8")

marker = 'uiThaiQianPinShengZai.checkBox_S1.isChecked()'
pos = text.find(marker)
if pos < 0:
    raise SystemExit("underfreq S1 checkbox not found")

# find EDIT EACH after this marker (within step1)
seg_start = text.find('elif S1ACEACHStatus == "三相":', pos)
if seg_start < 0:
    raise SystemExit("三相 branch not found after underfreq S1")

# end at next "strArraySingle = ..." + OUTP ON for S1ACStatus after the EACH block
end_marker = (
    '        strArraySingle = ["" for _ in range(10)]\n'
    '        if S1ACStatus == "开启":\n'
    '            strArraySingle[0] = "AC"\n'
    '            strArraySingle[1] = "write"\n'
    '            strArraySingle[2] = "OUTP ON"\n'
    '            strArraySingle[9] = fS1ACWaitTime\n'
)
seg_end = text.find(end_marker, seg_start)
if seg_end < 0:
    raise SystemExit("OUTP ON end marker not found")

old = text[seg_start:seg_end]
if "INST:EDIT EACH" not in old:
    if "INST:EDIT ALL" in old:
        print("already patched")
        raise SystemExit(0)
    raise SystemExit("unexpected: no EDIT EACH in segment")

new = '''elif S1ACEACHStatus == "三相":
            # 三相：EDIT ALL + 一次 VOLT/FREQ，避免 NSEL 逐相改频导致短时三相不一致跳机
            strArraySingle = ["" for _ in range(10)]
            S1Command = "INST:PHAS THREE"
            strArraySingle[0] = "AC"
            strArraySingle[1] = "write"
            strArraySingle[2] = S1Command
            strArrayTest.append(strArraySingle)
            strArrayTestStepSingle.append(strArraySingle)

            strArraySingle = ["" for _ in range(10)]
            S1Command = "INST:EDIT ALL"
            strArraySingle[0] = "AC"
            strArraySingle[1] = "write"
            strArraySingle[2] = S1Command
            strArrayTest.append(strArraySingle)
            strArrayTestStepSingle.append(strArraySingle)

            strArraySingle = ["" for _ in range(10)]
            S1ACVOLT = uiThaiQianPinShengZai.textEdit_S1_AC_VOLT.toPlainText()
            S1Command = "VOLT " + S1ACVOLT
            strArraySingle[0] = "AC"
            strArraySingle[1] = "write"
            strArraySingle[2] = S1Command
            strArrayTest.append(strArraySingle)
            strArrayTestStepSingle.append(strArraySingle)

            strArraySingle = ["" for _ in range(10)]
            S1ACFR = uiThaiQianPinShengZai.textEdit_S1_AC_FR.toPlainText()
            S1Command = "FREQ " + S1ACFR
            strArraySingle[0] = "AC"
            strArraySingle[1] = "write"
            strArraySingle[2] = S1Command
            strArrayTest.append(strArraySingle)
            strArrayTestStepSingle.append(strArraySingle)

'''

text2 = text[:seg_start] + new + text[seg_end:]
p.write_text(text2, encoding="utf-8")
print(f"patched underfreq step1: removed {len(old)} chars, wrote {len(new)} chars")
