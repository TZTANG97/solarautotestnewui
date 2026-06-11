"""将所有 .pushButton_XXX.clicked.connect(...) 改为 _safe_click 方式。"""
import re

filepath = r"c:\Users\28468\Desktop\workspace\codes\solarautotestdev\SCPITestWave.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 匹配所有 .pushButton_XXX.clicked.connect(YYY)
# 排除已注释的行、_safe_click 开头的行、以及 lambda 参数
pattern = r'(?<!_safe_click\()(\w+)\.(pushButton_\w+)\.clicked\.connect\(([^)]+)\)'

def replace_match(m):
    full_match = m.group(0)
    obj = m.group(1)
    attr = m.group(2)
    slot = m.group(3)
    
    # 获取该行内容，如果已被注释则跳过
    line_start = content.rfind('\n', 0, m.start()) + 1
    line = content[line_start:m.end()]
    if line.lstrip().startswith('#'):
        return full_match  # 不修改注释行
    
    return f'_safe_click({obj}, "{attr}", {slot})'

new_content = re.sub(pattern, replace_match, content)

# 计数替换数量
old_matches = list(re.finditer(pattern, content))
new_matches = list(re.finditer(pattern, new_content))
replaced_count = len(old_matches) - len(new_matches)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(new_content)
print(f"✓ 已替换 {replaced_count} 处信号连接为 _safe_click")
print(f"  剩余 {len(new_matches)} 处未被替换（可能是注释行或 lambda 模式）")
