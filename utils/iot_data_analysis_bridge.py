# -*- coding: utf-8 -*-
"""台架结案 → SolarTestDataAnalysisApp 无头处理 → 报告路径回填。"""
from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.iot_data_analysis_map import (
    PHASE1_AUTO_PACKS,
    PHASE1_AUTO_TESTS,
    resolve_analysis_target,
)

logger = logging.getLogger(__name__)

_DEFAULT_ANALYSIS_ROOTS = (
    Path(r"E:\MyProject\SolarTestDataAnalysisApp"),
    Path(r"E:\SolarTestDataAnalysisApp"),
)


def _analysis_root() -> Optional[Path]:
    env = str(os.environ.get("SOLAR_DATA_ANALYSIS_ROOT") or "").strip()
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    for cand in _DEFAULT_ANALYSIS_ROOTS:
        if cand.is_dir():
            return cand
    return None


def _analysis_python(root: Path) -> Path:
    # 优先分析项目自己的 .venv
    for rel in (".venv/Scripts/python.exe", "CEI/.venv/Scripts/python.exe"):
        p = root / rel
        if p.is_file():
            return p
    return Path(sys.executable)


def _job_params(job: Dict[str, Any]) -> Dict[str, Any]:
    return job.get("params") if isinstance(job.get("params"), dict) else {}


def _job_widgets(job: Dict[str, Any]) -> Dict[str, Any]:
    """IOT 任务 widgets 常在 params.widgets，不只是顶层 widgets。"""
    top = job.get("widgets") if isinstance(job.get("widgets"), dict) else {}
    nested = _job_params(job).get("widgets")
    nested = nested if isinstance(nested, dict) else {}
    if top and nested:
        merged = dict(nested)
        merged.update(top)
        return merged
    return top or nested


def _job_test_type(job: Dict[str, Any], result: Optional[Dict[str, Any]] = None) -> str:
    params = _job_params(job)
    summary = {}
    if isinstance(result, dict):
        summary = result.get("result_summary") if isinstance(result.get("result_summary"), dict) else {}
    for src in (job, params, summary):
        if not isinstance(src, dict):
            continue
        for k in ("testType", "test_type"):
            v = src.get(k)
            if v:
                return str(v).strip().lower()
    return ""


def _job_solar_standard(job: Dict[str, Any], result: Dict[str, Any]) -> str:
    params = _job_params(job)
    for src in (
        _job_widgets(job),
        params,
        (result.get("result_summary") or {}) if isinstance(result.get("result_summary"), dict) else {},
    ):
        if not isinstance(src, dict):
            continue
        for k in ("solarStandard", "solar_standard", "standard"):
            v = src.get(k)
            if v:
                return str(v)
    return "thai"


def _collect_analysis_params(job: Dict[str, Any]) -> Dict[str, Any]:
    """从 job.params / widgets（含 params.widgets）抽额定参数。"""
    out: Dict[str, Any] = {}
    params = _job_params(job)
    widgets = _job_widgets(job)
    nested = params.get("analysisParams") or params.get("analysis_params") or {}
    if isinstance(nested, dict):
        out.update(nested)
    for key in ("Pn", "Un", "In", "SeMax", "PeMax", "Srated", "reconnect_time", "rated_power"):
        if key in params and params[key] not in (None, ""):
            out[key] = params[key]
        elif key in widgets and widgets[key] not in (None, ""):
            out[key] = widgets[key]
    # 常见 Dialog 字段兜底
    alias = {
        "textEdit_Pn": "Pn",
        "textEdit_Un": "Un",
        "textEdit_In": "In",
        "textEdit_SeMax": "SeMax",
        "textEdit_S1_AC_VOLT": "Un",
        # IOT 开测页「数据分析额定参数」
        "analysis_Pn": "Pn",
        "analysis_Un": "Un",
        "analysis_In": "In",
        "analysis_SeMax": "SeMax",
        "analysisPn": "Pn",
        "analysisSeMax": "SeMax",
    }
    for src_k, dst_k in alias.items():
        if dst_k not in out and widgets.get(src_k) not in (None, ""):
            out[dst_k] = widgets.get(src_k)
    # 环境默认（工控机可设 SOLAR_ANALYSIS_PN 等）
    env_map = {
        "Pn": "SOLAR_ANALYSIS_PN",
        "Un": "SOLAR_ANALYSIS_UN",
        "In": "SOLAR_ANALYSIS_IN",
        "SeMax": "SOLAR_ANALYSIS_SEMAX",
    }
    for k, env_k in env_map.items():
        if k not in out or out[k] in (None, ""):
            ev = str(os.environ.get(env_k) or "").strip()
            if ev:
                out[k] = ev
    # 数值化
    for k, v in list(out.items()):
        try:
            if isinstance(v, str) and v.strip():
                out[k] = float(v) if ("." in v or "e" in v.lower()) else int(v)
        except ValueError:
            pass
    return out


