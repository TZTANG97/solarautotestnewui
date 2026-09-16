# -*- coding: utf-8 -*-
"""IOT 台架输出上限读回与开跑门禁（骨架；品牌读回待补）。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_SLOT_KEYS = ("ac", "dc1", "dc2", "dc3", "dc4")
_LIMIT_KEYS = ("volt_max", "curr_max", "pow_max")

_SLOT_LABEL_ZH = {
    "ac": "交流电源",
    "dc1": "直流电源1",
    "dc2": "直流电源2",
    "dc3": "直流电源3",
    "dc4": "直流电源4",
}

_FIELD_LABEL_ZH = {
    "volt_max": "电压",
    "curr_max": "电流",
    "pow_max": "功率",
}


def default_limits_path() -> Path:
    return Path(__file__).resolve().parent.parent / "config" / "iot_output_limits.json"


def load_expected_limits(path=None) -> dict:
    """从 JSON 加载期望上限。path 默认 config/iot_output_limits.json。"""
    p = Path(path) if path is not None else default_limits_path()
    with open(p, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("iot_output_limits.json 根节点必须是对象")
    return data


def _as_number(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        s = value.strip()
        if not s or s.lower() in ("null", "none"):
            return None
        try:
            return float(s)
        except ValueError:
            return None
    return None


def _slot_expected_numbers(slot_cfg: Any) -> Dict[str, float]:
    if not isinstance(slot_cfg, dict):
        return {}
    out: Dict[str, float] = {}
    for key in _LIMIT_KEYS:
        num = _as_number(slot_cfg.get(key))
        if num is not None:
            out[key] = num
    return out


def has_any_expected_limits(expected: Optional[dict]) -> bool:
    if not isinstance(expected, dict):
        return False
    for slot in _SLOT_KEYS:
        if _slot_expected_numbers(expected.get(slot)):
            return True
    return False


def _try_call(obj: Any, name: str) -> Any:
    if obj is None or not hasattr(obj, name):
        return None
    attr = getattr(obj, name)
    try:
        return attr() if callable(attr) else attr
    except Exception:
        return None


def _normalize_limits_dict(raw: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(raw, dict):
        return None
    out: Dict[str, Any] = {}
    for key in _LIMIT_KEYS:
        if key in raw:
            out[key] = raw.get(key)
        else:
            # 兼容常见别名
            aliases = {
                "volt_max": ("voltage_max", "v_max", "volt"),
                "curr_max": ("current_max", "i_max", "curr", "amp_max"),
                "pow_max": ("power_max", "p_max", "pow", "watt_max"),
            }
            for alt in aliases.get(key, ()):
                if alt in raw:
                    out[key] = raw.get(alt)
                    break
    if not out:
        return None
    return out


def _read_one_controller(ctrl: Any) -> Dict[str, Any]:
    if ctrl is None:
        return {"_unread": True, "detail": "未实现读回"}

    for method_name in ("query_output_limits", "get_output_limits", "read_output_limits"):
        raw = _try_call(ctrl, method_name)
        normalized = _normalize_limits_dict(raw)
        if normalized is not None:
            return normalized

    raw_limits = _try_call(ctrl, "limits")
    normalized = _normalize_limits_dict(raw_limits)
    if normalized is not None:
        return normalized

    # 单字段属性 / 无参方法（不发明 SCPI 字符串）
    collected: Dict[str, Any] = {}
    for key in _LIMIT_KEYS:
        val = None
        for name in (key, key.replace("_max", ""), "get_" + key, "query_" + key):
            got = _try_call(ctrl, name)
            if got is not None and not callable(got):
                val = got
                break
            if got is not None:
                val = got
                break
        if val is not None:
            collected[key] = val
    if collected:
        return collected

    return {"_unread": True, "detail": "未实现读回"}


def read_limits_from_controllers(ac_controller=None, dc_controllers=None) -> dict:
    """尽最大努力从控制器读回上限；不可用则标记 _unread。"""
    dc_map = dc_controllers or {}
    result: Dict[str, Any] = {
        "ac": _read_one_controller(ac_controller),
    }
    for slot in ("dc1", "dc2", "dc3", "dc4"):
        ctrl = dc_map.get(slot) or dc_map.get(slot.upper())
        result[slot] = _read_one_controller(ctrl)
    return result


def compare_limits(expected, actual) -> Tuple[bool, List[str]]:
    """
    对比期望与读回。
    - expected 某字段为 null/None：跳过
    - enforce=false：始终 ok=True，reasons 仍列出告警（超限/未读回）
    - enforce=true（默认）：有未读回或超限则 ok=False
    """
    expected = expected if isinstance(expected, dict) else {}
    actual = actual if isinstance(actual, dict) else {}
    enforce = bool(expected.get("enforce", True))
    reasons: List[str] = []

    for slot in _SLOT_KEYS:
        want = _slot_expected_numbers(expected.get(slot))
        if not want:
            continue
        label = _SLOT_LABEL_ZH.get(slot, slot)
        got_slot = actual.get(slot)
        if not isinstance(got_slot, dict):
            got_slot = {"_unread": True, "detail": "未实现读回"}

        if got_slot.get("_unread"):
            for key in want:
                field = _FIELD_LABEL_ZH.get(key, key)
                reasons.append("%s%s上限未能读回，禁止开跑" % (label, field))
            continue

        for key, exp_val in want.items():
            field = _FIELD_LABEL_ZH.get(key, key)
            act_num = _as_number(got_slot.get(key))
            if act_num is None:
                reasons.append("%s%s上限未能读回，禁止开跑" % (label, field))
                continue
            if act_num > exp_val:
                reasons.append(
                    "%s%s上限超限：期望≤%s，读回=%s，禁止开跑"
                    % (label, field, _fmt_num(exp_val), _fmt_num(act_num))
                )

    if not enforce:
        return True, reasons
    return (len(reasons) == 0), reasons


def _fmt_num(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return ("%s" % value).rstrip("0").rstrip(".") if "." in str(value) else str(value)


def format_limit_fail_reason(reasons) -> str:
    items = [str(r).strip() for r in (reasons or []) if str(r).strip()]
    if not items:
        return "输出上限检查未通过"
    if len(items) == 1:
        return items[0]
    return "；".join("%d.%s" % (i + 1, t) for i, t in enumerate(items))


def check_output_limits_gate(
    *,
    expected=None,
    actual=None,
    enforce=None,
    path=None,
) -> Tuple[bool, str]:
    """
    高阶门禁：配置缺失或全部期望为 null → 放行。
    enforce=false → 放行（即便有告警）。
    否则未读回/超限 → 禁止开跑。
    """
    exp = expected
    if exp is None:
        p = Path(path) if path is not None else default_limits_path()
        if not p.is_file():
            return True, ""
        try:
            exp = load_expected_limits(p)
        except Exception as exc:
            return False, "输出上限配置读取失败：%s" % exc

    if not isinstance(exp, dict):
        return True, ""

    if enforce is not None:
        exp = dict(exp)
        exp["enforce"] = bool(enforce)

    if not has_any_expected_limits(exp):
        return True, ""

    act = actual if actual is not None else {}
    ok, reasons = compare_limits(exp, act)
    if ok:
        return True, ""
    return False, format_limit_fail_reason(reasons)
