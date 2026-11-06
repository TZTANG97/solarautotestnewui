# -*- coding: utf-8 -*-
"""After [9]/[8] wait loops, break outer for-i when EndProject is pressed."""
from pathlib import Path

p = Path(r"E:\solarautotestnewui\SCPITestWave.py")
text = p.read_text(encoding="utf-8")

needle = """                                if strTestStatusFlag == \"结束\":
                                    break
                                time.sleep(0.1)

"""

insert = """                                if strTestStatusFlag == \"结束\":
                                    break
                                time.sleep(0.1)
                        if strTestStatusFlag == \"结束\":
                            break

"""

# Only insert when the next non-empty content is NOT already the outer break
count = 0
out = []
i = 0
while True:
    j = text.find(needle, i)
    if j < 0:
        out.append(text[i:])
        break
    out.append(text[i:j])
    after = text[j + len(needle) : j + len(needle) + 80]
    if after.lstrip().startswith('if strTestStatusFlag == "结束":'):
        # already has outer break
        out.append(needle)
    else:
        out.append(insert)
        count += 1
    i = j + len(needle)

new = "".join(out)
if count:
    p.write_text(new, encoding="utf-8")
print(f"inserted outer end-break after wait loops: {count}")