def _dir_has_csv(path: Path) -> bool:
    try:
        return path.is_dir() and any(path.glob("*.csv"))
    except OSError:
        return False


def _pick_input_dir(repo_root: Path, result: Dict[str, Any]) -> Optional[Path]:
    summary = result.get("result_summary") if isinstance(result.get("result_summary"), dict) else {}
    # 显式目录
    for key in ("analysis_input_dir", "analysisInputDir", "data_dir", "dataDir"):
        raw = summary.get(key)
        if raw:
            p = Path(str(raw))
            if not p.is_absolute():
                p = repo_root / p
            if p.exists():
                return p if p.is_dir() else p.parent
    # report_files 里找 CSV 父目录（按试验关键词优先，勿永远偏向 overload）
    prefer_keys = summary.get("analysis_csv_prefer_keys") or ()
    if not prefer_keys:
        tt = str(summary.get("testType") or summary.get("test_type") or "").lower()
        if tt in ("harmonic", "harmonics", "谐波", "谐波电流"):
            prefer_keys = ("33%", "66%", "100%", "harmonic", "voltage")
        elif tt in ("overload", "overloads", "过载"):
            prefer_keys = ("overload", "过载", "542", "5.4.2")
        else:
            prefer_keys = (tt,) if tt else ()
    files = summary.get("report_files") or summary.get("reportFiles") or []
    csv_parents: List[Path] = []
    preferred: List[Path] = []
    for item in files:
        if isinstance(item, dict):
            raw = item.get("path") or item.get("file") or ""
        else:
            raw = item
        p = Path(str(raw or ""))
        if not p.is_absolute():
            p = repo_root / p
        name_l = p.name.lower()
        if p.is_file() and p.suffix.lower() == ".csv":
            csv_parents.append(p.parent)
            if prefer_keys and any(k.lower() in name_l for k in prefer_keys):
                preferred.append(p.parent)
        elif p.is_dir() and _dir_has_csv(p):
            return p
    if preferred:
        preferred.sort(key=lambda d: d.stat().st_mtime if d.exists() else 0, reverse=True)
        return preferred[0]
    if csv_parents:
        csv_parents.sort(key=lambda d: d.stat().st_mtime if d.exists() else 0, reverse=True)
        return csv_parents[0]
    # 兜底：command_data / dewetron 最近目录（含 csv 的文件夹或扁平 csv 目录）
    for base in (
        repo_root / "command_save_files" / "command_data",
        repo_root / "command_save_files" / "dewetron_data",
    ):
        if not base.is_dir():
            continue
        if _dir_has_csv(base):
            return base
        dirs = [p for p in base.iterdir() if p.is_dir()]
        dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
        for d in dirs[:12]:
            if _dir_has_csv(d) or any(d.rglob("*.csv")):
                # 若 csv 在子目录，取含 csv 的最近子目录
                if _dir_has_csv(d):
                    return d
                nested = sorted(
                    (p.parent for p in d.rglob("*.csv")),
                    key=lambda x: x.stat().st_mtime if x.exists() else 0,
                    reverse=True,
                )
                if nested:
                    return nested[0]
    return None


