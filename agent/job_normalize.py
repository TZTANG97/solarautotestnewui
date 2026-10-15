# -*- coding: utf-8 -*-
"""startexper / claim 任务载荷归一化：保证 id=solar_jobs 主键。"""
from __future__ import annotations

import json
from typing import Any, Dict


def normalize_startexper_job(raw: Dict[str, Any] | None) -> Dict[str, Any]:
    """
    对齐 IOT agent_job_envelope：
    - id：solar_jobs 主键（进度/结案 HTTPS 必用）
    - experid：可为 experiments.id（与 id 不同）
    - commands.command 内嵌 JSON 可还原 testType/title/params
    """
    job: Dict[str, Any] = dict(raw or {})
    cmds = job.get("commands") if isinstance(job.get("commands"), dict) else None
    nested: Dict[str, Any] = {}
    if isinstance(cmds, dict):
        raw_cmd = cmds.get("command")
        if isinstance(raw_cmd, str) and raw_cmd.strip().startswith("{"):
            try:
                parsed = json.loads(raw_cmd)
                if isinstance(parsed, dict):
                    nested = parsed
            except json.JSONDecodeError:
                nested = {}
        elif isinstance(raw_cmd, dict):
            nested = raw_cmd

    if nested:
        if not job.get("testType") and nested.get("testType"):
            job["testType"] = nested.get("testType")
        if not job.get("title") and nested.get("title"):
            job["title"] = nested.get("title")
        if not job.get("params") and isinstance(nested.get("params"), dict):
            job["params"] = nested.get("params")

    params = job.get("params") if isinstance(job.get("params"), dict) else {}
    exper_ref = ""
    for k in ("experId", "experid", "exper_id"):
        if params.get(k) is not None and str(params.get(k)).strip() != "":
            exper_ref = str(params.get(k)).strip()
            break

    job_id = job.get("id")
    if job_id is None or str(job_id).strip() == "":
        # 禁止在已有 experiments.id 时把 experid 误当 solar_jobs.id
        if not exper_ref:
            try:
                job_id = int(job.get("experid") or 0)
            except (TypeError, ValueError):
                job_id = 0
        else:
            job_id = 0
    try:
        job["id"] = int(job_id)
    except (TypeError, ValueError):
        job["id"] = 0

    if not job.get("experid") and exper_ref:
        job["experid"] = exper_ref
    elif not job.get("experid") and job["id"]:
        job["experid"] = str(job["id"])

    return job
