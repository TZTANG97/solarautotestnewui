# -*- coding: utf-8 -*-
from pathlib import Path

root = Path(__file__).resolve().parents[1]

# Dialog
p = root / "Dialog_thaantibackflow.py"
t = p.read_text(encoding="utf-8")
for a, b in [
    ("Ui_Dialog_thaiactiveP", "Ui_Dialog_thaantibackflow"),
    ("Dialog_thaiactiveP", "Dialog_thaantibackflow"),
    ("有功调度项目配置", "防逆流测试项目配置（UNE 217001）"),
    ("启用有功调度工况", "启用防逆流工况（UNE 217001）"),
    ("③ P 调度", "③ 防逆流工况"),
]:
    t = t.replace(a, b)
p.write_text(t, encoding="utf-8")

# Open_Save
p = root / "utils" / "Open_Save_ThaiAntiBackflow.py"
t = p.read_text(encoding="utf-8")
for a, b in [
    ("有功调度", "防逆流测试"),
    ("ThaiActiveP", "ThaiAntiBackflow"),
    ("ActiveP", "AntiBackflow"),
    ("uiThaiActiveP", "uiThaiAntiBackflow"),
]:
    t = t.replace(a, b)
# PROJECT_SPECS key after 有功调度->防逆流测试 already becomes 防逆流测试
p.write_text(t, encoding="utf-8")
print("ok")
