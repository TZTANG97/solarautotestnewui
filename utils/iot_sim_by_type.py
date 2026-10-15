# -*- coding: utf-8 -*-
"""按 testType 生成模拟工况 CSV（避免谐波等试验仍落 sample_overload）。"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from utils.iot_sim_overload import plant_sim_overload_csv, run_overload_sim_timeline


def _job_tt(job: Dict[str, Any]) -> str:
    params = job.get("params") if isinstance(job.get("params"), dict) else {}
    for src in (job, params):
        if not isinstance(src, dict):
            continue
        for k in ("testType", "test_type"):
            v = src.get(k)
            if v:
                return str(v).strip().lower()
    # WS startexper：testType 可能只在 commands.command JSON 里
    commands = job.get("commands") if isinstance(job.get("commands"), dict) else {}
    cmd = commands.get("command") if commands else None
    if isinstance(cmd, str) and cmd.strip().startswith("{"):
        try:
            import json as _json

            nested = _json.loads(cmd)
            if isinstance(nested, dict):
                v = nested.get("testType") or nested.get("test_type")
                if v:
                    return str(v).strip().lower()
        except Exception:
            pass
    elif isinstance(cmd, dict):
        v = cmd.get("testType") or cmd.get("test_type")
        if v:
            return str(v).strip().lower()
    return "overload"


def _widgets(job: Dict[str, Any]) -> Dict[str, Any]:
    params = job.get("params") if isinstance(job.get("params"), dict) else {}
    top = job.get("widgets") if isinstance(job.get("widgets"), dict) else {}
    nested = params.get("widgets") if isinstance(params.get("widgets"), dict) else {}
    out = dict(nested)
    out.update(top)
    return out


def _num(v: Any, default: float) -> float:
    try:
        if v is None or v == "":
            return float(default)
        return float(str(v).replace(",", ".").strip())
    except (TypeError, ValueError):
        return float(default)


def _rated_pn_un(job: Dict[str, Any]) -> Tuple[float, float]:
    """返回 (Pn_W, Un_V)。谐波分析器按 kW 读 Pn，造数仍用 W。"""
    w = _widgets(job)
    params = job.get("params") if isinstance(job.get("params"), dict) else {}
    pn_raw = (
        w.get("analysis_Pn")
        or w.get("Pn")
        or params.get("Pn")
        or 10000
    )
    un = _num(w.get("analysis_Un") or w.get("Un") or w.get("textEdit_S1_AC_VOLT") or 230, 230)
    pn = _num(pn_raw, 10000)
    # 网页常填 10000(W)；若 <200 视为已是 kW
    if pn < 200:
        pn_w = pn * 1000.0
    else:
        pn_w = pn
    return pn_w, un


def _clear_sim_stale(dest_dir: Path) -> None:
    """清掉目录里过载/旧 plan，避免谐波任务仍上传 sample_overload。"""
    dest_dir = Path(dest_dir)
    if not dest_dir.is_dir():
        return
    for name in ("sample_overload.csv", "sim_plan.json"):
        p = dest_dir / name
        if p.is_file():
            try:
                p.unlink()
            except OSError:
                pass
    for stale in dest_dir.glob("sample_overload*.csv"):
        try:
            stale.unlink()
        except OSError:
            pass


def plant_sim_harmonic_csv(job: Dict[str, Any], dest_dir: Path) -> Path:
    """南德谐波：33%/66%/100%.csv + voltage harmonic.csv（多行采样，供 MAX/THD）。"""
    import math
    import random

    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    _clear_sim_stale(dest_dir)
    pn_w, un = _rated_pn_un(job)
    in_a = (pn_w / un) if un > 0 else 43.5
    n_samples = 30
    dt_s = 1.0

    # 电流谐波：I(k)-{phase}-{order}
    i_headers: List[str] = ["Time [s]"]
    for ph in (1, 2, 3):
        for order in range(1, 41):
            i_headers.append(f"I(k)-{ph}-{order}")

    def _current_row(t: float, scale: float) -> List[float]:
        # 轻微抖动，模拟功率分析仪连续采样
        wobble = 1.0 + 0.01 * math.sin(t / 5.0) + random.uniform(-0.005, 0.005)
        row: List[float] = [round(t, 3)]
        for _ph in (1, 2, 3):
            for order in range(1, 41):
                if order == 1:
                    row.append(round(in_a * scale * wobble, 4))
                elif order % 2 == 1:
                    row.append(round(in_a * scale * 0.02 / order * wobble, 6))
                else:
                    row.append(round(in_a * scale * 0.005 / order * wobble, 6))
        return row

    for level, scale in (("33%", 0.33), ("66%", 0.66), ("100%", 1.0)):
        path = dest_dir / f"{level}.csv"
        lines = [",".join(i_headers)]
        for i in range(n_samples):
            lines.append(",".join(str(x) for x in _current_row(i * dt_s, scale)))
        path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")

    # 电压谐波：U(k)-1-{order}
    v_headers = ["Time [s]"] + [f"U(k)-1-{o}" for o in range(1, 51)]
    v_lines = [",".join(v_headers)]
    for i in range(n_samples):
        t = i * dt_s
        wobble = 1.0 + 0.003 * math.sin(t / 7.0) + random.uniform(-0.002, 0.002)
        v_row: List[float] = [round(t, 3)]
        for order in range(1, 51):
            if order == 1:
                v_row.append(round(un * wobble, 4))
            elif order % 2 == 1:
                v_row.append(round(un * 0.005 / order * wobble, 6))
            else:
                v_row.append(round(un * 0.002 / order * wobble, 6))
        v_lines.append(",".join(str(x) for x in v_row))
    (dest_dir / "voltage harmonic.csv").write_text(
        "\n".join(v_lines) + "\n",
        encoding="utf-8-sig",
    )
    _clear_sim_stale(dest_dir)
    return dest_dir


def _write_csv(path: Path, headers: List[str], rows: List[List[Any]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [",".join(headers)]
    for row in rows:
        lines.append(",".join(str(x) for x in row))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def plant_sim_dc_csv(job: Dict[str, Any], dest_dir: Path) -> Path:
    """直流分量：南德要 33%/66%/100%.csv（I(k)-n-DC + P-1）；巴西 5.9 同列可读。"""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    _clear_sim_stale(dest_dir)
    pn_w, un = _rated_pn_un(job)
    in_a = (pn_w / un) if un > 0 else 43.5
    headers = ["Time [s]", "I(k)-1-DC", "I(k)-2-DC", "I(k)-3-DC", "P-1", "P-SIGMA"]
    for level, scale in (("33%", 0.33), ("66%", 0.66), ("100%", 1.0)):
        idc = round(in_a * scale * 0.001, 6)  # 远低于 0.5%In
        p = round(pn_w * scale, 3)
        rows = [[i * 1.0, idc, idc, idc, p, p] for i in range(20)]
        _write_csv(dest_dir / f"{level}.csv", headers, rows)
    return dest_dir


def plant_sim_flicker_csv(job: Dict[str, Any], dest_dir: Path) -> Path:
    """闪变：巴西 5.4.16 需 Pst/Plt 列。"""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    _clear_sim_stale(dest_dir)
    pn_w, un = _rated_pn_un(job)
    headers = ["Time [s]", "P-SIGMA", "U-SIGMA", "Pst", "Plt", "Pst-1", "Plt-1"]
    rows = []
    for i in range(30):
        rows.append(
            [
                i * 1.0,
                round(pn_w, 3),
                round(un, 3),
                0.12,
                0.08,
                0.11,
                0.07,
            ]
        )
    _write_csv(dest_dir / "sample_flicker.csv", headers, rows)
    return dest_dir


def plant_sim_fixedpf_csv(job: Dict[str, Any], dest_dir: Path) -> Path:
    """固定 PF：南德要 pf=±0.9/1 子目录 + 0%~100%.csv；巴西读扁平 P/Q/PF。"""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    _clear_sim_stale(dest_dir)
    pn_w, un = _rated_pn_un(job)
    headers = ["Time [s]", "P-SIGMA", "Q-SIGMA", "PF-SIGMA", "P-1", "Q-1", "PF-1"]
    # 巴西扁平样例
    flat_rows = []
    for i in range(40):
        flat_rows.append([i * 0.5, round(pn_w, 3), 0.0, 1.0, round(pn_w, 3), 0.0, 1.0])
    _write_csv(dest_dir / "sample_fixedpf.csv", headers, flat_rows)
    # 南德子目录结构
    for sub, target_pf in (("pf=0.9", 0.9), ("pf=-0.9", -0.9), ("pf=1", 1.0)):
        sub_dir = dest_dir / sub
        sub_dir.mkdir(parents=True, exist_ok=True)
        for level in range(0, 101, 10):
            scale = max(level, 1) / 100.0
            p = pn_w * scale
            # Q ≈ P * tan(acos(pf)) 近似
            pf = abs(target_pf) if abs(target_pf) > 1e-6 else 1.0
            pf = min(pf, 0.999)
            q = p * math.tan(math.acos(pf))
            if target_pf < 0:
                q = -q
            rows = [
                [0.0, round(p, 3), round(q, 3), target_pf, round(p, 3), round(q, 3), target_pf],
                [1.0, round(p, 3), round(q, 3), target_pf, round(p, 3), round(q, 3), target_pf],
            ]
            _write_csv(sub_dir / f"{level}%.csv", headers, rows)
    return dest_dir


def plant_sim_reconnect_csv(job: Dict[str, Any], dest_dir: Path) -> Path:
    """重连：电压跌落再恢复，有功约 185s 后抬升（巴西 5.4.22）。"""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    _clear_sim_stale(dest_dir)
    pn_w, un = _rated_pn_un(job)
    headers = ["Time [s]", "U-SIGMA", "P-SIGMA", "U-1", "P-1"]
    rows: List[List[Any]] = []
    # 0–10s 正常 → 掉电 → 20s 电压恢复 → 205s 有功恢复（间隔≈185s）
    for i in range(0, 250):
        t = float(i)
        if t < 10:
            u, p = un, pn_w
        elif t < 20:
            u, p = 0.0, 0.0
        elif t < 205:
            u, p = un, 0.0
        else:
            u, p = un, pn_w
        rows.append([t, round(u, 3), round(p, 3), round(u, 3), round(p, 3)])
    _write_csv(dest_dir / "sample_reconnect.csv", headers, rows)
    return dest_dir


def plant_sim_ovuf_csv(job: Dict[str, Any], dest_dir: Path) -> Path:
    """过欠频：文件名带目标频率；后半段 P≈0 表示断联（巴西 5.4.15）。"""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    _clear_sim_stale(dest_dir)
    pn_w, _un = _rated_pn_un(job)
    headers = ["Time [s]", "Freq", "F-SIGMA", "P-SIGMA", "P-1"]
    for target in (47.5, 51.5):
        rows: List[List[Any]] = []
        for i in range(100):
            t = float(i)
            # 前半额定，后半断联
            p = pn_w if i < 50 else 0.0
            f = 50.0 if i < 40 else target
            rows.append([t, round(f, 3), round(f, 3), round(p, 3), round(p, 3)])
        _write_csv(dest_dir / f"ovuf_{target}Hz.csv", headers, rows)
    return dest_dir


def plant_sim_reactive_csv(job: Dict[str, Any], dest_dir: Path) -> Path:
    """无功注入/调节：P/Q 稳定段样例（巴西 5.4.13 / 南德 reactive 占位）。"""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    _clear_sim_stale(dest_dir)
    pn_w, un = _rated_pn_un(job)
    headers = ["Time [s]", "P-SIGMA", "Q-SIGMA", "PF-SIGMA", "U-SIGMA"]
    q = round(pn_w * 0.4358, 3)
    rows = [[i * 0.5, round(pn_w, 3), q, 0.9, round(un, 3)] for i in range(60)]
    _write_csv(dest_dir / "sample_reactiveqin.csv", headers, rows)
    return dest_dir


def plant_sim_activep_csv(job: Dict[str, Any], dest_dir: Path) -> Path:
    """有功调度 5.4.23：100%→10%Pn 台阶（供 consecutive_level_segments）。"""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    _clear_sim_stale(dest_dir)
    pn_w, un = _rated_pn_un(job)
    headers = ["Time [s]", "P-SIGMA", "Q-SIGMA", "U-SIGMA"]
    rows: List[List[Any]] = []
    t = 0.0
    for pu in (1.0, 0.8, 0.6, 0.4, 0.2, 0.1):
        for _ in range(20):
            rows.append([round(t, 3), round(pn_w * pu, 3), 0.0, round(un, 3)])
            t += 0.5
    _write_csv(dest_dir / "sample_activep.csv", headers, rows)
    return dest_dir


def plant_sim_fixedq_csv(job: Dict[str, Any], dest_dir: Path) -> Path:
    """定无功 5.24：额定 P + 目标 Q 台阶。"""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    _clear_sim_stale(dest_dir)
    pn_w, un = _rated_pn_un(job)
    qmax = pn_w * 0.4358
    headers = ["Time [s]", "P-SIGMA", "Q-SIGMA", "PF-SIGMA", "U-SIGMA"]
    rows: List[List[Any]] = []
    t = 0.0
    for q_pu in (1.0, 0.5, 0.0, -0.5, -1.0):
        q = qmax * q_pu
        for _ in range(16):
            rows.append([round(t, 3), round(pn_w, 3), round(q, 3), 0.9, round(un, 3)])
            t += 0.5
    _write_csv(dest_dir / "sample_fixedq.csv", headers, rows)
    return dest_dir


def plant_sim_cosphi_brazil_csv(job: Dict[str, Any], dest_dir: Path) -> Path:
    """Cos(φ)_Brazil 5.4.12：稳定 PF≈0.9。"""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    _clear_sim_stale(dest_dir)
    pn_w, un = _rated_pn_un(job)
    headers = ["Time [s]", "P-SIGMA", "Q-SIGMA", "PF-SIGMA", "U-SIGMA"]
    q = round(pn_w * math.tan(math.acos(0.9)), 3)
    rows = [[i * 0.5, round(pn_w, 3), q, 0.9, round(un, 3)] for i in range(48)]
    _write_csv(dest_dir / "sample_cosphibrazil.csv", headers, rows)
    return dest_dir


def plant_sim_freq_adapt_csv(job: Dict[str, Any], dest_dir: Path) -> Path:
    """频率适应性 5.4.20：扰动后有功回到额定附近。"""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    _clear_sim_stale(dest_dir)
    pn_w, un = _rated_pn_un(job)
    headers = ["Time [s]", "P-SIGMA", "FreqU-1", "U-SIGMA"]
    rows: List[List[Any]] = []
    t = 0.0
    for f, p_scale in ((50.0, 1.0), (51.5, 0.95), (50.0, 1.0), (48.5, 0.95), (50.0, 1.0)):
        for _ in range(12):
            rows.append([round(t, 3), round(pn_w * p_scale, 3), round(f, 3), round(un, 3)])
            t += 0.05
    _write_csv(dest_dir / "sample_frequencyadaptability.csv", headers, rows)
    return dest_dir


def plant_sim_volt_adapt_csv(job: Dict[str, Any], dest_dir: Path) -> Path:
    """电压适应性 5.4.21：过/欠压恢复后有功回额定。"""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    _clear_sim_stale(dest_dir)
    pn_w, un = _rated_pn_un(job)
    headers = ["Time [s]", "P-SIGMA", "U-SIGMA", "Urms-1"]
    rows: List[List[Any]] = []
    t = 0.0
    for u, p_scale in ((un, 1.0), (un * 1.1, 0.92), (un, 1.0), (un * 0.9, 0.92), (un, 1.0)):
        for _ in range(12):
            rows.append([round(t, 3), round(pn_w * p_scale, 3), round(u, 3), round(u, 3)])
            t += 0.5
    _write_csv(dest_dir / "sample_voltageadaptability.csv", headers, rows)
    return dest_dir


def plant_sim_freq_power_ctrl_csv(job: Dict[str, Any], dest_dir: Path, *, over_freq: bool) -> Path:
    """过频降载 5.4.19 / 欠频抗扰 5.4.18。"""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    _clear_sim_stale(dest_dir)
    pn_w, un = _rated_pn_un(job)
    headers = ["Time [s]", "P-SIGMA", "FreqU-1", "U-SIGMA"]
    rows: List[List[Any]] = []
    t = 0.0
    if over_freq:
        steps = ((50.0, 1.0), (50.2, 0.95), (50.5, 0.85), (51.0, 0.7), (50.0, 1.0))
        name = "sample_guopinjiangzai.csv"
    else:
        steps = ((50.0, 1.0), (49.5, 1.0), (49.0, 0.98), (50.0, 1.0))
        name = "sample_guoqianpin_immun.csv"
    for f, p_scale in steps:
        for _ in range(16):
            rows.append([round(t, 3), round(pn_w * p_scale, 3), round(f, 3), round(un, 3)])
            t += 0.2
    _write_csv(dest_dir / name, headers, rows)
    return dest_dir


def plant_sim_staticmppt_csv(job: Dict[str, Any], dest_dir: Path) -> Path:
    """静态 MPPT 5.4.26：效率列占位。"""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    _clear_sim_stale(dest_dir)
    pn_w, _un = _rated_pn_un(job)
    headers = ["Time [s]", "P-SIGMA", "Pdc", "eta_mppt", "eta_conv"]
    rows = []
    for i, pct in enumerate((1.0, 0.75, 0.5, 0.25)):
        p = pn_w * pct
        rows.append([i * 10.0, round(p, 3), round(p / 0.98, 3), 0.98, 0.97])
    _write_csv(dest_dir / "sample_staticmppt.csv", headers, rows)
    return dest_dir


_PHASE2_SHORT_TYPES = frozenset(
    {
        "activep",
        "active_p",
        "有功调度",
        "fixedq",
        "fixed_q",
        "定无功",
        "cosphibrazil",
        "cos_phi_brazil",
        "frequencyadaptability",
        "freqadapt",
        "频率适应性",
        "voltageadaptability",
        "voltadapt",
        "电压适应性",
        "guopinjiangzai",
        "过频降载",
        "guoqianpin_immun",
        "qianpinshengzai",
        "巴西过欠频稳定性",
        "欠频升载",
        "staticmppt",
        "static_mppt",
        "静态mppt",
        "静态MPPT测试",
    }
)


def plant_sim_csv_for_job(job: Dict[str, Any], dest_dir: Path) -> Path:
    """按试验类型落模拟 CSV；未知类型先落过载（兼容旧联调）。"""
    tt = _job_tt(job)
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    if tt in ("harmonic", "harmonics", "harmonic_current", "谐波", "谐波电流", "谐波电流测试"):
        return plant_sim_harmonic_csv(job, dest_dir)
    if tt in ("dccomponent", "dc_component", "直流分量", "直流电流"):
        return plant_sim_dc_csv(job, dest_dir)
    if tt in ("flicker", "voltage_flicker", "闪变", "电压闪变"):
        return plant_sim_flicker_csv(job, dest_dir)
    if tt in ("fixedpf", "fixed_pf", "固定pf", "固定PF"):
        return plant_sim_fixedpf_csv(job, dest_dir)
    if tt in ("reconnect", "重连"):
        return plant_sim_reconnect_csv(job, dest_dir)
    if tt in ("ovuf", "过欠压过欠频", "brazil_ovuf"):
        return plant_sim_ovuf_csv(job, dest_dir)
    if tt in ("reactiveqin", "reactive_qin", "无功注入"):
        return plant_sim_reactive_csv(job, dest_dir)
    if tt in ("activep", "active_p", "有功调度", "有功控制"):
        return plant_sim_activep_csv(job, dest_dir)
    if tt in ("fixedq", "fixed_q", "定无功", "固无功"):
        return plant_sim_fixedq_csv(job, dest_dir)
    if tt in ("cosphibrazil", "cos_phi_brazil", "cosphibrazil"):
        return plant_sim_cosphi_brazil_csv(job, dest_dir)
    if tt in ("frequencyadaptability", "freqadapt", "频率适应性"):
        return plant_sim_freq_adapt_csv(job, dest_dir)
    if tt in ("voltageadaptability", "voltadapt", "voltage_adaptability", "电压适应性"):
        return plant_sim_volt_adapt_csv(job, dest_dir)
    if tt in ("guopinjiangzai", "过频降载", "of_reduce"):
        return plant_sim_freq_power_ctrl_csv(job, dest_dir, over_freq=True)
    if tt in ("guoqianpin_immun", "qianpinshengzai", "巴西过欠频稳定性", "欠频升载"):
        return plant_sim_freq_power_ctrl_csv(job, dest_dir, over_freq=False)
    if tt in ("staticmppt", "static_mppt", "静态mppt", "静态MPPT测试", "静态MPPT"):
        return plant_sim_staticmppt_csv(job, dest_dir)
    csv_path, _plan, _rows = plant_sim_overload_csv(job, dest_dir)
    return Path(csv_path).parent


def run_sim_timeline_for_job(
    job: Dict[str, Any],
    *,
    dest_dir: Path,
    on_progress,
    set_measures,
) -> Tuple[Path, Optional[Any], List]:
    """返回 (data_dir, plan|None, rows)。谐波等走短进度条。"""
    tt = _job_tt(job)
    dest_dir = Path(dest_dir)
    short_msgs = {
        "harmonic": "谐波造数 33%/66%/100% + voltage harmonic",
        "harmonics": "谐波造数 33%/66%/100% + voltage harmonic",
        "谐波": "谐波造数 33%/66%/100% + voltage harmonic",
        "谐波电流": "谐波造数 33%/66%/100% + voltage harmonic",
        "谐波电流测试": "谐波造数 33%/66%/100% + voltage harmonic",
        "dccomponent": "直流分量造数 33%/66%/100%",
        "直流分量": "直流分量造数 33%/66%/100%",
        "flicker": "闪变造数 Pst/Plt",
        "电压闪变": "闪变造数 Pst/Plt",
        "fixedpf": "固定 PF 造数（含南德子目录）",
        "固定pf": "固定 PF 造数（含南德子目录）",
        "固定PF": "固定 PF 造数（含南德子目录）",
        "reconnect": "重连造数（电压恢复+有功延迟）",
        "重连": "重连造数（电压恢复+有功延迟）",
        "ovuf": "过欠频造数",
        "过欠压过欠频": "过欠频造数",
        "reactiveqin": "无功注入造数",
        "无功注入": "无功注入造数",
        "activep": "有功调度造数",
        "有功调度": "有功调度造数",
        "fixedq": "定无功造数",
        "定无功": "定无功造数",
        "cosphibrazil": "Cos(φ)_Brazil 造数",
        "frequencyadaptability": "频率适应性造数",
        "频率适应性": "频率适应性造数",
        "voltageadaptability": "电压适应性造数",
        "电压适应性": "电压适应性造数",
        "guopinjiangzai": "过频降载造数",
        "过频降载": "过频降载造数",
        "guoqianpin_immun": "欠频抗扰造数",
        "qianpinshengzai": "欠频升载造数",
        "staticmppt": "静态MPPT造数",
        "静态MPPT测试": "静态MPPT造数",
    }
    if tt in short_msgs or tt in _PHASE2_SHORT_TYPES or tt in (
        "harmonic",
        "harmonics",
        "harmonic_current",
        "dccomponent",
        "dc_component",
        "flicker",
        "voltage_flicker",
        "fixedpf",
        "fixed_pf",
        "reconnect",
        "ovuf",
        "brazil_ovuf",
        "reactiveqin",
        "reactive_qin",
        "谐波",
        "谐波电流",
        "谐波电流测试",
        "直流分量",
        "闪变",
        "电压闪变",
        "固定pf",
        "固定PF",
        "重连",
        "过欠压过欠频",
        "无功注入",
    ):
        data_dir = plant_sim_csv_for_job(job, dest_dir)
        msg = short_msgs.get(tt, f"{tt} 造数")
        on_progress(15, f"sim：{msg}", "prepare")
        on_progress(70, f"sim：写入 {tt} CSV", "S2")
        on_progress(95, f"sim：准备结案分析（{tt}）", "finish")
        if set_measures:
            set_measures(None)
        return data_dir, None, []
    if tt in (
        "overload",
        "overloads",
        "过载能力测试",
        "",
    ):
        csv_path, plan, rows = plant_sim_overload_csv(job, dest_dir)
        run_overload_sim_timeline(
            plan=plan,
            rows=rows,
            on_progress=on_progress,
            set_measures=set_measures,
        )
        return Path(csv_path).parent, plan, rows
    data_dir = plant_sim_csv_for_job(job, dest_dir)
    on_progress(20, f"sim：{tt} 占位 CSV（专用造数待补）", "prepare")
    on_progress(90, f"sim：{tt} 收尾，准备结案分析", "finish")
    if set_measures:
        set_measures(None)
    return data_dir, None, []
