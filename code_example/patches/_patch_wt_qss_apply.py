# -*- coding: utf-8 -*-
from pathlib import Path
import re

p = Path("components/wt_config_content.py")
t = p.read_text(encoding="utf-8")


def repl_gb(m):
    return f"_apply_design_qss({m.group(1)}, _GROUPBOX_STYLE)"


t = re.sub(r"(\w+)\.setStyleSheet\(_GROUPBOX_STYLE\)", repl_gb, t)
t = t.replace(
    "cb_auto.setStyleSheet(_CHECKBOX_STYLE)",
    "_apply_design_qss(cb_auto, _CHECKBOX_STYLE)",
)
t = t.replace(
    '_make_te(parent, "textEdit_SetStart", max_h=32)',
    '_make_te(parent, "textEdit_SetStart", max_h=36)',
)
t = t.replace(
    '_make_te(parent, "textEdit_SetStop", max_h=32)',
    '_make_te(parent, "textEdit_SetStop", max_h=36)',
)
p.write_text(t, encoding="utf-8")
print("apply_design_qss count", t.count("_apply_design_qss("))
print("left groupbox setStyleSheet", t.count("setStyleSheet(_GROUPBOX_STYLE)"))
