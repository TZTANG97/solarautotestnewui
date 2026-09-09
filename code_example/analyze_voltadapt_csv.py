# -*- coding: utf-8 -*-
"""Quick analysis of docs/VoltAdapt_BR_5421.CSV"""
import pandas as pd
import numpy as np

path = "E:/solarautotestnewui/docs/VoltAdapt_BR_5421.CSV"
df = pd.read_csv(path, encoding="utf-8-sig")
for c in ["Urms-1", "Urms-2", "Urms-3", "Irms-1", "Irms-2", "Irms-3", "P-1", "P-2", "P-3", "FreqU-2", "FreqU-3"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

df["ts"] = pd.to_datetime(
    df["Date"].astype(str) + " " + df["Time"].astype(str) + "." + df["Millisecond"].astype(int).astype(str).str.zfill(3),
    format="%Y/%m/%d %H:%M:%S.%f",
)
df["t_s"] = (df["ts"] - df["ts"].iloc[0]).dt.total_seconds()
dur = df["t_s"].iloc[-1]

print("=== 基本信息 ===")
print(f"行数: {len(df)}, 时长: {dur:.1f}s, 约 {len(df)/dur:.1f} Hz")

print("\n=== 三相电压统计 ===")
for i in (1, 2, 3):
    u = df[f"Urms-{i}"]
    print(
        f"Urms-{i}: min={u.min():.2f} max={u.max():.2f} mean={u.mean():.2f} "
        f"<1V占比={((u < 1).mean() * 100):.1f}%"
    )

fu1_err = df["FreqU-1"].astype(str).str.strip().str.upper().eq("ERROR").sum()
print(f"FreqU-1 'Error' 行数: {fu1_err}/{len(df)}")
print(f"FreqU-2/3 均值 Hz: {df['FreqU-2'].mean():.3f}, {df['FreqU-3'].mean():.3f}")

first_ok = df.index[df["Urms-1"] > 10]
if len(first_ok):
    r = first_ok[0]
    print(f"\n=== 启机段 ===")
    print(f"Urms-1 首次 >10V: t={df.loc[r, 't_s']:.1f}s (行 {r})")
    early = df[df["t_s"] < df.loc[r, "t_s"]]
    if len(early):
        print(f"此前 Urms-1=0 时 Urms-2 mean={early['Urms-2'].mean():.1f} Urms-3 mean={early['Urms-3'].mean():.1f}")

print("\n=== 时间分段 (30s) ===")
bins = np.arange(0, dur + 30, 30)
for i in range(len(bins) - 1):
    m = (df["t_s"] >= bins[i]) & (df["t_s"] < bins[i + 1])
    if m.sum() < 5:
        continue
    sub = df[m]
    print(
        f"t={int(bins[i]):3d}-{int(bins[i+1]):3d}s "
        f"U1={sub['Urms-1'].mean():5.1f} U2={sub['Urms-2'].mean():5.1f} U3={sub['Urms-3'].mean():5.1f}"
    )

print("\n=== 扫压范围 ===")
print(f"Urms-2 峰值 {df['Urms-2'].max():.2f}V @ t={df.loc[df['Urms-2'].idxmax(), 't_s']:.1f}s")
print(f"Urms-2 最低 {df['Urms-2'].min():.2f}V @ t={df.loc[df['Urms-2'].idxmin(), 't_s']:.1f}s")
print(f"达到 ≥252V: {(df['Urms-2'] >= 252).any()}")
print(f"达到 ≤195V: {(df['Urms-2'] <= 195).any()} (欠压目标通常 195)")

late = df[df["t_s"] > 60]
if len(late):
    print("\n=== t>60s 稳态段 ===")
    print(f"三相均值 U1/U2/U3: {late['Urms-1'].mean():.1f} / {late['Urms-2'].mean():.1f} / {late['Urms-3'].mean():.1f}")
    print(f"相间最大偏差 |U2-U1| max={abs(late['Urms-2'] - late['Urms-1']).max():.2f}V")
    ps = late["P-1"] + late["P-2"] + late["P-3"]
    print(f"总有功 P mean={ps.mean():.0f}W max={ps.max():.0f}W")
