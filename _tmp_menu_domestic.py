# -*- coding: utf-8 -*-
import re
import sys
from collections import Counter, defaultdict

import openpyxl

sys.stdout.reconfigure(encoding="utf-8")

MENUS = [
    "重连", "电压闪变", "谐波电流", "固定PF=1", "无功能力范围", "定无功", "无功注入",
    "无功精度", "有功调度", "过载能力测试", "直流分量", "静态QU", "动态QU", "Test_PU",
    "静态Cos(φ)", "动态Cos(φ)", "Cos(φ)_Brazil", "10min过压保护", "过频降载", "欠频升载",
    "过欠压_过欠频", "巴西过欠频稳定性", "静态MPPT测试", "频率适应性", "电压适应性",
    "ROCOF保护", "快速电压变化",
]

# Sheet1 中文释义 → 菜单名（同义映射）
ALIASES = {
    "闪变": "电压闪变",
    "电压闪变": "电压闪变",
    "谐波": "谐波电流",
    "谐波电流": "谐波电流",
    "谐波和间谐波": "谐波电流",
    "固定PF=1": "固定PF=1",
    "无功能力范围": "无功能力范围",
    "定无功": "定无功",
    "定无功测试": "定无功",
    "固定无功测试": "定无功",
    "无功注入": "无功注入",
    "无功精度": "无功精度",
    "无功精度测试": "无功精度",
    "有功调度": "有功调度",
    "有功调度测试": "有功调度",
    "有功控制": "有功调度",
    "逆变器有功调度测试": "有功调度",
    "过载能力测试": "过载能力测试",
    "直流分量": "直流分量",
    "静态QU": "静态QU",
    "QU曲线测试": "静态QU",
    "Q(U)曲线测试": "静态QU",
    "动态QU": "动态QU",
    "QU曲线动态测试": "动态QU",
    "Q (U)曲线动态测试": "动态QU",
    "Test_PU": "Test_PU",
    "静态Cos(φ)": "静态Cos(φ)",
    "cos φ (P)曲线测试": "静态Cos(φ)",
    "动态Cos(φ)": "动态Cos(φ)",
    "cos φ (P)曲线动态测试": "动态Cos(φ)",
    "Cos(φ)_Brazil": "Cos(φ)_Brazil",
    "10min过压保护": "10min过压保护",
    "10分钟过压保护": "10min过压保护",
    "过频降载": "过频降载",
    "过频降载测试": "过频降载",
    "欠频升载": "欠频升载",
    "欠频升载测试": "欠频升载",
    "过欠压_过欠频": "过欠压_过欠频",
    "电压保护": "过欠压_过欠频",
    "频率保护": "过欠压_过欠频",
    "过欠频": "过欠压_过欠频",
    "巴西过欠频稳定性": "巴西过欠频稳定性",
    "静态MPPT测试": "静态MPPT测试",
    "频率适应性": "频率适应性",
    "频率适应性测试": "频率适应性",
    "电压、频率适应性": "频率适应性",  # 或拆分
    "电压适应性": "电压适应性",
    "ROCOF保护": "ROCOF保护",
    "ROCOF保护测试": "ROCOF保护",
    "快速电压变化": "快速电压变化",
    "快速电压变化测试": "快速电压变化",
    "重连": "重连",
}

wb = openpyxl.load_workbook(r"c:/Users/13852/Desktop/光伏自动化项目进度表-20260804.xlsx")
ws = wb["Sheet1"]

# col19 国产电源验证
c19 = Counter()
samples = defaultdict(list)
for r in range(2, ws.max_row + 1):
    v = ws.cell(r, 19).value
    key = str(v).strip() if v is not None and str(v).strip() else "(空)"
    c19[key] += 1
    if len(samples[key]) < 3:
        samples[key].append((r, ws.cell(r, 7).value, ws.cell(r, 20).value, ws.cell(r, 21).value, ws.cell(r, 22).value))

print("=== Sheet1「国产电源验证」col19 分布 ===")
for k, n in c19.most_common():
    print(f"  {k}: {n}")
    for s in samples[k]:
        print(f"    r{s[0]} {s[1]} | AC={s[2]} DC={s[3]} WT={s[4]}")

# map coverage
hit = defaultdict(list)
unmapped_soft = []
for r in range(2, ws.max_row + 1):
    name = str(ws.cell(r, 7).value or "").strip()
    st = str(ws.cell(r, 24).value or "").strip()
    if not name:
        continue
    menu = ALIASES.get(name)
    if menu:
        hit[menu].append((r, name, st, ws.cell(r, 19).value, ws.cell(r, 26).value))
    elif st in ("模拟通过", "WT已验", "界面已有") or "菜单" in str(ws.cell(r, 26).value or ""):
        unmapped_soft.append((r, name, st))

print("\n=== 27 菜单 ↔ Sheet1 覆盖 ===")
for m in MENUS:
    rows = hit.get(m, [])
    if not rows:
        print(f"[缺Sheet行] {m}")
        continue
    sts = sorted({str(x[2] or "(空)") for x in rows})
    domestic = sorted({str(x[3] or "(空)") for x in rows})
    names = sorted({x[1] for x in rows})
    print(f"[OK] {m} ← {names} | 软件进度={sts} | 国产电源={domestic} | 行数={len(rows)}")

print("\n=== 软件相关但未映射到菜单名的 Sheet1 行（抽样）===")
for item in unmapped_soft[:25]:
    print(item)
print("count", len(unmapped_soft))
