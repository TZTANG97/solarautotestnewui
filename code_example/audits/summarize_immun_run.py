# -*- coding: utf-8 -*-
"""Summarize latest guoqianpin_immun run from today log."""
from pathlib import Path
import re

log = Path(r"E:\solarautotestnewui\data_logs\auto_test_2026-09-02.log")
lines = log.read_text(encoding="utf-8", errors="replace").splitlines()

# Focus on afternoon/evening runs after 16:50
interesting = []
for ln in lines:
    if not ln.startswith("2026-09-02 1"):
        continue
    hhmm = ln[11:16]
    if hhmm < "16:50":
        continue
    if any(
        k in ln
        for k in (
            "实验完成",
            "实验已中止",
            "结束试验",
            "FREQ ",
            "正在解析第1条",
            "Upper_WT_Config",
            "跳过剩余",
            "强制关闭",
            "DC2 Not Connect",
            "OUTP OFF",
            "STANDBY",
            "开始试验",
            "追加",
        )
    ):
        interesting.append(ln)

print(f"interesting lines after 16:50: {len(interesting)}")
for ln in interesting[-80:]:
    print(ln)

# Collect FREQ values from last complete run (after last 正在解析第1条 before 实验完成)
starts = [i for i, ln in enumerate(lines) if "正在解析第1条命令" in ln and ln.startswith("2026-09-02 1") and ln[11:16] >= "16:50"]
completes = [i for i, ln in enumerate(lines) if "实验完成" in ln and ln.startswith("2026-09-02 1") and ln[11:16] >= "16:50"]
print("\nstarts:", [lines[i][:30] for i in starts])
print("completes:", [lines[i][:40] for i in completes])
if starts and completes:
    s, e = starts[-1], completes[-1]
    freqs = []
    for ln in lines[s:e+1]:
        m = re.search(r"FREQ\s+([0-9.]+)", ln)
        if m and "准备发送" in ln:
            freqs.append(float(m.group(1)))
    print(f"last run cmd range lines {s}-{e}")
    print(f"FREQ points: {len(freqs)}")
    if freqs:
        print(f"FREQ min/max/first/last: {min(freqs)} / {max(freqs)} / {freqs[0]} / {freqs[-1]}")
        print(f"unique count: {len(set(freqs))}")
        # show condensed unique sequence
        seq = []
        for f in freqs:
            if not seq or seq[-1] != f:
                seq.append(f)
        print("FREQ sequence (dedup consecutive):", seq[:40], "..." if len(seq)>40 else "")
