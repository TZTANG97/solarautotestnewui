# -*- coding: utf-8 -*-
"""按 testType 生成模拟工况 CSV（避免谐波等试验仍落 sample_overload）。"""
from __future__ import annotations

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


def plant_sim_harmonic_csv(job: Dict[str, Any], dest_dir: Path) -> Path:
    """南德谐波：33%/66%/100%.csv + voltage harmonic.csv。"""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    pn_w, un = _rated_pn_un(job)
    in_a = (pn_w / un) if un > 0 else 43.5

    # 电流谐波：I(k)-{phase}-{order}
    i_headers: List[str] = ["Time [s]"]
    for ph in (1, 2, 3):
        for order in range(1, 41):
            i_headers.append(f"I(k)-{ph}-{order}")

    def _current_row(scale: float) -> List[float]:
        row = [0.0]
        for _ph in (1, 2, 3):
            for order in range(1, 41):
                if order == 1:
                    row.append(round(in_a * scale, 4))
                elif order % 2 == 1:
                    row.append(round(in_a * scale * 0.02 / order, 6))
                else:
                    row.append(round(in_a * scale * 0.005 / order, 6))
        return row

    for level, scale in (("33%", 0.33), ("66%", 0.66), ("100%", 1.0)):
        path = dest_dir / f"{level}.csv"
        lines = [",".join(i_headers), ",".join(str(x) for x in _current_row(scale))]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")

    # 电压谐波：U(k)-1-{order}
    v_headers = ["Time [s]"] + [f"U(k)-1-{o}" for o in range(1, 51)]
    v_row: List[float] = [0.0]
    for order in range(1, 51):
        if order == 1:
            v_row.append(round(un, 4))
        elif order % 2 == 1:
            v_row.append(round(un * 0.005 / order, 6))
        else:
            v_row.append(round(un * 0.002 / order, 6))
    (dest_dir / "voltage harmonic.csv").write_text(
        ",".join(v_headers) + "\n" + ",".join(str(x) for x in v_row) + "\n",
        encoding="utf-8-sig",
    )
    # 删除误导性分析的过载样例
    for stale in dest_dir.glob("sample_overload*.csv"):
        try:
            stale.unlink()
        except OSError:
            pass
    return dest_dir


def plant_sim_csv_for_job(job: Dict[str, Any], dest_dir: Path) -> Path:
    """按试验类型落模拟 CSV；未知类型先落过载（兼容旧联调）。"""
    tt = _job_tt(job)
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    if tt in ("harmonic", "harmonics", "harmonic_current", "谐波", "谐波电流", "谐波电流测试"):
        return plant_sim_harmonic_csv(job, dest_dir)
    # 其它南德条款：暂无专用造数时给最小占位，避免写成过载样例名
    if tt in (
        "flicker",
        "voltage_flicker",
        "闪变",
        "电压闪变",
        "dccomponent",
        "dc_component",
        "直流分量",
        "fixedpf",
        "fixed_pf",
        "固定pf",
        "固定PF",
        "reconnect",
        "重连",
        "ovuf",
        "过欠压过欠频",
    ):
        # 仍优先谐波结构不够用；给明确文件名便于排查，并去掉 overload 样例
        for stale in dest_dir.glob("sample_overload*.csv"):
            try:
                stale.unlink()
            except OSError:
                pass
        stub = dest_dir / f"sample_{tt}.csv"
        pn_w, un = _rated_pn_un(job)
        stub.write_text(
            "Time [s],P-SIGMA,U-SIGMA,Irms-1\n"
            f"0.0,{pn_w},{un},{pn_w / max(un, 1):.3f}\n"
            f"1.0,{pn_w},{un},{pn_w / max(un, 1):.3f}\n",
            encoding="utf-8-sig",
        )
        return dest_dir
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
    if tt in ("harmonic", "harmonics", "harmonic_current", "谐波", "谐波电流", "谐波电流测试"):
        data_dir = plant_sim_harmonic_csv(job, dest_dir)
        on_progress(10, "sim：谐波造数 33%/66%/100% + voltage harmonic", "prepare")
        on_progress(40, "sim：写入电流/电压谐波 CSV", "S2")
        on_progress(80, "sim：谐波采集完成", "S3")
        on_progress(95, "sim：准备结案分析（NanDe harmonic）", "finish")
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
    # 其它类型：落占位 CSV + 短进度
    data_dir = plant_sim_csv_for_job(job, dest_dir)
    on_progress(20, f"sim：{tt} 占位 CSV（专用造数待补）", "prepare")
    on_progress(90, f"sim：{tt} 收尾，准备结案分析", "finish")
    if set_measures:
        set_measures(None)
    return data_dir, None, []
