"""批量替换 SCPITestWave.py 中可能缺失属性的信号连接为 _safe_click 方式。"""
import re

filepath = r"c:\Users\28468\Desktop\workspace\codes\solarautotestdev\SCPITestWave.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 匹配 .pushButton_ReadSettingFile.clicked.connect(some_func)
# 或 .pushButton_SaveSettingFile.clicked.connect(some_func)
# 或 .pushButton_TestAppend.clicked.connect(some_func)
# 排除已注释的行和已修复的行
pattern = r'(?<!_safe_click\()(\w+)\.(pushButton_(?:ReadSettingFile|SaveSettingFile|TestAppend))\.clicked\.connect\((\w+)\)'

def replace_match(m):
    obj = m.group(1)
    attr = m.group(2)
    slot = m.group(3)
    return f'_safe_click({obj}, "{attr}", {slot})'

new_content = re.sub(pattern, replace_match, content)

count = (content != new_content)
if count:
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"✓ 已替换 {len(re.findall(pattern, content))} 处信号连接为 _safe_click")
else:
    print("✓ 没有需要替换的连接")
