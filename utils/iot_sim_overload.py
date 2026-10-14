# -*- coding: utf-8 -*-
"""过载模拟工况：按任务 widgets 步骤/时长生成 CSV，并压缩墙钟上报进度与 measures。"""
from __future__ import annotations

import math
import os
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

ProgressCb = Callable[[int, str, str], None]


def _widgets(job: Dict[str, Any]) -> Dict[str, Any]:
    top = job.get("widgets") if isinstance(job.get("widgets"), dict) else {}
    params = job.get("params") if isinstance(job.get("params"), dict) else {}
    nested = params.get("widgets") if isinstance(params.get("widgets"), dict) else {}
    if top and nested:
        out = dict(nested)
        out.update(top)
        return out
    return top or nested


def _num(raw: Any, default: float) -> float:
    try:
        if raw is None or raw == "":
            return float(default)
        return float(raw)
    except (TypeError, ValueError):
        return float(default)


def _unit_to_seconds(value: float, unit: str) -> float:
    u = str(unit or "").strip().lower()
    if u in ("小时", "hour", "hours", "h"):
        return value * 3600.0
    if u in ("分钟", "min", "mins", "minute", "minutes", "m"):
        return value * 60.0
    return value  # 秒


@dataclass
class OverloadSimPlan:
    un: float
    pn: float
    freq: float
    load_pct: float
    ac_wait_s: float
    s1_stabilize_s: float
    hold_s: float
    sample_dt_s: float
    wall_scale: float  # 墙钟秒 = 名义秒 / wall_scale

    @property
    def p_target(self) -> float:
        return self.pn * (self.load_pct / 100.0)

    @property
    def i_target(self) -> float:
        # 三相近似：P ≈ √3 · U · I · pf，sim 用 pf≈1
        if self.un <= 0:
            return 0.0
        return self.p_target / (math.sqrt(3.0) * self.un)

    @property
    def total_nominal_s(self) -> float:
        return self.ac_wait_s + self.s1_stabilize_s + self.hold_s


def build_overload_sim_plan(job: Dict[str, Any]) -> OverloadSimPlan:
    w = _widgets(job)
    un = _num(
        w.get("analysis_Un")
        or w.get("textEdit_S1_AC_VOLT")
        or w.get("Un")
        or 230,
        230,
    )
    pn = _num(w.get("analysis_Pn") or w.get("Pn") or w.get("analysisPn") or 10000, 10000)
    freq = _num(w.get("textEdit_S1_AC_FR") or w.get("freq") or 60, 60)
    load_pct = _num(w.get("_overloadLoadPct") or w.get("overloadLoadPct") or 100, 100)
    ac_wait = _unit_to_seconds(
        _num(w.get("textEdit_S1_ACWaitTIME") or 3, 3),
        str(w.get("comboBox_S1_ACWaitTIME") or "秒"),
    )
    s1 = _unit_to_seconds(
        _num(w.get("textEdit_S1_TIME") or 5, 5),
        str(w.get("comboBox_S1_TIME") or "分钟"),
    )
    hold = _unit_to_seconds(
        _num(
            w.get("_overloadHoldMin")
            or w.get("textEdit_S3_TIME_2")
            or w.get("textEdit_S3_TIME")
            or 90,
            90,
        ),
        str(w.get("comboBox_S3_TIME_2") or w.get("comboBox_S3_TIME") or "分钟"),
    )
    # 采样：默认 1s；长保持可稀疏，避免超大 CSV
    sample_dt = _num(os.environ.get("SOLAR_SIM_SAMPLE_DT_SEC") or 1.0, 1.0)
    if sample_dt < 0.1:
        sample_dt = 0.1
    if hold > 3600 and sample_dt < 2.0:
        sample_dt = 2.0

    # 墙钟压缩：默认把整段压到 ~60s；SOLAR_SIM_REALTIME=1 则 1:1
    realtime = str(os.environ.get("SOLAR_SIM_REALTIME") or "").strip().lower() in (
        "1",
        "true",
        "yes",
    )
    if realtime:
        wall_scale = 1.0
    else:
        target_wall = _num(os.environ.get("SOLAR_SIM_TARGET_WALL_SEC") or 60, 60)
        if target_wall < 5:
            target_wall = 5
        total = max(ac_wait + s1 + hold, 1.0)
        wall_scale = max(total / target_wall, 1.0)
        env_scale = str(os.environ.get("SOLAR_SIM_TIME_SCALE") or "").strip()
        if env_scale:
            wall_scale = max(_num(env_scale, wall_scale), 1.0)

    return OverloadSimPlan(
        un=un,
        pn=pn,
        freq=freq,
        load_pct=load_pct,
        ac_wait_s=ac_wait,
        s1_stabilize_s=s1,
        hold_s=hold,
        sample_dt_s=sample_dt,
        wall_scale=wall_scale,
    )


