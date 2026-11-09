# -*- coding: utf-8 -*-
"""从 IOT 命令库拉取 DC 源 token（按品牌），覆盖 dc_mode_preamble 等。"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Mapping, Optional

from utils.guochan_sim_matrix import DC_MODE_PREAMBLE

logger = logging.getLogger(__name__)

DC_CATALOG_BRANDS = ("Chroma", "Itech", "Bluesight", "Keysight")

_overrides_by_brand: Dict[str, Dict[str, str]] = {}

_BRAND_ALIASES = {
    "chroma": "Chroma",
    "itech": "Itech",
    "bluesight": "Bluesight",
    "keysight": "Keysight",
}


def _normalize_brand(brand: str) -> str:
    raw = str(brand or "").strip()
    if not raw:
        return "Chroma"
    return _BRAND_ALIASES.get(raw.lower(), raw)


def set_dc_source_overrides(brand: str, mapping: Optional[Mapping[str, str]]) -> None:
    b = _normalize_brand(brand)
    if mapping is None:
        _overrides_by_brand.pop(b, None)
        return
    _overrides_by_brand[b] = {
        str(k): str(v).strip()
        for k, v in mapping.items()
        if str(k).strip() and str(v).strip()
    }


def clear_dc_source_overrides() -> None:
    _overrides_by_brand.clear()


def get_dc_mode_preamble(brand: str) -> List[str]:
    """优先命令库 dc_mode_preamble（多行 split），否则 guochan_sim_matrix。"""
    b = _normalize_brand(brand)
    raw = (_overrides_by_brand.get(b) or {}).get("dc_mode_preamble")
    if raw is not None and str(raw).strip():
        return [ln.strip() for ln in str(raw).splitlines() if ln.strip()]
    fallback = DC_MODE_PREAMBLE.get(b)
    if fallback is not None:
        return list(fallback)
    return list(DC_MODE_PREAMBLE.get("Chroma", []))


def _tokens_from_response(res: Any) -> Optional[Dict[str, Any]]:
    data = (res or {}).get("data") if isinstance(res, dict) else None
    if not isinstance(data, dict):
        data = res if isinstance(res, dict) else {}
    tokens = data.get("tokens") if isinstance(data, dict) else None
    return tokens if isinstance(tokens, dict) else None


def apply_dc_source_catalog_from_client(client: Any, firm: str) -> int:
    brand = _normalize_brand(firm)
    try:
        res = client.get_dc_source_commands(brand)
    except Exception:
        logger.debug("拉取 DC 命令库失败 firm=%s", brand, exc_info=True)
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
    _overrides_by_brand[brand] = mapped
    logger.info("DC 命令库已覆盖 firm=%s tokens=%s", brand, len(mapped))
    return len(mapped)
