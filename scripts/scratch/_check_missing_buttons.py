"""检查 Dialog_*.py 文件中是否缺少 common buttons。"""
import os
import re

# 所有在 SCPITestWave.py 信号连接中引用的按钮属性
BUTTONS_TO_CHECK = [
    "pushButton_ReadSettingFile",
    "pushButton_SaveSettingFile",
    "pushButton_TestAppend",
    "pushButton_Confirm",
    "pushButton_Send",
]

dialog_dir = os.path.dirname(os.path.abspath(__file__))
issues = []

for fname in sorted(os.listdir(dialog_dir)):
    if not fname.startswith("Dialog_") or not fname.endswith(".py"):
        continue
    fpath = os.path.join(dialog_dir, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    # 获取类名
    cls_match = re.search(r"class (\w+)", content)
    cls_name = cls_match.group(1) if cls_match else "Unknown"

    # 检查 setupUi 中的属性定义
    setup_ui_attrs = set(re.findall(r"self\.(\w+)\s*=", content))

    for btn in BUTTONS_TO_CHECK:
        if btn not in setup_ui_attrs:
            # 检查 retranslateUi 是否有引用
            in_retranslate = btn in content
            issues.append((fname, cls_name, btn, in_retranslate))

print(f"{'文件':40s} {'类名':40s} {'缺失属性':30s} {'在retranslateUi中':>15s}")
print("="*130)
for fname, cls_name, btn, in_retranslate in issues:
    print(f"{fname:40s} {cls_name:40s} {btn:30s} {'是' if in_retranslate else '否':>15s}")

if not issues:
    print("\n✓ 所有 Dialog 文件都包含必需的按钮属性！")
else:
    print(f"\n总计 {len(issues)} 个缺失属性")
