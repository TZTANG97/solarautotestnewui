# -*- coding: utf-8 -*-
"""实时测量页的纯数据：解析一轮读数、滚动缓存、按已连接仪器读一帧。

不写文件。试验正在录波时只看已有最新行，不再改 NUMERIC 通道。
"""
from __future__ import annotations

from typing import Dict, List, Mapping, MutableMapping, Optional, Sequence, Tuple


def parse_numeric_list(raw: str) -> List[float]:
    """把 VALUE? 回包收成浮点。开头的绝对时间（非数字）丢掉。"""
    text = str(raw or "").strip()
    if not text:
        return []
    if text.startswith(":"):
        parts = text.split(None, 1)
        text = parts[1] if len(parts) > 1 else ""
    out: List[float] = []
    skipped_time = False
    for piece in text.split(","):
        token = piece.strip().strip('"').strip("'")
        if not token:
            continue
        try:
            out.append(float(token))
        except ValueError:
            if not skipped_time and not out:
                skipped_time = True
                continue
            out.append(float("nan"))
    return out


def zip_items(items: Sequence[str], values: Sequence[float]) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for index, name in enumerate(items):
        if index >= len(values):
            break
        number = values[index]
        if number != number:
            continue
        key = str(name).strip()
        if key:
            out[key] = float(number)
    return out


def append_history(
    history: MutableMapping[str, List[float]],
    sample: Mapping[str, float],
    *,
    limit: int = 180,
) -> None:
    """勾选中的通道各追加一个点；本轮没有的通道补一个空位，曲线对齐。"""
    names = list(history.keys())
    for name in sample:
        if name not in history:
            history[name] = [float("nan")] * (len(history[names[0]]) if names else 0)
            names.append(name)
    if not names:
        return
    for name in list(history.keys()):
        history[name].append(float(sample[name]) if name in sample else float("nan"))
        if len(history[name]) > limit:
            del history[name][: len(history[name]) - limit]


def split_item_names(raw: str) -> List[str]:
    text = str(raw or "").strip()
    if text.startswith(":"):
        parts = text.split(None, 1)
        text = parts[1] if len(parts) > 1 else text
    names = []
    for piece in text.replace(";", ",").split(","):
        name = piece.strip().strip('"').strip("'")
        if name and not name.endswith("?"):
            names.append(name)
    return names


_wt_prepared: Dict[int, Tuple[str, ...]] = {}
_last_wt_model = "3000"

_WT_STYLE = {
    "3000": "Thai_WT3000E_Config",
    "1800": "Thai_WT1800_Config",
    "1806": "Thai_WT1806E_Config",
    "5000": "Thai_WT5000_Config",
}


def wt_style_for_model(model: str) -> str:
    return _WT_STYLE.get(str(model or "").strip(), _WT_STYLE["3000"])


def detect_connected_wt_model() -> str:
    """3000 / 1800 / 1806 / 5000。录波中不再问 *IDN?，沿用上次识别。"""
    global _last_wt_model
    from utils.wt_scale_probe import detect_model_from_idn
    from utils.wt_scpi_session import ensure_collector

    collector = ensure_collector()
    if collector is None:
        return _last_wt_model
    if collector.is_gather.is_set():
        inferred = _model_from_open_items(collector.latest_item_map())
        if inferred == "3000" or (inferred and _last_wt_model == "3000"):
            _last_wt_model = inferred
        return _last_wt_model
    raw = collector._query("*IDN?")
    model = detect_model_from_idn(str(raw or ""))
    if model in _WT_STYLE:
        _last_wt_model = model
    return _last_wt_model


def _model_from_open_items(measures: Mapping[str, float]) -> str:
    """录波中的列名：带 TOTAL 或 U, / I, 是 3000；URMS 这一族是 1800/1806/5000。"""
    for key in measures:
        upper = str(key).upper()
        if ",TOTAL" in upper or upper.startswith("U,") or upper.startswith("I,"):
            return "3000"
        if upper.startswith(("URMS", "IRMS", "UK,", "UFND")):
            return "1800"
    return ""


