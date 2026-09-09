# -*- coding: utf-8 -*-
"""分析 VoltAdapt_BR_5421.CSV 电压轨迹与试验设定一致性。"""
import pandas as pd
import numpy as np
from pathlib import Path

path = Path("E:/solarautotestnewui/docs/VoltAdapt_BR_5421.CSV")
df = pd.read_csv(path, encoding="utf-8-sig")
cols = ["Urms-1", "Urms-2", "Urms-3", "P-1", "P-2", "P-3", "FreqU-2"]
for c in cols:
    df[c] = pd.to_numeric(df[c], errors="coerce")

df["ts"] = pd.to_datetime(
    df["Date"].astype(str) + " " + df["Time"].astype(str) + "." + df["Millisecond"].astype(int).astype(str).str.zfill(3),
    format="%Y/%m/%d %H:%M:%S.%f",
)
df["t_s"] = (df["ts"] - df["ts"].iloc[0]).dt.total_seconds()
df["Umean"] = (df["Urms-1"] + df["Urms-2"] + df["Urms-3"]) / 3.0
df["Psum"] = df["P-1"] + df["P-2"] + df["P-3"]

# 粗分段：找 Umean 峰值与回到 230 附近、开始下降点
u = df["Umean"].values
t = df["t_s"].values
imax = int(np.argmax(u))
print("=== 基本信息 ===")
print(f"行数 {len(df)}, 时长 {t[-1]:.1f}s, 起止 {df['ts'].iloc[0]} ~ {df['ts'].iloc[-1]}")
print(f"Umean 峰值 {u[imax]:.1f}V @ t={t[imax]:.1f}s")

# 过压爬升结束：首次 U>252
ov_top = df[df["Umean"] > 252]
if len(ov_top):
    print(f"首次 Umean>252V: t={ov_top['t_s'].iloc[0]:.1f}s, U={ov_top['Umean'].iloc[0]:.1f}")

# 从峰值后找回到 228-232（回 230 带）
after_peak = df[df["t_s"] > t[imax]]
back_230 = after_peak[(after_peak["Umean"] >= 228) & (after_peak["Umean"] <= 232)]
if len(back_230):
    print(f"峰后回到 228-232V: t={back_230['t_s'].iloc[0]:.1f}s ~ {back_230['t_s'].iloc[-1]:.1f}s (首点 U={back_230['Umean'].iloc[0]:.1f})")

# 欠压：峰后首次持续 U<225
uv_start = after_peak[after_peak["Umean"] < 225]
if len(uv_start):
    print(f"开始明显下降(<225V): t={uv_start['t_s'].iloc[0]:.1f}s U={uv_start['Umean'].iloc[0]:.1f}")

print(f"末点 Umean={df['Umean'].iloc[-1]:.1f}V")

# 250→230 跳变：找相邻点差>15V
du = np.diff(u)
jump_idx = np.where(du < -15)[0]
if len(jump_idx):
    for j in jump_idx[:5]:
        print(f"急跌: t {t[j]:.1f}->{t[j+1]:.1f}s  U {u[j]:.1f}->{u[j+1]:.1f}V (Δ={du[j]:.1f})")

# 分段统计
segments = []
# 稳态 230 初段 t 5-30
s0 = df[(df.t_s >= 5) & (df.t_s < 30)]
segments.append(("稳态230(初)", s0))
# 爬升 t 30-160
s1 = df[(df.t_s >= 30) & (df.t_s < 160)]
segments.append(("过压爬升/高位", s1))
# 回230 t 160-200
s2 = df[(df.t_s >= 160) & (df.t_s < 200)]
segments.append(("回230段", s2))
# 欠压 t 200-end
s3 = df[df.t_s >= 200]
segments.append(("欠压下降", s3))

print("\n=== 分段统计 ===")
for name, seg in segments:
    if len(seg) == 0:
        continue
    print(
        f"{name}: t={seg['t_s'].iloc[0]:.0f}-{seg['t_s'].iloc[-1]:.0f}s "
        f"Umean {seg['Umean'].min():.1f}-{seg['Umean'].max():.1f} "
        f"Psum {seg['Psum'].mean():.0f}W Freq {seg['FreqU-2'].mean():.2f}Hz"
    )

# 频率范围
print(f"\nFreqU-2: {df['FreqU-2'].min():.3f} ~ {df['FreqU-2'].max():.3f} Hz")

# 三相平衡（t>10）
late = df[df.t_s > 10]
print(
    f"三相平衡(t>10s): max|U1-U2|={abs(late['Urms-1']-late['Urms-2']).max():.2f}V "
    f"|U2-U3|={abs(late['Urms-2']-late['Urms-3']).max():.2f}V"
)

# 期望墙钟：230-253@30s 爬+降各约30s
print("\n=== 与设定 230-253@30 + 230-195@30 对照 ===")
print("期望: 先 230→253 (~30s), 再 253→230 (~30s), 再 230→195 (~30s)")
climb = df[(df.t_s > 5) & (df.t_s < 80)]
print(f"  爬升段(5-80s) U: {climb['Umean'].iloc[0]:.0f} -> {climb['Umean'].iloc[-1]:.0f}")
mid = df[(df.t_s > 140) & (df.t_s < 210)]
if len(mid):
    print(f"  140-210s U: {mid['Umean'].iloc[0]:.0f} -> {mid['Umean'].iloc[-1]:.0f}")
