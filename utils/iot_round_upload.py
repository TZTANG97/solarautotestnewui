# -*- coding: utf-8 -*-
"""分开录：每轮录波结束后立刻把 CSV 上传到当前 IOT 任务（不必等整单结束）。"""
from __future__ import annotations

import logging
import os
import re
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# 分开录在本轮结束时上传。超过这段时间还没改过的 CSV 是目录里的旧文件，不能传给本单。
_ROUND_CSV_MAX_AGE_S = 20 * 60
_STAMPED_TAIL_RE = re.compile(r"_(\d{6})$", re.IGNORECASE)


def _resolve_job_id() -> Optional[int]:
    try:
        from utils.iot_local_run import current_local_job_id

        jid = current_local_job_id()
        if jid:
            return int(jid)
    except Exception:
        pass
    try:
        import json

        root = Path(__file__).resolve().parent.parent
        raw = json.loads((root / "status.json").read_text(encoding="utf-8"))
        proj = raw.get("project") if isinstance(raw, dict) else None
        if isinstance(proj, dict):
            jid = int(proj.get("jobId") or proj.get("job_id") or 0)
            if jid > 0:
                return jid
    except Exception:
        pass
    try:
        import SCPITestWave as sw

        svc = getattr(sw, "_iot_ui_handoff_svc", None)
        for src in (
            getattr(svc, "_awaiting", None),
            getattr(svc, "_job_ctx", None),
        ):
            if isinstance(src, dict):
                jid = int(src.get("job_id") or 0)
                if jid > 0:
                    return jid
    except Exception:
        pass
    return None


def _save_path_from_config(config_dict: Optional[Dict[str, Any]]) -> str:
    if not isinstance(config_dict, dict):
        return ""
    return str(
        config_dict.get("textEdit_SavePath")
        or config_dict.get("SavePath")
        or ""
    ).strip()


def _file_age_s(path: str) -> float:
    try:
        return max(0.0, time.time() - os.path.getmtime(path))
    except OSError:
        return 1e9


def _newest_stamped_csv(stem: str, dirs) -> Optional[str]:
    """WT 常把 Pdisp_BR 存成 Pdisp_BR_161912.csv。只认多出来的这一段时刻。"""
    prefix = stem.lower() + "_"
    best = None
    best_mtime = -1.0
    for folder in dirs:
        if not folder or not os.path.isdir(folder):
            continue
        try:
            names = os.listdir(folder)
        except OSError:
            continue
        for name in names:
            if not name.lower().endswith(".csv"):
                continue
            body = name[:-4]
            if not body.lower().startswith(prefix):
                continue
            if _STAMPED_TAIL_RE.fullmatch(body[len(stem) :]) is None:
                continue
            fp = os.path.join(folder, name)
            try:
                if not os.path.isfile(fp) or os.path.getsize(fp) <= 0:
                    continue
                mtime = os.path.getmtime(fp)
            except OSError:
                continue
            if mtime >= best_mtime:
                best = fp
                best_mtime = mtime
    return best


def find_round_csv(
    file_label: str,
    *,
    config_dict: Optional[Dict[str, Any]] = None,
    wait_s: float = 3.0,
) -> Optional[str]:
    """按轮次文件名在 SavePath / 工作目录查找刚落盘的 CSV。

    同名旧文件（Pdisp_BR.csv）留在目录里时，改传本轮带时刻的那一份。
    两份都不是刚写的，就返回空，避免把上一次试验传上去。
    """
    label = (file_label or "").strip()
    if not label:
        return None
    try:
        from utils.wt_csv_merge import candidate_save_dirs, find_wt_csv
    except Exception:
        return None
    dirs = candidate_save_dirs(
        _save_path_from_config(config_dict),
        extra=[str(Path.cwd()), str(Path(__file__).resolve().parent.parent)],
    )
    exact = find_wt_csv(label, dirs, wait_s=wait_s)
    stem = label[:-4] if label.lower().endswith(".csv") else label
    stamped = _newest_stamped_csv(stem, dirs)
    exact_fresh = bool(exact) and _file_age_s(exact) <= _ROUND_CSV_MAX_AGE_S
    stamped_fresh = bool(stamped) and _file_age_s(stamped) <= _ROUND_CSV_MAX_AGE_S
    if stamped_fresh and (
        not exact_fresh or _file_age_s(stamped) <= _file_age_s(exact)
    ):
        return stamped
    if exact_fresh:
        return exact
    return None


