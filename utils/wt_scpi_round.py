# -*- coding: utf-8 -*-
"""WT SCPI 一轮采集：按文件名落 CSV，并带回路径供立刻上传。"""
from __future__ import annotations

import re
from typing import Any, Callable, Mapping, Optional


def ensure_scpi_measure_ready(config: Optional[Mapping]) -> tuple[bool, str]:
    """SCPI 模式下补一次 prepare。未选 SCPI 时返回 (False, '')。"""
    from utils.wt_acquire_mode import is_scpi_mode
    from utils import wt_scpi_session

    cfg = dict(config) if isinstance(config, Mapping) else {}
    if not is_scpi_mode(cfg):
        return False, ""
    ok, err = wt_scpi_session.prepare_from_config(cfg)
    return bool(ok), str(err or "")


def file_names_from_config(config: Optional[Mapping]) -> list[str]:
    if not isinstance(config, Mapping):
        return []
    raw = str(config.get("textEdit_FileNameList") or config.get("FileNameList") or "")
    return [part.strip() for part in re.split(r"[,，]", raw) if part.strip()]


def run_scpi_measure_round(
    config: Optional[Mapping],
    *,
    file_index: int = 0,
    stop_event_check: Optional[Callable[[], bool]] = None,
    async_stop_check: Optional[Callable[[], bool]] = None,
    logger=None,
    notify: Optional[Callable[[str], None]] = None,
) -> dict[str, Any]:
    """跑一轮 SCPI 采集。返回 ok / csv_path / label / names / note / error。"""
    cfg = dict(config) if isinstance(config, Mapping) else {}
    names = file_names_from_config(cfg)
    idx = max(0, int(file_index or 0))
    label = names[idx] if idx < len(names) else (names[-1] if names else "")
    result: dict[str, Any] = {
        "ok": False,
        "csv_path": "",
        "label": label,
        "names": names,
        "note": "本轮完成",
        "error": "",
    }

    def _say(text: str) -> None:
        if notify is None:
            return
        try:
            notify(text)
        except Exception:
            pass

    try:
        from utils import wt_scpi_session
    except Exception as exc:
        result["error"] = f"SCPI session unavailable: {exc}"
        result["note"] = "未生成CSV"
        _say(f"[功率分析仪] SCPI 采集失败: {result['error']}")
        return result

    _say("[功率分析仪] SCPI 采集中…")
    ok = False
    try:
        ok = bool(
            wt_scpi_session.run_measure_blocking(
                cfg,
                file_index=idx,
                stop_event_check=stop_event_check,
                async_stop_check=async_stop_check,
                logger=logger,
            )
        )
    except Exception as exc:
        result["error"] = str(exc)
        result["note"] = "未生成CSV"
        _say(f"[功率分析仪] SCPI 采集失败: {exc}")
        return result

    csv_path = ""
    try:
        csv_path = str(wt_scpi_session.last_csv() or "")
    except Exception:
        csv_path = ""
    result["ok"] = bool(ok and csv_path)
    result["csv_path"] = csv_path
    if result["ok"]:
        result["note"] = "本轮完成"
        _say(f"[功率分析仪] SCPI 已导出: {csv_path}")
        return result

    err = ""
    try:
        err = str(wt_scpi_session.last_error() or "")
    except Exception:
        err = ""
    result["error"] = err or "采到 0 行，未生成 CSV"
    result["note"] = "未生成CSV"
    _say(f"[功率分析仪] SCPI 未落盘: {result['error']}")
    return result
