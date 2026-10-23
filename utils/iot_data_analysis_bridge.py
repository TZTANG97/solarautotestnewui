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
    """从 job.params / widgets（含 params.widgets）抽额定参数 + 南德 Word 元数据。"""
    out: Dict[str, Any] = {}
    params = _job_params(job)
    widgets = _job_widgets(job)
    nested = params.get("analysisParams") or params.get("analysis_params") or {}
    if isinstance(nested, dict):
        out.update(nested)
    for key in (
        "Pn",
        "Un",
        "In",
        "SeMax",
        "PeMax",
        "Srated",
        "reconnect_time",
        "rated_power",
        # 南德总体报告页眉页脚
        "project_no",
        "ProjectNo",
        "model_no",
        "ModelNo",
        "model",
        "sample_no",
        "SampleNo",
        "tested_by",
        "Tester",
        "test_date",
        "TestDate",
    ):
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
        "analysis_Model": "model_no",
        "analysis_ProjectNo": "project_no",
        "analysis_SampleNo": "sample_no",
        "analysis_Tester": "tested_by",
        "analysis_TestDate": "test_date",
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
    # 标题里偶有型号线索时作兜底（不覆盖已填）
    title = str(job.get("title") or "").strip()
    if title and not out.get("project_no") and not out.get("ProjectNo"):
        out["project_no"] = title[:80]
    # 数值化（跳过元数据字符串）
    skip_num = {
        "project_no",
        "ProjectNo",
        "model_no",
        "ModelNo",
        "model",
        "sample_no",
        "SampleNo",
        "tested_by",
        "Tester",
        "test_date",
        "TestDate",
    }
    for k, v in list(out.items()):
        if k in skip_num:
            continue
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


def _parse_trailing_json(text: str) -> Dict[str, Any]:
    """从混有日志的 stdout 中提取最后一段完整 JSON 对象。"""
    raw = (text or "").strip()
    if not raw:
        return {}
    # 优先：最后一个以 { 开头的多行块（避免 rfind 命中内部 {}）
    starts = [i for i, ch in enumerate(raw) if ch == "{"]
    for start in reversed(starts):
        chunk = raw[start:]
        try:
            obj = json.loads(chunk)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            return obj
    return {}


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
        info["reason"] = f"testType={tt or '(空)'} 不在结案自动处理列表"
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
            f"pack={target['standard_pack']} 不在自动处理包 "
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
    summary0 = (
        result.get("result_summary")
        if isinstance(result.get("result_summary"), dict)
        else {}
    )
    is_sim = bool(summary0.get("sim_bench") or summary0.get("dry_run"))
    defaults_applied: List[str] = []

    def _ensure_param(name: str, default: Any, *, reason: str) -> bool:
        if params.get(name) not in (None, ""):
            return True
        if is_sim:
            params[name] = default
            defaults_applied.append(f"{name}={default}")
            return True
        info["reason"] = reason
        logger.warning("结案分析跳过: %s", info["reason"])
        _store_analysis_meta(result, info)
        return False

    # 巴西 Ordinance：多数条款要 Pn；直流/谐波/闪变/重连/电压适应另要 Un
    if target["standard_pack"] == "BRAZIL_140":
        br_need_pn = target["test_code"] in {
            "5.4.2",
            "5.9",
            "5.10",
            "5.4.11",
            "5.4.12",
            "5.4.13",
            "5.4.14",
            "5.4.15",
            "5.4.16",
            "5.4.18",
            "5.4.19",
            "5.4.20",
            "5.4.21",
            "5.4.22",
            "5.4.23",
            "5.4.25",
            "5.4.26",
            "5.24",
        }
        br_need_un = target["test_code"] in {
            "5.9",
            "5.10",
            "5.4.14",
            "5.4.16",
            "5.4.21",
            "5.4.22",
        }
        if br_need_pn and not _ensure_param(
            "Pn", 10000, reason=f"巴西 {target['test_code']} 缺少 Pn（analysis_Pn）"
        ):
            return info
        if br_need_un and not _ensure_param(
            "Un", 230, reason=f"巴西 {target['test_code']} 缺少 Un（analysis_Un）"
        ):
            return info
        if target["test_code"] == "5.4.2" and not params.get("SeMax"):
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
        if need_pn and not _ensure_param(
            "Pn", 10000, reason=f"南德 {target['test_code']} 缺少 Pn（analysis_Pn）"
        ):
            return info
        if need_un and not _ensure_param(
            "Un", 230, reason=f"南德 {target['test_code']} 缺少 Un（analysis_Un / 交流电压）"
        ):
            return info
        # 南德处理器普遍按 kW 读 Pn：网页填 10000(W) 时自动换算
        if need_pn and params.get("Pn") is not None:
            try:
                pn_v = float(params["Pn"])
                if pn_v >= 200:
                    params["Pn"] = pn_v / 1000.0
            except (TypeError, ValueError):
                pass
    # 北德 / CEI 0-16（图喆麦田报告）
    if target["standard_pack"] == "CEI_Nbis_BeiDe":
        code = target["test_code"]
        need_in = code in {"3.1"}
        need_pn = code in {
            "3.2",
            "3.3",
            "4",
            "5",
            "6.1",
            "6.4",
            "6.5",
            "6.7",
            "6.8",
            "7.1",
            "8.1",
            "A.4.9",
            "A.4.3.4",
        }
        need_un = code in {"3.2", "4", "5", "6.5", "6.7", "6.8", "7.1", "8.1"}
        if need_in and not _ensure_param(
            "In", 100, reason=f"北德 CEI0-16 {code} 缺少 In（analysis_In）"
        ):
            return info
        if need_pn and not _ensure_param(
            "Pn", 100000, reason=f"北德 CEI0-16 {code} 缺少 Pn（analysis_Pn）"
        ):
            return info
        if need_un and not _ensure_param(
            "Un", 230, reason=f"北德 CEI0-16 {code} 缺少 Un（analysis_Un）"
        ):
            return info
        # 北德部分条款 Pn 按 W；若网页填 kW 小数则保持，填 100000(W) 不换算
        # （与南德 kW 习惯不同，避免误除 1000）
    if defaults_applied:
        info["defaults_applied"] = defaults_applied
        logger.info("分析使用默认额定参数: %s", ",".join(defaults_applied))
    # 把 testType 写入 summary，便于选 CSV 时不要误偏 overload
    summary = result.get("result_summary")
    if not isinstance(summary, dict):
        summary = {}
        result["result_summary"] = summary
    summary.setdefault("testType", tt)

    out_dir = (
        Path(repo_root).resolve()
        / "command_save_files"
        / "analysis_reports"
        / f"job_{job.get('id') or job.get('jobId') or 'x'}_{int(time.time())}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    # subprocess cwd 在分析项目 CEI/ 下，必须用绝对路径，否则报告落到错误目录
    input_dir = Path(input_dir).resolve()
    out_dir = out_dir.resolve()

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
            # 日志后可能跟一段 JSON；勿用 rfind('{')（会命中 calculated_values: {}）
            payload = _parse_trailing_json(stdout)
            if not payload:
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