def remember_analysis_input_dir(result: Dict[str, Any], repo_root: Path) -> Optional[Path]:
    """结案收集原始文件后，把最可能的 CSV 目录记入 summary，供处理直接使用。"""
    picked = _pick_input_dir(Path(repo_root), result)
    if not picked:
        return None
    summary = result.get("result_summary")
    if not isinstance(summary, dict):
        summary = {}
        result["result_summary"] = summary
    summary["analysis_input_dir"] = str(picked)
    return picked


def _append_report_files(result: Dict[str, Any], paths: List[Path]) -> None:
    summary = result.get("result_summary")
    if not isinstance(summary, dict):
        summary = {}
        result["result_summary"] = summary
    listed = list(summary.get("report_files") or [])
    existing = set()
    for item in listed:
        if isinstance(item, dict):
            existing.add(str(item.get("path") or ""))
        else:
            existing.add(str(item))
    for p in paths:
        s = str(p)
        if s and s not in existing:
            listed.append({"path": s, "name": p.name, "kind": "analysis_report"})
            existing.add(s)
    summary["report_files"] = listed


def run_analysis_after_job(
    *,
    repo_root: Path,
    job: Dict[str, Any],
    result: Dict[str, Any],
    timeout_sec: float = 600.0,
) -> Dict[str, Any]:
    """
    结案成功时尝试跑数据处理。失败只记日志/摘要，不改写任务 success/failed。
    """
    info: Dict[str, Any] = {"ran": False, "skipped": True, "reason": ""}
    status = str(result.get("status") or "").lower()
    if status not in ("success", "ok"):
        info["reason"] = f"status={status} 不自动处理"
        _store_analysis_meta(result, info)
        return info

    tt = _job_test_type(job, result)
    if tt not in PHASE1_AUTO_TESTS:
        info["reason"] = f"testType={tt or '(空)'} 不在一期自动处理列表"
        _store_analysis_meta(result, info)
        return info

    sid = _job_solar_standard(job, result)
    target = resolve_analysis_target(test_type=tt, solar_standard=sid)
    if not target:
        info["reason"] = f"无法映射 testType={tt} standard={sid}"
        _store_analysis_meta(result, info)
        return info

    if target["standard_pack"] not in PHASE1_AUTO_PACKS:
        info["reason"] = (
            f"pack={target['standard_pack']} 不在一期自动处理包 "
            f"({', '.join(sorted(PHASE1_AUTO_PACKS))})"
        )
        _store_analysis_meta(result, info)
        return info

    root = _analysis_root()
    if root is None:
        info["reason"] = "未找到 SolarTestDataAnalysisApp（设 SOLAR_DATA_ANALYSIS_ROOT）"
        _store_analysis_meta(result, info)
        return info

    input_dir = _pick_input_dir(Path(repo_root), result)
    if input_dir is None:
        info["reason"] = "未找到 CSV 输入目录"
        _store_analysis_meta(result, info)
        return info

    params = _collect_analysis_params(job)
    # 巴西过载缺 Pn 则跳过（避免空跑）
    if target["standard_pack"] == "BRAZIL_140" and target["test_code"] == "5.4.2":
        if not params.get("Pn"):
            info["reason"] = "过载分析缺少 Pn（widgets/params/SOLAR_ANALYSIS_PN）"
            _store_analysis_meta(result, info)
            return info
        if not params.get("SeMax"):
            params["SeMax"] = params["Pn"]
    # 南德多数条款需要 Pn；谐波/直流注入另需 Un
    if target["standard_pack"] == "CEI_Nbis_NanDe":
        need_pn = target["test_code"] in {
            "harmonic",
            "dc.injection",
            "fixed.displacement.factor",
            "reactive.power",
            "active.power.control",
        }
        need_un = target["test_code"] in {"harmonic", "dc.injection"}
        if need_pn and not params.get("Pn"):
            info["reason"] = f"南德 {target['test_code']} 缺少 Pn（analysis_Pn）"
            _store_analysis_meta(result, info)
            return info
        if need_un and not params.get("Un"):
            # 尝试从交流电压字段已在 _collect 里兜底；仍缺则跳过
            info["reason"] = f"南德 {target['test_code']} 缺少 Un（analysis_Un / 交流电压）"
            _store_analysis_meta(result, info)
            return info
        # 南德谐波处理器按 kW 读 Pn：网页填 10000(W) 时自动换算
        if target["test_code"] == "harmonic" and params.get("Pn") is not None:
            try:
                pn_v = float(params["Pn"])
                if pn_v >= 200:
                    params["Pn"] = pn_v / 1000.0
            except (TypeError, ValueError):
                pass
    # 把 testType 写入 summary，便于选 CSV 时不要误偏 overload
    summary = result.get("result_summary")
    if not isinstance(summary, dict):
        summary = {}
        result["result_summary"] = summary
    summary.setdefault("testType", tt)

    out_dir = Path(repo_root) / "command_save_files" / "analysis_reports" / f"job_{job.get('id') or job.get('jobId') or 'x'}_{int(time.time())}"
    out_dir.mkdir(parents=True, exist_ok=True)

    py = _analysis_python(root)
    script = root / "CEI" / "run_headless.py"
    if not script.is_file():
        info["reason"] = f"缺少无头脚本: {script}"
        return info

    result_json = out_dir / "headless_result.json"
    cmd = [
        str(py),
        str(script),
        "--standard",
        target["standard_pack"],
        "--test",
        target["test_code"],
        "--input",
        str(input_dir),
        "--output",
        str(out_dir),
        "--params-json",
        json.dumps(params, ensure_ascii=True),
        "--result-json",
        str(result_json),
    ]
    info.update(
        {
            "skipped": False,
            "ran": True,
            "target": target,
            "input_dir": str(input_dir),
            "output_dir": str(out_dir),
            "params": params,
            "cmd": cmd,
        }
    )
    env = dict(os.environ)
    env["PYTHONPATH"] = str(root / "CEI" / "src") + (
        os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else ""
    )
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            cwd=str(root / "CEI"),
            encoding="utf-8",
            errors="replace",
            env=env,
        )
    except Exception as exc:
        info["success"] = False
        info["reason"] = f"subprocess 异常: {exc}"
        logger.warning("数据处理调用失败: %s", exc)
        _store_analysis_meta(result, info)
        return info

    payload: Dict[str, Any] = {}
    if result_json.is_file():
        try:
            payload = json.loads(result_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            payload = {"success": False, "message": f"result-json 解析失败: {exc}"}
    if not payload:
        stdout = (proc.stdout or "").strip()
        if stdout:
            try:
                start = stdout.rfind("{")
                if start >= 0:
                    payload = json.loads(stdout[start:])
            except json.JSONDecodeError:
                payload = {
                    "success": False,
                    "message": "无法解析无头输出",
                    "raw": stdout[-2000:],
                }
    info["returncode"] = proc.returncode
    info["payload"] = payload
    info["stderr"] = (proc.stderr or "")[-2000:]
    ok = bool(payload.get("success")) and proc.returncode == 0
    info["success"] = ok
    if not ok:
        info["reason"] = str(payload.get("message") or f"exit={proc.returncode}")
        logger.warning("数据处理未成功: %s", info["reason"])
    else:
        files = [Path(p) for p in (payload.get("output_files") or []) if p]
        if not files:
            files = [
                p
                for p in out_dir.rglob("*")
                if p.is_file() and p.name != "headless_result.json"
            ]
        _append_report_files(result, files)
        info["output_files"] = [str(p) for p in files]
        logger.info(
            "数据处理完成 pack=%s test=%s files=%s",
            target["standard_pack"],
            target["test_code"],
            len(files),
        )
    _store_analysis_meta(result, info)
    return info


def _store_analysis_meta(result: Dict[str, Any], info: Dict[str, Any]) -> None:
    summary = result.get("result_summary")
    if not isinstance(summary, dict):
        summary = {}
        result["result_summary"] = summary
    # 去掉过大的 cmd/raw
    slim = {
        k: v
        for k, v in info.items()
        if k not in ("cmd", "stderr") or (k == "stderr" and v)
    }
    if "cmd" in info:
        slim["cmd"] = [str(x) for x in info["cmd"][:12]]
    summary["data_analysis"] = slim
