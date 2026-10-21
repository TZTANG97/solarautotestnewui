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


# 进程退出后不可能仍在跑的状态（内存试验线程已没了）
_STALE_IN_FLIGHT_STATUSES = frozenset({"进行中", "暂停", "待开始"})


def mark_stale_in_flight_project(data: Optional[Dict[str, Any]]) -> tuple[Dict[str, Any], bool]:
    """
    软件冷启动时：若 status.json 仍写着「进行中/暂停」，改为「已中止」。
    试验进度会落盘供 Agent/首页展示，但重启后线程已不在，不能继续显示进行中。
    返回 (payload, changed)。
    """
    payload = ensure_device_rows(data)
    proj = payload.get("project")
    if not isinstance(proj, dict):
        return payload, False
    status = str(proj.get("status") or "").strip()
    if status not in _STALE_IN_FLIGHT_STATUSES:
        return payload, False
    proj = dict(proj)
    proj["status"] = "已中止"
    proj["operator_pause"] = False
    proj["estimated_end_time"] = ""
    proj["remain_text"] = ""
    proj["remain_s"] = 0.0
    detail = str(proj.get("current_detail") or "").strip()
    if not detail or "进程已退出" not in detail:
        proj["current_detail"] = "软件已重新打开，上次未跑完的试验已标为中止"
    rounds = []
    for r in proj.get("rounds") or []:
        if not isinstance(r, dict):
            continue
        item = dict(r)
        if str(item.get("status") or "") in ("进行中", "等待", "暂停", "待开始"):
            item["status"] = "中止"
            note = str(item.get("note") or "").strip()
            if not note:
                item["note"] = "软件重启"
        rounds.append(item)
    if rounds:
        proj["rounds"] = rounds
    queue = []
    for q in proj.get("queue") or []:
        if not isinstance(q, dict):
            continue
        item = dict(q)
        if str(item.get("status") or "") in ("进行中", "等待", "暂停", "待开始"):
            item["status"] = "中止"
        queue.append(item)
    if "queue" in proj:
        proj["queue"] = queue
    payload = dict(payload)
    payload["project"] = proj
    return payload, True


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



def _plain_text(widget) -> str:
    if widget is None:
        return ""
    try:
        if hasattr(widget, "toPlainText"):
            return str(widget.toPlainText() or "").strip()
        if hasattr(widget, "text"):
            return str(widget.text() or "").strip()
        if hasattr(widget, "currentText"):
            return str(widget.currentText() or "").strip()
    except Exception:
        return ""
    return ""


def read_ac_ui_snapshot(ac_ui: Any) -> Dict[str, Any]:
    """交流源设置页当前电压/频率 → status.json / Agent 上报。"""
    out: Dict[str, Any] = {"measures": {}}
    if ac_ui is None:
        return out
    volt = _plain_text(getattr(ac_ui, "textEdit_AC_VOLT", None))
    freq = _plain_text(getattr(ac_ui, "textEdit_AC_FR", None))
    measures: Dict[str, Any] = {}
    if volt:
        measures["voltage"] = volt
        out["voltage"] = volt
    if freq:
        measures["frequency"] = freq
        out["frequency"] = freq
    if measures:
        out["measures"] = measures
    return out


def read_dc_ui_snapshot(dc_ui: Any, *, slot: str = "dc1") -> Dict[str, Any]:
    """直流源设置页当前 IV 设定 → status.json / Agent 上报。"""
    out: Dict[str, Any] = {"measures": {}}
    if dc_ui is None:
        return out
    measures: Dict[str, Any] = {}
    mapping = (
        ("textEdit_Vmp", "vmp", "voltage"),
        ("textEdit_Imp", "imp", "current"),
        ("textEdit_Voc", "voc", None),
        ("textEdit_Isc", "isc", None),
        ("textEdit_PF", "powerPercent", None),
    )
    for attr, key, alias in mapping:
        val = _plain_text(getattr(dc_ui, attr, None))
        if not val:
            continue
        measures[key] = val
        if alias and alias not in out:
            out[alias] = val
    if measures:
        out["measures"] = measures
        out["slot"] = str(slot or "dc1").lower()
    return out



def update_device_measures(
    data: Optional[Dict[str, Any]],
    *,
    device_name: str,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """只刷新量测/设定字段，不改 connected / resource。"""
    payload = ensure_device_rows(data)
    name = (device_name or "").strip()
    if not name or not isinstance(extra, dict):
        return payload
    for dev in payload["devices"]:
        if str(dev.get("name") or "").strip() != name:
            continue
        for key, value in extra.items():
            if value is None:
                continue
            if key == "measures" and isinstance(value, dict):
                merged = dict(dev.get("measures") or {}) if isinstance(dev.get("measures"), dict) else {}
                merged.update({str(k): v for k, v in value.items() if v is not None})
                dev["measures"] = merged
            else:
                dev[str(key)] = value
        break
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
    # 槽位通道映射（与 Web dew_channel_map 对称）
    slot_widgets = getattr(dew_ui, "_slot_input_widgets", None)
    if isinstance(slot_widgets, dict) and slot_widgets:
        ch_map: dict = {}
        for slot_name, le in slot_widgets.items():
            try:
                text = ""
                if hasattr(le, "get_channel"):
                    text = str(le.get_channel() or "").strip()
                elif hasattr(le, "text"):
                    text = str(le.text() or "").strip()
                if text:
                    ch_map[str(slot_name)] = text
            except Exception:
                continue
        if ch_map:
            widgets["dew_channel_map"] = ch_map
    out["widgets"] = widgets
    return out