def upload_round_csv_now(
    *,
    job_id: int,
    csv_path: str,
    round_index: int = 0,
    file_label: str = "",
) -> bool:
    """同步上传一个 CSV；成功返回 True。"""
    path = Path(str(csv_path or ""))
    if job_id <= 0 or not path.is_file() or path.stat().st_size <= 0:
        return False
    try:
        from agent.client import IotSolarClient
        from agent.config import load_config

        cfg = load_config()
        if not cfg.agent_token or str(cfg.agent_token).startswith("请填写"):
            logger.info("[iot_round_upload] 无 agent_token，跳过轮次上传")
            return False
        pythonid = ""
        try:
            import json

            raw_path = Path(__file__).resolve().parent.parent / "config" / "solar_agent.json"
            if raw_path.is_file():
                raw = json.loads(raw_path.read_text(encoding="utf-8"))
                pythonid = str(raw.get("pythonid") or raw.get("pythonId") or "").strip()
        except Exception:
            pythonid = ""
        client = IotSolarClient(cfg.iot_base, cfg.agent_token, pythonid=pythonid)
        name = path.name
        if file_label and not name.lower().startswith(str(file_label).lower()[:8]):
            # 保留原名；仅日志提示轮次
            pass
        client.upload_report(int(job_id), str(path), filename=name)
        logger.info(
            "[iot_round_upload] 已上传轮次#%s job=%s file=%s",
            int(round_index) + 1,
            job_id,
            name,
        )
        return True
    except Exception:
        logger.info(
            "[iot_round_upload] 上传失败 job=%s path=%s",
            job_id,
            path,
            exc_info=True,
        )
        return False


def schedule_round_csv_upload(
    *,
    round_index: int,
    file_label: str = "",
    config_dict: Optional[Dict[str, Any]] = None,
    job_id: Optional[int] = None,
    csv_path: str = "",
    wait_s: float = 3.0,
) -> None:
    """后台上传本轮 CSV。已给出路径时直接传，不再等整单结案。"""

    def _worker() -> None:
        jid = int(job_id or 0) or (_resolve_job_id() or 0)
        if jid <= 0:
            logger.info("[iot_round_upload] 无 jobId，跳过轮次#%s", int(round_index) + 1)
            return
        label = (file_label or "").strip()
        known = str(csv_path or "").strip()
        if known and Path(known).is_file() and Path(known).stat().st_size > 0:
            csv_path_hit = known if _file_age_s(known) <= _ROUND_CSV_MAX_AGE_S else None
        else:
            csv_path_hit = find_round_csv(label, config_dict=config_dict, wait_s=wait_s) if label else None
        if not csv_path_hit:
            logger.info(
                "[iot_round_upload] 未找到轮次#%s 文件 label=%r",
                int(round_index) + 1,
                label,
            )
            return
        ok = upload_round_csv_now(
            job_id=jid,
            csv_path=csv_path_hit,
            round_index=int(round_index),
            file_label=label,
        )
        if ok:
            try:
                print(
                    f"[IOT] 分开录第{int(round_index)+1}轮 CSV 已上传: {os.path.basename(csv_path_hit)}",
                    flush=True,
                )
            except Exception:
                pass

    threading.Thread(
        target=_worker,
        daemon=True,
        name=f"iot-round-upload-{int(round_index)+1}",
    ).start()
