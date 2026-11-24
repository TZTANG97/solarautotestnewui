# -*- coding: utf-8 -*-
"""设备发现结果 → 现有连接路径的薄胶水（不含 PyQt 对话框）。"""
from __future__ import annotations

from typing import Any, Dict, Optional

from utils.device_discovery import FoundDevice, connect_plan


def build_connect_jobs(slot_device_pairs):
    """[(slot, FoundDevice), ...] → [(slot, plan, device), ...]"""
    out = []
    for slot, dev in slot_device_pairs:
        if not isinstance(dev, FoundDevice):
            continue
        plan = connect_plan(str(slot or ""), dev)
        out.append((str(slot), plan, dev))
    return out


def combo_text_for_plan(plan: Dict[str, Any]) -> Optional[str]:
    """多数槽位写入 comboBox 的文本。"""
    target = str(plan.get("target") or "")
    if target in ("ac_itech", "ac_chroma_ip"):
        host = plan.get("host") or ""
        port = plan.get("port")
        if not host:
            return None
        if port:
            return f"{host}:{port}"
        return str(host)
    if target == "ac_visa":
        return str(plan.get("resource") or "") or None
    if target in ("dc_itech", "dc_modbus", "dc_chroma"):
        return str(plan.get("addr") or plan.get("host") or "") or None
    if target == "scope":
        return str(plan.get("resource") or "") or None
    if target == "wt":
        host = plan.get("host") or ""
        port = plan.get("port")
        if host and port:
            return f"{host}:{port}"
        if host:
            return str(host)
        return str(plan.get("resource") or "") or None
    if target == "dew":
        host = plan.get("host") or ""
        port = plan.get("port") or 10001
        if host:
            return f"{host}:{port}"
        return None
    return str(plan.get("resource") or "") or None


def remember_text_for_plan(plan: Optional[Dict[str, Any]], dev: Any) -> str:
    """连接成功后写入历史/槽位偏好的地址。

    WT 的 ``connect_plan`` 会把 502/2101/8080 改成 5025；必须记修正后的口，
    不能写回扫描到的电源口 ``dev.resource``。
    """
    text = combo_text_for_plan(plan or {}) or ""
    if text:
        return text
    return str(getattr(dev, "resource", "") or "")