def _jitter(base: float, rel: float = 0.004) -> float:
    return base * (1.0 + random.uniform(-rel, rel))


def generate_overload_series(plan: OverloadSimPlan) -> List[Dict[str, Any]]:
    """名义时间轴上的采点（供 CSV + 上报）。"""
    rows: List[Dict[str, Any]] = []
    t = 0.0
    end = plan.total_nominal_s
    dt = plan.sample_dt_s
    while t <= end + 1e-9:
        if t < plan.ac_wait_s:
            # 启机等待：电压已上、功率爬升
            ratio = t / max(plan.ac_wait_s, 1e-6)
            p = plan.p_target * 0.15 * ratio
            u = plan.un * (0.92 + 0.08 * ratio)
            phase = "ac_wait"
        elif t < plan.ac_wait_s + plan.s1_stabilize_s:
            # S1 稳定：爬到目标功率
            local = t - plan.ac_wait_s
            ratio = min(1.0, local / max(plan.s1_stabilize_s, 1e-6))
            p = plan.p_target * (0.15 + 0.85 * ratio)
            u = plan.un
            phase = "s1"
        else:
            # S3 过载保持
            local = t - plan.ac_wait_s - plan.s1_stabilize_s
            # 轻微热漂移
            drift = 1.0 + 0.008 * math.sin(local / 120.0)
            p = plan.p_target * drift
            u = plan.un * (1.0 + 0.001 * math.sin(local / 90.0))
            phase = "hold"
        i = p / (math.sqrt(3.0) * u) if u > 0 else 0.0
        rows.append(
            {
                "t": round(t, 3),
                "p": round(_jitter(p), 2),
                "u": round(_jitter(u, 0.0015), 3),
                "i": round(_jitter(i, 0.003), 4),
                "f": round(_jitter(plan.freq, 0.0004), 4),
                "phase": phase,
            }
        )
        t += dt
    return rows


