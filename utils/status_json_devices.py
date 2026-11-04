# -*- coding: utf-8 -*-
"""status.json 设备行：保证连接时能写入，供 Agent 心跳上报 IOT。"""
from __future__ import annotations

import json
import math
import os
import re
import threading
from contextlib import contextmanager
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


def project_status_is_live_local_run(progress_state: Optional[Dict[str, Any]], run_flag: str = "") -> bool:
    """本进程已经点过开始：进度是进行中，或执行标志已是运行/暂停。

    冷启动纠偏只能收上一次进程留下的「进行中」。
    自动连接结束、每 5 秒的会话纠偏若再收一次，会把刚开的电压闪变写成已中止。
    """
    if str(run_flag or "").strip() in ("运行", "暂停"):
        return True
    if not isinstance(progress_state, dict):
        return False
    status = str(progress_state.get("status") or "").strip()
    if status not in ("进行中", "暂停"):
        return False
    try:
        return float(progress_state.get("started_at") or 0) > 0
    except (TypeError, ValueError):
        return False


def status_when_binding_new_job(existing: str) -> str:
    """新任务号不能挂在上一局的终态上，否则心跳会立刻按「台架状态=已中止」结案。"""
    st = str(existing or "").strip()
    if st in ("", "未开始", "待开始", "已中止", "失败", "已结束", "中止"):
        return "进行中"
    return st


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


def format_report_number(value: float) -> str:
    """上报用短数字：650.0 → 650，12.30769 → 12.3077。"""
    try:
        num = float(value)
    except (TypeError, ValueError):
        return ""
    if not math.isfinite(num):
        return ""
    rounded = round(num, 4)
    if abs(rounded - round(rounded)) < 1e-9:
        return str(int(round(rounded)))
    return f"{rounded:.4f}".rstrip("0").rstrip(".")


def canonical_reported_brand(brand: str) -> str:
    """桌面面包屑 / 网页展示名 → IOT 下拉 value。

    网页下拉展示名是「蓝点(Bluesight)（Modbus 网口）」，不能只认整词 bluesight，
    否则连接计划会落到致茂页，蓝点页不会被选中。
    """
    raw = str(brand or "").strip()
    if not raw:
        return ""
    key = raw.lower().replace(" ", "")
    aliases = {
        "itech": "itech",
        "it6000": "itech",
        "爱科": "itech",
        "bluesight": "bluesight",
        "蓝点": "bluesight",
        "蓝电": "bluesight",
        "chroma": "chroma",
        "致茂": "chroma",
        "chroma_ip": "chroma_ip",
        "chroma-ip": "chroma_ip",
        "chromaip": "chroma_ip",
        "keysight": "keysight",
        "agilent": "keysight",
        "是德": "keysight",
        "dewetron": "dewetron",
        "yokogawa": "yokogawa",
    }
    hit = aliases.get(key)
    if hit:
        return hit
    low = raw.lower()
    if "bluesight" in low or "蓝点" in raw or "蓝电" in raw:
        return "bluesight"
    if "爱科" in raw or "itech" in low or "it6000" in low:
        return "itech"
    if "是德" in raw or "keysight" in low or "agilent" in low:
        return "keysight"
    if "致茂" in raw or "chroma" in low:
        if "chroma_ip" in key or "chromaip" in key:
            return "chroma_ip"
        return "chroma"
    if "dewetron" in low or "德威创" in raw:
        return "dewetron"
    if "yokogawa" in low or "横河" in raw:
        return "yokogawa"
    return aliases.get(raw.lower(), raw.lower())