def items_for_wt_checks(config: Mapping, model: str) -> List[str]:
    from utils.wt_scpi_items import items_from_wt_config

    payload = dict(config)
    payload["Style"] = wt_style_for_model(model)
    return items_from_wt_config(payload)


def read_wt_checks(config: Mapping) -> Tuple[Dict[str, float], str]:
    model = detect_connected_wt_model()
    items = items_for_wt_checks(config, model)
    if not items:
        return {}, "先勾选测量项"
    sample, message = read_snapshot("wt", items)
    return sample, f"WT{model} · {message}"


def read_snapshot(kind: str, items: Sequence[str]) -> Tuple[Dict[str, float], str]:
    """读一帧。返回 (通道->值, 状态说明)。"""
    from app.context import get_app_context

    ctx = get_app_context()
    if kind == "dew":
        return _read_dewetron(ctx, items)
    return _read_wt(ctx, items)


def _read_wt(ctx, items: Sequence[str]) -> Tuple[Dict[str, float], str]:
    from utils.wt_scpi_session import ensure_collector

    collector = ensure_collector(getattr(ctx, "logger", None))
    if collector is None:
        return {}, "WT 未连接"
    if collector.is_gather.is_set():
        current = {
            key: value
            for key, value in collector.latest_item_map().items()
            if key in {str(item).strip().upper() for item in items}
        }
        return current, "试验正在录波，只显示已采到的数"
    wanted = [str(item).strip() for item in items if str(item).strip()]
    if not wanted:
        return {}, "先勾选测量项"
    key = tuple(wanted)
    note = ""
    if _wt_prepared.get(id(collector)) != key:
        ok, _accepted, warnings = collector.prepare(
            items=wanted, rate_text="500ms", save_path=""
        )
        if not ok:
            _wt_prepared.pop(id(collector), None)
            return {}, collector.last_error() or "WT 测量项配置失败"
        _wt_prepared[id(collector)] = key
        if warnings:
            note = "；".join(str(item) for item in warnings[:2])
    if not collector.sample_once():
        return {}, collector.last_error() or note or "WT 没有读到数"
    row = collector.latest_item_map()
    return row, note or "WT 实时"


def _read_dewetron(ctx, items: Sequence[str]) -> Tuple[Dict[str, float], str]:
    collector = getattr(ctx, "dewetron_collector", None)
    if collector is not None and collector.is_gather.is_set():
        return {}, "德威创正在录波，实时页暂停读取，避免和录波抢数据"
    ctrl = getattr(ctx, "dewetron_controller", None)
    if ctrl is None or not getattr(ctrl, "connected", False):
        return {}, "德威创未连接"
    wanted = [str(item).strip() for item in items if str(item).strip()]
    if not wanted:
        return {}, "先勾选测量项"
    query = getattr(ctrl, "query", None) or getattr(ctrl, "query_command", None)
    if query is None:
        return {}, "德威创没有查询接口"
    query(":NUM:NORM:ITEMs " + ",".join(wanted), timeout_ms=3000)
    raw = query(":NUM:NORM:VALue?", timeout_ms=3000)
    values = parse_numeric_list(str(raw or ""))
    if len(values) == len(wanted) + 1:
        values = values[1:]
    if not values:
        return {}, "德威创没有读到数"
    return zip_items(wanted, values), "德威创实时"


def read_dewetron_item_names() -> Tuple[List[str], str]:
    from app.context import get_app_context

    ctx = get_app_context()
    ctrl = getattr(ctx, "dewetron_controller", None)
    if ctrl is None or not getattr(ctrl, "connected", False):
        return [], "德威创未连接"
    query = getattr(ctrl, "query", None) or getattr(ctrl, "query_command", None)
    if query is None:
        return [], "德威创没有查询接口"
    raw = query(":NUM:NORM:ITEMs?", timeout_ms=3000)
    names = split_item_names(str(raw or ""))
    if not names:
        return [], "设备上还没有测量项，先在试验里点测试生效"
    return names, "已读取当前测量项"