def write_overload_csv(path: Path, rows: List[Dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["Time [s],P-SIGMA,U-SIGMA,Irms-1"]
    for r in rows:
        lines.append(f"{r['t']},{r['p']},{r['u']},{r['i']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _wall_sleep(nominal_s: float, plan: OverloadSimPlan) -> None:
    wall = max(nominal_s / max(plan.wall_scale, 1e-6), 0.0)
    if wall <= 0:
        return
    # 分段 sleep，便于响应中断（当前无 abort 钩子，仍避免一次长 sleep）
    end = time.time() + wall
    while True:
        remain = end - time.time()
        if remain <= 0:
            break
        time.sleep(min(remain, 0.25))


def run_overload_sim_timeline(
    *,
    plan: OverloadSimPlan,
    rows: List[Dict[str, Any]],
    on_progress: ProgressCb,
    set_measures: Optional[Callable[[Optional[Dict[str, float]]], None]] = None,
) -> None:
    """
    按步骤推进进度，并按墙钟间隔上报 measures（供曲线落库）。
    CSV 已按名义时长生成；此处只压缩墙钟等待。
    """

    def push(pct: int, text: str, step: str, sample: Optional[Dict[str, float]] = None) -> None:
        if set_measures and sample is not None:
            set_measures(
                {
                    "u_rms": float(sample["u"]),
                    "i_rms": float(sample["i"]),
                    "p": float(sample["p"]),
                    "freq": float(sample["f"]),
                }
            )
        on_progress(pct, text, step)

    push(5, "sim：解析过载参数 / 标准", "prepare", rows[0] if rows else None)

    # S1 AC 等待
    push(
        12,
        f"sim S1：交流启机等待 {plan.ac_wait_s:.0f}s（墙钟 ÷{plan.wall_scale:.0f}）",
        "S1_ac_wait",
        rows[0] if rows else None,
    )
    _wall_sleep(plan.ac_wait_s, plan)

    # S1 稳定
    push(
        25,
        f"sim S1：稳定/启机 {plan.s1_stabilize_s/60:.1f} min @ Un={plan.un:g}V",
        "S1_stabilize",
        rows[max(0, len(rows) // 10)] if rows else None,
    )
    # 稳定段内多报几点
    s1_end_t = plan.ac_wait_s + plan.s1_stabilize_s
    s1_rows = [r for r in rows if plan.ac_wait_s <= r["t"] <= s1_end_t]
    chunks = max(3, min(8, len(s1_rows)))
    for i in range(chunks):
        idx = int(i * (len(s1_rows) - 1) / max(chunks - 1, 1)) if s1_rows else 0
        sample = s1_rows[idx] if s1_rows else None
        pct = 25 + int(15 * (i + 1) / chunks)
        push(pct, f"sim S1：稳定中 {i+1}/{chunks}", "S1_stabilize", sample)
        _wall_sleep(plan.s1_stabilize_s / chunks, plan)

    # S3 保持
    hold_rows = [r for r in rows if r["t"] >= s1_end_t]
    push(
        45,
        f"sim S3：过载保持 {plan.hold_s/60:.1f} min @ {plan.load_pct:g}% Pn={plan.pn:g}W",
        "S3_hold",
        hold_rows[0] if hold_rows else None,
    )
    hold_chunks = max(6, min(24, len(hold_rows)))
    for i in range(hold_chunks):
        idx = int(i * (len(hold_rows) - 1) / max(hold_chunks - 1, 1)) if hold_rows else 0
        sample = hold_rows[idx] if hold_rows else None
        pct = 45 + int(45 * (i + 1) / hold_chunks)
        elapsed_min = (sample["t"] - s1_end_t) / 60.0 if sample else 0.0
        push(
            min(pct, 92),
            f"sim S3：保持中 {elapsed_min:.1f}/{plan.hold_s/60:.1f} min P≈{sample['p'] if sample else plan.p_target:.0f}W",
            "S3_hold",
            sample,
        )
        _wall_sleep(plan.hold_s / hold_chunks, plan)

    push(96, "sim S5：关机 / 收尾", "S5_shutdown", hold_rows[-1] if hold_rows else None)
    _wall_sleep(min(5.0, plan.ac_wait_s or 3.0), plan)
    if set_measures:
        set_measures(None)
    push(99, "sim：采集结束，准备结案分析", "finish")


def plant_sim_overload_csv(
    job: Dict[str, Any], dest_dir: Path
) -> Tuple[Path, OverloadSimPlan, List[Dict[str, Any]]]:
    plan = build_overload_sim_plan(job)
    rows = generate_overload_series(plan)
    dest_dir.mkdir(parents=True, exist_ok=True)
    csv_path = dest_dir / "sample_overload.csv"
    write_overload_csv(csv_path, rows)
    meta = {
        "un": plan.un,
        "pn": plan.pn,
        "freq": plan.freq,
        "load_pct": plan.load_pct,
        "ac_wait_s": plan.ac_wait_s,
        "s1_stabilize_s": plan.s1_stabilize_s,
        "hold_s": plan.hold_s,
        "sample_dt_s": plan.sample_dt_s,
        "wall_scale": plan.wall_scale,
        "points": len(rows),
    }
    (dest_dir / "sim_plan.json").write_text(
        __import__("json").dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return csv_path, plan, rows
