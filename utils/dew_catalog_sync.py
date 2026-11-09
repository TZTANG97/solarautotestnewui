# -*- coding: utf-8 -*-
"""从 IOT 命令库拉取 DEWETRON 采集启停 SCPI。"""
from __future__ import annotations

import logging
from typing import Any, Dict, Mapping, Optional

logger = logging.getLogger(__name__)

_overrides: Dict[str, str] = {}

_DEW_KEY_ALIASES = {
    "start": "dew_acq_start",
    "stop": "dew_acq_stop",
    "dew_acq_start": "dew_acq_start",
    "dew_acq_stop": "dew_acq_stop",
}


def set_dew_overrides(mapping: Optional[Mapping[str, str]]) -> None:
    global _overrides
    if mapping is None:
        _overrides.clear()
        return
    _overrides = {
        str(k): str(v).strip()
        for k, v in mapping.items()
        if str(k).strip() and str(v).strip()
    }


def clear_dew_overrides() -> None:
    _overrides.clear()


def get_dew_acq_command(which: str, default: str) -> str:
    w = str(which or "").strip().lower()
    key = _DEW_KEY_ALIASES.get(w, str(which or "").strip())
    ov = _overrides.get(key)
    return ov if ov else default


def _tokens_from_response(res: Any) -> Optional[Dict[str, Any]]:
    data = (res or {}).get("data") if isinstance(res, dict) else None
    if not isinstance(data, dict):
        data = res if isinstance(res, dict) else {}
    tokens = data.get("tokens") if isinstance(data, dict) else None
    return tokens if isinstance(tokens, dict) else None


def apply_dew_catalog_from_client(client: Any) -> int:
    try:
        res = client.get_dew_commands()
    except Exception:
        logger.debug("拉取 DEW 命令库失败", exc_info=True)
        return 0
    tokens = _tokens_from_response(res)
    if not tokens:
        return 0
    set_dew_overrides(
        {
            str(k): str(v).strip()
            for k, v in tokens.items()
            if str(k).strip() and str(v).strip()
        }
    )
    count = len(_overrides)
    if count:
        logger.info("DEW 命令库已覆盖 tokens=%s", count)
    return count
