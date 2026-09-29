# -*- coding: utf-8 -*-
from pathlib import Path

p = Path("components/wt_config_content.py")
t = p.read_text(encoding="utf-8")
t = t.replace(
    '_make_te(parent, "textEdit_StopTime", plain_text="00:05:00", max_h=40, min_w=120)',
    '_make_te(parent, "textEdit_StopTime", plain_text="00:05:00", max_h=44, min_w=140)',
)
t = t.replace(
    '_make_te(parent, "textEdit_SavePath", plain_text=r"D:\\EnergyTest\\wt_file_save_path", max_h=40, min_w=220)',
    '_make_te(parent, "textEdit_SavePath", plain_text=r"D:\\EnergyTest\\wt_file_save_path", max_h=44, min_w=260)',
)
t = t.replace(
    '_make_te(parent, "textEdit_FileNameList", max_h=120, min_h=56)',
    '_make_te(parent, "textEdit_FileNameList", max_h=140, min_h=64)',
)
p.write_text(t, encoding="utf-8")
print("wt sizes updated")