def bluesight_iv_fields(page: Optional[Dict[str, Any]]) -> Dict[str, str]:
    """蓝点页当前值 → Vmp/Voc/Imp/Isc/功率%。

    SAS：Vmp=Umpp，Imp=Pmpp(kW)×1000/Umpp，Voc/Isc 只用页上的填充因子拆开
    （FF=Vmp×Imp/(Voc×Isc)），功率%记 100。不读致茂/爱科页的 220 或 Sandia 默认。
    原始负载：只填当前模式那一项，其余留空。
    """
    blank = {"vmp": "", "voc": "", "imp": "", "isc": "", "pf": ""}
    if not isinstance(page, dict):
        return dict(blank)
    mode = str(page.get("mode") or "").strip().lower()
    if mode == "sas":
        try:
            umpp = float(page.get("umpp_v"))
            pmpp = float(page.get("pmpp_kw"))
            ff_v = float(page.get("ff"))
        except (TypeError, ValueError):
            return dict(blank)
        if umpp <= 0 or pmpp <= 0 or not (0 < ff_v < 1):
            return dict(blank)
        imp = pmpp * 1000.0 / umpp
        scale = math.sqrt(ff_v)
        out = dict(blank)
        out["vmp"] = format_report_number(umpp)
        out["imp"] = format_report_number(imp)
        out["voc"] = format_report_number(umpp / scale)
        out["isc"] = format_report_number(imp / scale)
        out["pf"] = "100"
        return out
    out = dict(blank)
    outmode = str(page.get("outmode") or "").strip().lower()
    try:
        if outmode == "cv" and page.get("voltage_v") not in (None, ""):
            voltage = float(page["voltage_v"])
            # 原始负载电压默认 0，不能当成 Vmp 回写，否则网页四点每次被清成 0。
            if voltage > 0:
                out["vmp"] = format_report_number(voltage)
        elif outmode == "cc" and page.get("current_a") not in (None, ""):
            current = float(page["current_a"])
            if current > 0:
                out["imp"] = format_report_number(current)
    except (TypeError, ValueError):
        return dict(blank)
    return out


_IV_WIDGET_KEYS = (
    ("vmp", "textEdit_Vmp", "vmp", "voltage"),
    ("imp", "textEdit_Imp", "imp", "current"),
    ("voc", "textEdit_Voc", "voc", None),
    ("isc", "textEdit_Isc", "isc", None),
    ("pf", "textEdit_PF", "powerPercent", None),
)


def dc_connection_extra(
    *,
    brand: str,
    iv: Optional[Dict[str, Any]] = None,
    slot: str = "dc1",
    force_iv: bool = False,
) -> Dict[str, Any]:
    """直流连接态附加字段：品牌 + 有值的 IV。空串和 0 不回写，避免冲掉网页已算好的四点。"""
    canon = canonical_reported_brand(brand)
    out: Dict[str, Any] = {"brand": canon, "slot": str(slot or "dc1").lower(), "measures": {}}
    src = iv if isinstance(iv, dict) else {}
    force = bool(force_iv) or canon == "bluesight"
    widgets: Dict[str, str] = {}
    measures: Dict[str, str] = {}
    for key, widget_key, measure_key, alias in _IV_WIDGET_KEYS:
        if key not in src and not force:
            continue
        val = str(src.get(key) or "").strip()
        if not val:
            continue
        if key in ("vmp", "voc", "imp", "isc"):
            try:
                if float(val) == 0.0:
                    continue
            except (TypeError, ValueError):
                pass
        widgets[widget_key] = val
        if val:
            measures[measure_key] = val
            if alias and alias not in out:
                out[alias] = val
    if widgets:
        out["widgets"] = widgets
    if measures:
        out["measures"] = measures
    return out


def ac_connection_extra(
    *,
    brand: str,
    voltage: str = "",
    frequency: str = "",
    phase: str = "",
) -> Dict[str, Any]:
    """交流连接态：品牌 + 当前页电压/频率/相位。"""
    canon = canonical_reported_brand(brand)
    out: Dict[str, Any] = {"brand": canon, "measures": {}}
    widgets: Dict[str, str] = {}
    measures: Dict[str, str] = {}
    volt = str(voltage or "").strip()
    freq = str(frequency or "").strip()
    ph = str(phase or "").strip()
    if volt:
        widgets["textEdit_AC_VOLT"] = volt
        measures["voltage"] = volt
        out["voltage"] = volt
    if freq:
        widgets["textEdit_AC_FR"] = freq
        measures["frequency"] = freq
        out["frequency"] = freq
    if ph:
        widgets["comboBox_Phase"] = ph
        measures["phase"] = ph
    if widgets:
        out["widgets"] = widgets
    if measures:
        out["measures"] = measures
    return out



