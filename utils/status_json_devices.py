# -*- coding: utf-8 -*-
"""status.json 设备行：保证连接时能写入，供 Agent 心跳上报 IOT。"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

# 与首页 / Agent instruments_snapshot 名称一致
DEFAULT_STATUS_DEVICE_NAMES: tuple[str, ...] = (
    "交流电源",
    "直流电源1",
    "直流电源2",
    "直流电源3",
    "直流电源4",
    "WT3000",
    "DL850",
    "DEWETRON",
)


def empty_status_payload() -> Dict[str, Any]:
    return {
        "devices": [
            {"name": n, "connected": False, "resource": "", "last_connected": ""}
            for n in DEFAULT_STATUS_DEVICE_NAMES
        ],
        "project": {},
    }


def ensure_device_rows(data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """补齐缺失的设备占位行（不覆盖已有 resource / last_connected）。"""
    if not isinstance(data, dict):
        return empty_status_payload()
    devices = data.get("devices")
    if not isinstance(devices, list):
        devices = []
    by_name = {
        str(d.get("name") or "").strip(): d
        for d in devices
        if isinstance(d, dict) and str(d.get("name") or "").strip()
    }
    out: List[Dict[str, Any]] = []
    for name in DEFAULT_STATUS_DEVICE_NAMES:
        if name in by_name:
            out.append(by_name.pop(name))
        else:
            out.append(
                {"name": name, "connected": False, "resource": "", "last_connected": ""}
            )
    # 保留未知额外行
    for extra in by_name.values():
        out.append(extra)
    data = dict(data)
    data["devices"] = out
    if "project" not in data or not isinstance(data.get("project"), dict):
        data["project"] = {}
    return data


def apply_device_connection(
    data: Optional[Dict[str, Any]],
    *,
    device_name: str,
    connected: bool,
    resource: str = "",
    now: Optional[datetime] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    更新/新建单台设备连接态。
    旧实现只改已有 name：status.json 为空或无该行时连接成功也不会入库 → IOT 台架仪器永远为空。
    extra：可选附加字段（如德威创 widgets / brand），写入同名设备行供 Agent 回填 Web。
    """
    payload = ensure_device_rows(data)
    name = (device_name or "").strip()
    if not name:
        return payload
    now_str = (now or datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    found = None
    for dev in payload["devices"]:
        if str(dev.get("name") or "").strip() == name:
            found = dev
            break
    if found is None:
        found = {"name": name, "connected": False, "resource": "", "last_connected": ""}
        payload["devices"].append(found)
    found["connected"] = bool(connected)
    if resource:
        found["resource"] = str(resource)
    if connected:
        found["last_connected"] = now_str
    if isinstance(extra, dict):
        for key, value in extra.items():
            if value is None:
                continue
            found[str(key)] = value
    return payload


def read_dewetron_ui_snapshot(dew_ui: Any) -> Dict[str, Any]:
    """从桌面德威创设置页读出 Web 需回填的字段。"""
    out: Dict[str, Any] = {
        "brand": "dewetron",
        "widgets": {},
    }
    if dew_ui is None:
        return out
    widgets: Dict[str, Any] = {}
    rate = getattr(dew_ui, "comboBox_maxRefreshRate", None)
    if rate is not None and hasattr(rate, "currentText"):
        try:
            text = str(rate.currentText() or "").strip()
            if text:
                widgets["comboBox_maxRefreshRate"] = text
                widgets["comboBox_DEW_MaxRefreshRate"] = text
        except Exception:
            pass
    ds = getattr(dew_ui, "comboBox_downsampling", None)
    if ds is not None and hasattr(ds, "currentText"):
        try:
            text = str(ds.currentText() or "").strip()
            if text:
                widgets["comboBox_downsampling"] = text
        except Exception:
            pass
    fc = getattr(dew_ui, "comboBox_frequencyChannel", None)
    if fc is not None and hasattr(fc, "currentText"):
        try:
            text = str(fc.currentText() or "").strip()
            if text:
                widgets["comboBox_frequencyChannel"] = text
        except Exception:
            pass
    wiring_i = None
    buttons = getattr(dew_ui, "_wiring_buttons", None)
    if buttons:
        try:
            for type_id, btn in buttons:
                if btn is not None and hasattr(btn, "isChecked") and btn.isChecked():
                    wiring_i = int(type_id)
                    break
        except Exception:
            wiring_i = None
    if wiring_i is None:
        canvas = getattr(dew_ui, "wiringDiagramCanvas", None)
        if canvas is not None and hasattr(canvas, "_wiring_type"):
            try:
                wiring_i = int(getattr(canvas, "_wiring_type"))
            except Exception:
                wiring_i = None
    if wiring_i is not None:
        widgets["dew_wiring_type"] = wiring_i
    out["widgets"] = widgets
    return out
