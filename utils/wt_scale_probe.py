# -*- coding: utf-8 -*-
"""连接页核对比例系数：下发 VT/CT 后试读 U/I/P/频率。

流程与 WT 上位机一致：交流源、直流源通电 → 看实测值 → 不合适就改系数再下发。
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from utils.wt_channel_scale import max_scale_element, scaling_commands


def detect_model_from_idn(idn: str) -> str:
    text = str(idn or "").upper()
    for tag in ("5000", "1806", "1800", "3000"):
        if tag in text:
            return tag
    return "3000"


def probe_items(model: str = "3000", element_count: int = 4) -> List[str]:
    """试读用的 NUMERIC 项。只取 U/I/P/频率，方便对照交流源设定。"""
    count = max(1, min(int(element_count or 1), 7))
    items: List[str] = []
    if model == "3000":
        for element in range(1, count + 1):
            items.extend(
                [
                    f"U,{element},TOTAL",
                    f"I,{element},TOTAL",
                    f"P,{element},TOTAL",
                    f"FU,{element}",
                ]
            )
        return items
    for element in range(1, count + 1):
        items.extend(
            [
                f"URMS,{element}",
                f"IRMS,{element}",
                f"P,{element}",
                f"FU,{element}",
            ]
        )
    return items


def parse_probe_values(items: Sequence[str], values: Sequence[float]) -> Dict[str, float]:
    """把 VALUE? 回读收成 U1/I1/P1/F1…"""
    out: Dict[str, float] = {}
    for index, token in enumerate(items):
        if index >= len(values):
            break
        number = values[index]
        if number != number:  # NaN
            continue
        parts = [part.strip().upper() for part in str(token).split(",") if part.strip()]
        if len(parts) < 2:
            continue
        func, element = parts[0], parts[1]
        if not element.isdigit():
            continue
        key = {
            "U": f"U{element}",
            "URMS": f"U{element}",
            "I": f"I{element}",
            "IRMS": f"I{element}",
            "P": f"P{element}",
            "FU": f"F{element}",
        }.get(func)
        if key:
            out[key] = float(number)
    return out


def format_probe_text(measures: Dict[str, float], element_count: int = 4) -> str:
    lines = []
    for element in range(1, max(1, min(int(element_count or 1), 7)) + 1):
        u = measures.get(f"U{element}")
        i = measures.get(f"I{element}")
        p = measures.get(f"P{element}")
        f = measures.get(f"F{element}")
        if u is None and i is None and p is None and f is None:
            continue
        lines.append(
            f"E{element}  U={_fmt(u)} V   I={_fmt(i)} A   P={_fmt(p)} W   f={_fmt(f)} Hz"
        )
    return "\n".join(lines) if lines else "暂无读数"


def _fmt(value: Optional[float]) -> str:
    if value is None:
        return "—"
    if abs(value) >= 1000:
        return f"{value:.1f}"
    if abs(value) >= 10:
        return f"{value:.2f}"
    return f"{value:.4f}"


def _parse_csv_floats(raw: str) -> List[float]:
    out: List[float] = []
    for part in str(raw or "").split(","):
        text = part.strip()
        if not text or text.upper() in ("NAN", "INF", "+INF", "-INF"):
            out.append(float("nan"))
            continue
        try:
            out.append(float(text))
        except ValueError:
            out.append(float("nan"))
    return out


def _item_accepted(token: str, reply: str) -> bool:
    try:
        from utils.wt_scpi_items import item_echo_matches

        return item_echo_matches(token, reply)
    except Exception:
        wanted = str(token or "").upper().replace(" ", "")
        payload = str(reply or "").upper().replace(" ", "")
        return wanted and wanted in payload


_STYLE_BY_MODEL = {
    "3000": "Thai_WT3000E_Config",
    "1800": "Thai_WT1800_Config",
    "1806": "Thai_WT1806E_Config",
    "5000": "Thai_WT5000_Config",
}


def resolve_connected_model(ctrl: Any, model: str = "") -> str:
    if model:
        return model
    if ctrl is None or not getattr(ctrl, "connected", False):
        return "3000"
    try:
        return detect_model_from_idn(ctrl.query("*IDN?"))
    except Exception:
        return "3000"


def apply_scales(
    ctrl: Any,
    mapping: Optional[Mapping] = None,
    *,
    style: str = "",
    model: str = "",
) -> Tuple[bool, str, List[str]]:
    """把连接页上的 VT/CT 立刻写到仪器。元素路数按 *IDN? 机型限制。"""
    if ctrl is None or not getattr(ctrl, "connected", False):
        return False, "功率分析仪未连接", []
    detected = resolve_connected_model(ctrl, model)
    style_text = style or _STYLE_BY_MODEL.get(detected, "Thai_WT3000E_Config")
    commands = scaling_commands(style_text, mapping or {})
    if not commands:
        return False, "没有可下发的比例系数", []
    written: List[str] = []
    for command in commands:
        try:
            ctrl.write(command)
            written.append(command)
        except Exception as exc:
            return False, f"下发失败 {command}: {exc}", written
    return True, f"已下发 {len(written)} 条比例系数命令 ({detected})", written


def prepare_probe(
    ctrl: Any,
    *,
    model: str = "",
    element_count: Optional[int] = None,
) -> Tuple[bool, str, List[str]]:
    """配置试读 NUMERIC 项。先 *IDN? 认型号，再写 ITEM。"""
    if ctrl is None or not getattr(ctrl, "connected", False):
        return False, "功率分析仪未连接", []
    detected = resolve_connected_model(ctrl, model)
    count = element_count or max_scale_element(_STYLE_BY_MODEL.get(detected, "Thai_WT3000E_Config"))
    items = probe_items(detected, count)
    try:
        ctrl.write(":NUMERIC:FORMAT ASCII")
        ctrl.write(f":NUMERIC:NORMAL:NUMBER {len(items)}")
    except Exception as exc:
        return False, f"准备试读失败: {exc}", []
    accepted: List[str] = []
    for index, token in enumerate(items, start=1):
        try:
            ctrl.write(f":NUMERIC:NORMAL:ITEM{index} {token}")
            reply = ctrl.query(f":NUMERIC:NORMAL:ITEM{index}?")
        except Exception:
            continue
        if _item_accepted(token, reply):
            accepted.append(token)
    if not accepted:
        return False, "仪器没有接受试读测量项", []
    try:
        ctrl.write(f":NUMERIC:NORMAL:NUMBER {len(accepted)}")
        for index, token in enumerate(accepted, start=1):
            ctrl.write(f":NUMERIC:NORMAL:ITEM{index} {token}")
    except Exception as exc:
        return False, f"压缩试读项失败: {exc}", accepted
    return True, f"试读已准备 ({detected}, {len(accepted)} 项)", accepted


def read_probe(ctrl: Any, items: Sequence[str]) -> Tuple[bool, str, Dict[str, float]]:
    if ctrl is None or not getattr(ctrl, "connected", False):
        return False, "功率分析仪未连接", {}
    if not items:
        return False, "还没有准备试读项", {}
    try:
        raw = ctrl.query(":NUMERIC:NORMAL:VALUE?")
    except Exception as exc:
        return False, f"读数失败: {exc}", {}
    measures = parse_probe_values(items, _parse_csv_floats(raw))
    if not measures:
        return False, "读数为空", {}
    count = max(
        (int(key[1:]) for key in measures if len(key) > 1 and key[1:].isdigit()),
        default=1,
    )
    return True, format_probe_text(measures, count), measures