_VOLT_RE = re.compile(
    r"(?:^|[;:])(?:SOUR(?:CE)?:)?VOLT(?:AGE)?(?:[:\s]+)([+-]?\d+(?:\.\d+)?)",
    re.IGNORECASE,
)
_FREQ_RE = re.compile(
    r"(?:^|[;:])(?:SOUR(?:CE)?:)?FREQ(?:UENCY)?(?:[:\s]+)([+-]?\d+(?:\.\d+)?)",
    re.IGNORECASE,
)
_OUTP_RE = re.compile(
    r"OUTP(?:UT)?(?::STAT(?:E)?)?(?:[:\s]+)(ON|OFF|1|0)\b",
    re.IGNORECASE,
)
_PHASE_RE = re.compile(
    r"INST:PHAS(?:E)?(?:[:\s]+)(SINGLE|THREE|1|3)\b",
    re.IGNORECASE,
)
_IV_RE = re.compile(
    r"\b(VMP|IMP|VOC|ISC)\s*[:= ]\s*([+-]?\d+(?:\.\d+)?)",
    re.IGNORECASE,
)
_STC_RE = re.compile(
    r"BLUESIGHT:STC\s+([+-]?\d+(?:\.\d+)?)\s+([+-]?\d+(?:\.\d+)?)",
    re.IGNORECASE,
)


def measures_from_supply_command(command: str) -> Dict[str, str]:
    """从刚下发的电源写命令抽出当前电压/频率/相数/直流设定，供台架卡片跟随。"""
    text = str(command or "").strip()
    if not text:
        return {}
    out: Dict[str, str] = {}
    volt = _VOLT_RE.search(text)
    if volt:
        out["voltage"] = volt.group(1)
    freq = _FREQ_RE.search(text)
    if freq:
        out["frequency"] = freq.group(1)
    outp = _OUTP_RE.search(text)
    if outp:
        flag = outp.group(1).upper()
        out["output"] = "off" if flag in ("OFF", "0") else "on"
    phase = _PHASE_RE.search(text)
    if phase:
        token = phase.group(1).upper()
        out["phase"] = "单相" if token in ("SINGLE", "1") else "三相"
    for match in _IV_RE.finditer(text):
        out[match.group(1).lower()] = match.group(2)
    stc = _STC_RE.search(text)
    if stc and "vmp" not in out:
        out["vmp"] = stc.group(2)
    return out


_STATUS_THREAD_LOCKS: Dict[str, threading.Lock] = {}
_STATUS_THREAD_GUARD = threading.Lock()


def _thread_lock_for(status_path: str) -> threading.Lock:
    with _STATUS_THREAD_GUARD:
        lock = _STATUS_THREAD_LOCKS.get(status_path)
        if lock is None:
            lock = threading.Lock()
            _STATUS_THREAD_LOCKS[status_path] = lock
        return lock


@contextmanager
def status_json_lock(status_path: str):
    """整份 status.json 读改写共用一把锁，避免进度落盘盖掉刚写入的电压。"""
    path = str(status_path or "").strip()
    lock_path = path + ".lock"
    folder = os.path.dirname(lock_path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with _thread_lock_for(path):
        fh = open(lock_path, "a+b")
        try:
            if fh.seek(0, os.SEEK_END) < 1:
                fh.write(b" ")
                fh.flush()
            if os.name == "nt":
                import msvcrt

                fh.seek(0)
                msvcrt.locking(fh.fileno(), msvcrt.LK_LOCK, 1)
            else:
                import fcntl

                fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
            yield
        finally:
            try:
                if os.name == "nt":
                    import msvcrt

                    fh.seek(0)
                    msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
            except Exception:
                pass
            fh.close()


def note_supply_command(status_path: str, *, device_name: str, command: str) -> bool:
    """把本条电源命令反映进 status.json。没有电压/频率/输出则不写。"""
    extra_measures = measures_from_supply_command(command)
    if not extra_measures:
        return False
    path = str(status_path or "").strip()
    if not path:
        return False
    with status_json_lock(path):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:
            data = empty_status_payload()
        data = update_device_measures(
            data,
            device_name=device_name,
            extra={"measures": extra_measures, **{k: v for k, v in extra_measures.items() if k != "output"}},
        )
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
    return True


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
    scales_fn = getattr(dew_ui, "channel_scale_factors", None)
    if callable(scales_fn):
        try:
            scales = scales_fn()
        except Exception:
            scales = None
        if isinstance(scales, dict) and scales:
            widgets["dew_channel_scales"] = {
                str(key): str(value)
                for key, value in scales.items()
                if str(value).strip()
            }
    out["widgets"] = widgets
    return out
