# -*- coding: utf-8 -*-
from pathlib import Path
import re

p = Path(__file__).resolve().parent / "rebuild_docs_interleaved.py"
t = p.read_text(encoding="utf-8")
t2 = re.sub(r'\(2, ("[^"]+"), an \+ ("""[\s\S]*?""")\)', r"(2, \1, \2)", t)
t2 = re.sub(r'\(2, ("[^"]+"), an \+ ("[^"]*")\)', r"(2, \1, \2)", t2)
t2 = re.sub(r'\(2, ("[^"]+"), an\)', r'(2, \1, "")', t2)
p.write_text(t2, encoding="utf-8")
print("done", len(re.findall(r"\(2,.*\ban\b", t2)))
