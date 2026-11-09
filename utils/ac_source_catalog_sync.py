# -*- coding: utf-8 -*-
"""从 IOT 命令库拉取 AC 源 token，按协议族覆盖 VOLT 等 SCPI 动词。"""
from __future__ import annotations

import logging
from typing import Any, Dict, Mapping, Optional

logger = logging.getLogger(__name__)

# family -> {blockly_name: com_content}
_overrides_by_family: Dict[str, Dict[str, str]] = {}


def set_ac_source_overrides(
    mapping: Optional[Mapping[str, str]], *, family: str = "AC_GENERIC"
) -> None:
    fam = str(family or "AC_GENERIC").strip() or "AC_GENERIC"
    if mapping is None:
        _overrides_by_family.pop(fam, None)
        return
    _overrides_by_family[fam] = {
        str(k): str(v).strip()
        for k, v in mapping.items()
        if str(k).strip() and str(v).strip()
    }


def get_ac_scpi_verb(key: str, default: str, *, family: Optional[str] = None) -> str:
    """
    取 SCPI 动词。family 缺省时：若 default 含 VOLT:AC 或调用方暗示 61800，优先 61800 表。
    """
    k = str(key or "").strip()
    if not k:
        return default
    fam = str(family or "").strip()
    if not fam:
        # 启发式：默认值已是 VOLT:AC 则查 61800
        if "VOLT:AC" in str(default).upper() or str(default).upper() == "VOLT:AC":
            fam = "61800"
        else:
            fam = "AC_GENERIC"
    ov = (_overrides_by_family.get(fam) or {}).get(k)
    if ov:
        return ov
    # 回退另一族
    for alt in ("61800", "AC_GENERIC"):
        if alt == fam:
            continue
        ov2 = (_overrides_by_family.get(alt) or {}).get(k)
        if ov2 and fam == "61800":
            # 61800 缺键时不回退到 GENERIC 的 VOLT（避免把 VOLT:AC 冲掉）
            if k == "VOLT" and ov2 == "VOLT":
                continue
        if ov2:
            return ov2
    return default


def clear_ac_source_overrides() -> None:
    _overrides_by_family.clear()


def get_ac_source_overrides(family: Optional[str] = None) -> Dict[str, str]:
    if family:
        return dict(_overrides_by_family.get(str(family), {}) or {})
    merged: Dict[str, str] = {}
    for d in _overrides_by_family.values():
        merged.update(d)
    return merged


def _tokens_from_response(res: Any) -> Optional[Dict[str, Any]]:
    data = (res or {}).get("data") if isinstance(res, dict) else None
    if not isinstance(data, dict):
        data = res if isinstance(res, dict) else {}
    tokens = data.get("tokens") if isinstance(data, dict) else None
    return tokens if isinstance(tokens, dict) else None


def apply_ac_source_catalog_from_client(
    client: Any,
    *,
    family: str = "AC_GENERIC",
) -> int:
    """GET ac-source-commands，写入对应 family 覆盖表。"""
    fam = str(family or "AC_GENERIC").strip() or "AC_GENERIC"
    try:
        res = client.get_ac_source_commands(fam)
    except Exception:
        logger.debug("拉取 AC 命令库失败 family=%s", fam, exc_info=True)
        return 0
    tokens = _tokens_from_response(res)
    if not tokens:
        return 0
    mapped = {
        str(k): str(v).strip()
        for k, v in tokens.items()
        if str(k).strip() and str(v).strip()
    }
    if not mapped:
        return 0
    _overrides_by_family[fam] = mapped
    logger.info("AC 命令库已覆盖 family=%s tokens=%s", fam, len(mapped))
    return len(mapped)
