# -*- coding: utf-8 -*-
"""从 IOT 命令库拉取 WT 采集 token，覆盖 wt_scpi_items（失败则保持代码表）。"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from utils.wt_scpi_items import WT_CATALOG_MODELS, clear_catalog_token_overrides, set_catalog_token_overrides
from utils.wt_setup_catalog_overrides import set_rate_scpi_prefix

logger = logging.getLogger(__name__)


def apply_wt_measure_catalog_from_client(client: Any, *, models: Optional[tuple] = None) -> Dict[str, int]:
    """
    对每个型号 GET agent/wt-measure-commands，写入 set_catalog_token_overrides。
    返回 {model: token_count}；全失败时不 clear，保留已有覆盖。
    """
    want = tuple(models or WT_CATALOG_MODELS)
    loaded: Dict[str, int] = {}
    any_ok = False
    for model in want:
        try:
            res = client.get_wt_measure_commands(model)
            data = (res or {}).get("data") if isinstance(res, dict) else None
            if not isinstance(data, dict):
                # 兼容直接返回 data
                data = res if isinstance(res, dict) else {}
            tokens = data.get("tokens") if isinstance(data, dict) else None
            if not isinstance(tokens, dict):
                continue
            if tokens:
                set_catalog_token_overrides(model, tokens)
                rate_tok = tokens.get("comboBox_ReplaceRate")
                if rate_tok is not None and str(rate_tok).strip():
                    set_rate_scpi_prefix(str(rate_tok).strip())
                loaded[model] = len(tokens)
                any_ok = True
            else:
                # 空字典：该型号尚未灌库，清掉旧覆盖以免脏数据
                set_catalog_token_overrides(model, None)
                loaded[model] = 0
        except Exception:
            logger.debug("拉取 WT 采集命令库失败 model=%s", model, exc_info=True)
    if not any_ok and not loaded:
        logger.info("WT 采集命令库未拉取到数据，继续使用本地 wt_scpi_items")
    else:
        logger.info("WT 采集命令库已覆盖 models=%s", loaded)
    return loaded


def reset_wt_measure_catalog_overrides() -> None:
    clear_catalog_token_overrides()
