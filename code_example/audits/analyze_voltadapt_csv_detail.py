# -*- coding: utf-8 -*-
"""深度对照 VoltAdapt_BR_5421.CSV 与 2026-08-22 13:50 试验日志。"""
import pandas as pd
import numpy as np

path = "E:/solarautotestnewui/docs/VoltAdapt_BR_5421.CSV"
df = pd.read_csv(path, encoding="utf-8-sig")
for c in ["Urms-1", "Urms-2", "Urms-3", "Irms-1", "Irms-2", "Irms-3", "P-1", "P-2", "P-3", "FreqU-2"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

df["ts"] = pd.to_datetime(
    df["Date"].astype(str) + " " + df["Time"].astype(str) + "." + df["Millisecond"].astype(int).astype(str).str.zfill(3),
    format="%Y/%m/%d %H:%M:%S.%f",
)
df["t_s"] = (df["ts"] - df["ts"].iloc[0]).dt.total_seconds()
df["Umean"] = (df["Urms-1"] + df["Urms-2"] + df["Urms-3"]) / 3.0
df["Psum"] = df["P-1"] + df["P-2"] + df["P-3"]

# 日志锚点（相对 CSV 首行）
anchors = {
    "csv_start": 0.0,
    "async_start_log": (pd.Timestamp("2026-08-22 13:52:51.075") - df["ts"].iloc[0]).total_seconds(),
    "first_volt_ac_sweep": (pd.Timestamp("2026-08-22 13:52:51.349") - df["ts"].iloc[0]).total_seconds(),
    "csv_end": float(df["t_s"].iloc[-1]),
    "wt_stop_approx": (pd.Timestamp("2026-08-22 13:57:01.072") - df["ts"].iloc[0]).total_seconds(),
    "volt_195_log": (pd.Timestamp("2026-08-22 13:58:00.083") - df["ts"].iloc[0]).total_seconds(),
    "wait_end_log": (pd.Timestamp("2026-08-22 13:58:00.519") - df["ts"].iloc[0]).total_seconds(),
}
print("=== 时间锚点 (相对 CSV 首行, 秒) ===")
for k, v in anchors.items():
    print(f"  {k}: {v:.1f}s")

print("\n=== 启机段 Urms-1=0 ===")
z = df[df["Urms-1"] < 1]
print(f"  行数 {len(z)}, 时长 {z['t_s'].max() - z['t_s'].min():.2f}s (首段)")
if len(z):
    print(f"  对应时刻 {z['ts'].iloc[0]} ~ {z['ts'].iloc[-1]}")

# 分段：过压爬升 / 回 230 / 欠压下降
async_t = anchors["async_start_log"]
seg_ov = df[(df["t_s"] >= async_t) & (df["t_s"] < async_t + 160)]
seg_uv = df[(df["t_s"] >= async_t + 160)]

print("\n=== 过压段 (ASYNC 后 ~160s) ===")
print(f"  Umean min={seg_ov.Umean.min():.1f} max={seg_ov.Umean.max():.1f}")
print(f"  Urms-2 max={seg_ov['Urms-2'].max():.2f} @ t={seg_ov.loc[seg_ov['Urms-2'].idxmax(), 't_s']:.1f}s")

print("\n=== 欠压段 (CSV 内剩余) ===")
if len(seg_uv):
    print(f"  Umean min={seg_uv.Umean.min():.1f} max={seg_uv.Umean.max():.1f}")
    print(f"  Urms-2 min={seg_uv['Urms-2'].min():.2f} @ t={seg_uv.loc[seg_uv['Urms-2'].idxmin(), 't_s']:.1f}s")
    print(f"  末行 Umean={seg_uv.Umean.iloc[-1]:.1f}V")

print("\n=== 三相平衡 (t>5s) ===")
late = df[df["t_s"] > 5]
print(f"  max|U1-U2|={abs(late['Urms-1']-late['Urms-2']).max():.2f}V")
print(f"  max|U2-U3|={abs(late['Urms-2']-late['Urms-3']).max():.2f}V")

print("\n=== 功率 ===")
print(f"  Psum mean={df.Psum.mean():.0f}W, max={df.Psum.max():.0f}W (t>30s: {late[late.t_s>30].Psum.mean():.0f}W)")

missing = df["FreqU-1"].astype(str).str.upper().eq("ERROR").sum()
print(f"\n=== FreqU-1 Error: {missing}/{len(df)} (均在 Urms-1≈0 段) ===")

print("\n=== 结论提示 ===")
print(f"  CSV 覆盖扫压约 {async_t:.0f}s ~ {df.t_s.iloc[-1]:.0f}s (相对首行)")
print(f"  日志 VOLT:AC 195 在 {anchors['volt_195_log']:.0f}s → 超出 CSV 末行 {df.t_s.iloc[-1]:.0f}s")
