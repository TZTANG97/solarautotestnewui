# -*- coding: utf-8 -*-
"""WT SCPI 采集会话：对接 messure_testing / ASYNC_START，不走 WTViewer。"""
from __future__ import annotations

import os
import threading
import time
from typing import Any, Mapping, Optional

from devices.wt_data_collector import WtScpiCollector
from utils.wt_acquire_mode import (
    is_scpi_mode,
    rate_text_from_config,
    resolve_csv_path,
)
from utils.wt_scpi_items import describe_mapping, items_from_wt_config

_collector: Optional[WtScpiCollector] = None
_session_lock = threading.Lock()
_active = False
_stop_requested = False
_deadline_ts = 0.0
_last_csv = ""
_last_error = ""
# 模拟工况机注入的采点（优先于真机 collector）
_override_cloud_measures: Optional[dict] = None
_override_lock = threading.Lock()


def reset_session_state():
    global _active, _stop_requested, _deadline_ts, _last_csv, _last_error
    _active = False
    _stop_requested = False
    _deadline_ts = 0.0
    _last_csv = ""
    _last_error = ""
    set_cloud_measures_override(None)


def is_active() -> bool:
    return _active


def set_cloud_measures_override(measures: Optional[dict]) -> None:
    """sim / 测试注入 U/I/P，供 progress 上报曲线。传 None 清除。"""
    global _override_cloud_measures
    with _override_lock:
        if measures is None:
            _override_cloud_measures = None
        elif isinstance(measures, dict) and measures:
            _override_cloud_measures = dict(measures)
        else:
            _override_cloud_measures = None


def latest_cloud_measures() -> Optional[dict]:
    """供 Agent progress 附带 U/I/P；优先 override，否则真机 collector。"""
    with _override_lock:
        if _override_cloud_measures is not None:
            return dict(_override_cloud_measures)
    collector = _collector
    if collector is None:
        return None
    try:
        return collector.latest_cloud_measures()
    except Exception:
        return None


def last_csv() -> str:
    return _last_csv


def last_error() -> str:
    return _last_error


def request_stop(reason: str = ""):
    global _stop_requested
    _stop_requested = True
    print(f"[wt_scpi_session] stop requested: {reason or '-'}")


def _get_controller():
    """取当前已连接的 WT 控制器。

    直接 ``python SCPITestWave.py`` 时模块名是 ``__main__``，不是 ``SCPITestWave``；
    还必须读到连接后同步的 ``app.context``，否则会出现「按钮已取消连接但判未连接」。
    """
    import sys

    for name in ("SCPITestWave", "__main__"):
        mod = sys.modules.get(name)
        if mod is None:
            continue
        ctrl = getattr(mod, "wt3000_controller", None)
        if ctrl is not None:
            return ctrl
    try:
        from app.context import get_app_context

        ctx = get_app_context()
        return getattr(ctx, "wt3000_controller", None)
    except Exception:
        return None


def _wt_scale_hosts():
    """主窗口和连接页都试一次。输入框挂在主窗口上，显示在第 7 页里。"""
    import sys

    hosts = []
    for name in ("SCPITestWave", "__main__"):
        mod = sys.modules.get(name)
        if mod is None:
            continue
        ui = getattr(mod, "ui", None)
        if ui is not None and ui not in hosts:
            hosts.append(ui)
    page = _wt_connection_page()
    if page is not None and page not in hosts:
        hosts.append(page)
    return hosts


def _persist_connection_scales() -> None:
    for host in _wt_scale_hosts():
        panel = getattr(host, "widget_wt_scale", None)
        if panel is None:
            extra = getattr(host, "_extra_widgets_comboBox_WT3000", None)
            if isinstance(extra, dict):
                panel = extra.get("widget_wt_scale")
        if panel is not None and hasattr(panel, "persist_scales"):
            panel.persist_scales()
            return


def _wt_connection_page():
    """功率分析仪连接页（stackedWidget 第 7 页）。比例系数放在这里。"""
    import sys

    for name in ("SCPITestWave", "__main__"):
        mod = sys.modules.get(name)
        if mod is None:
            continue
        ui = getattr(mod, "ui", None)
        stack = getattr(ui, "stackedWidget", None) if ui is not None else None
        try:
            if stack is not None and stack.count() > 7:
                return stack.widget(7)
        except Exception:
            continue
    return None


def ensure_collector(logger=None) -> Optional[WtScpiCollector]:
    global _collector
    ctrl = _get_controller()
    if ctrl is None or not getattr(ctrl, "connected", False):
        return None
    with _session_lock:
        if _collector is None:
            _collector = WtScpiCollector(ctrl, logger)
            _collector.start()
        else:
            _collector._ctrl = ctrl
        return _collector


def prepare_from_config(config: Mapping, logger=None) -> tuple[bool, str]:
    """Prepare RATE + NUMERIC from Upper_WT_Config dict."""
    global _last_error
    if not is_scpi_mode(config):
        return True, ""
    collector = ensure_collector(logger)
    if collector is None:
        _last_error = "WT SCPI 未连接（设备管理中连接功率分析仪）"
        return False, _last_error
    rate = rate_text_from_config(config)
    csv_path = resolve_csv_path(config, 0)
    items = items_from_wt_config(config)
    from utils.wt_channel_scale import load_saved_scales, scaling_commands

    # 只用「下发并保存」写过的配置档；开测不把未点保存的输入框偷偷写档
    scale_cmds = scaling_commands(
        str(config.get("Style") or ""),
        load_saved_scales(),
    )
    try:
        summary = describe_mapping(config)
        print(
            f"[wt_scpi_session] items from UI: n={len(items)} "
            f"funcs={summary.get('functions')} targets={summary.get('targets')}"
        )
    except Exception:
        pass
    ok, _items, warnings = collector.prepare(
        items=items,
        rate_text=rate,
        save_path=csv_path,
        header_style=str(config.get("Style") or ""),
        scaling_commands=scale_cmds,
    )
    if warnings:
        print(f"[wt_scpi_session] warnings: {warnings}")
    if not ok:
        _last_error = collector.last_error() or "prepare 失败"
        return False, _last_error
    return True, ""


def run_measure_blocking(
    config: Mapping,
    *,
    file_index: int = 0,
    stop_event_check=None,
    async_stop_check=None,
    logger=None,
) -> bool:
    """Start SCPI gathering, wait StopTime / stop flags, export CSV.

    ``stop_event_check`` / ``async_stop_check`` are zero-arg callables returning bool.
    Sets module ``_active`` while running. Caller should set external ``test_status``.
    """
    global _active, _stop_requested, _deadline_ts, _last_csv, _last_error

    ok, err = prepare_from_config(config, logger=logger)
    if not ok:
        _last_error = err
        print(f"[wt_scpi_session] {err}")
        return False

    collector = ensure_collector(logger)
    if collector is None:
        return False

    csv_path = resolve_csv_path(config, file_index)
    if csv_path:
        collector.set_save_path = getattr(collector, "set_save_path", None)
        try:
            collector._save_path = csv_path
        except Exception:
            pass

    stop_sec = _stoptime_seconds(config)
    # 若 WAIT_END 已先打停，勿清掉；否则会把 StopTime 余量再空跑一遍
    pending_stop = bool(_stop_requested)
    _stop_requested = bool(pending_stop)
    _active = True
    _deadline_ts = time.time() + max(stop_sec, 0.5) + 0.5
    print(
        f"[wt_scpi_session] start gather rate={rate_text_from_config(config)} "
        f"stop={stop_sec}s csv={csv_path}"
    )
    if not collector.start_gathering():
        _active = False
        _last_error = collector.last_error() or "start_gathering 失败"
        return False

    exported_ok = False
    try:
        while True:
            if callable(stop_event_check) and stop_event_check():
                break
            if callable(async_stop_check) and async_stop_check():
                break
            if _stop_requested:
                break
            if time.time() >= _deadline_ts:
                break
            time.sleep(0.05)
    finally:
        collector.stop_gathering()
        exported = None
        try:
            if collector.total_rows() <= 0:
                collector.sample_once()
            exported = collector.export_to_csv(csv_path or None)
        except Exception as exc:
            _last_error = f"export failed: {exc}"
            print(f"[wt_scpi_session] {_last_error}")
        _last_csv = exported or ""
        stats = {}
        try:
            stats = collector.sample_interval_stats()
        except Exception:
            pass
        rows = 0
        try:
            rows = collector.total_rows()
        except Exception:
            rows = 0
        print(f"[wt_scpi_session] done rows={rows} stats={stats} csv={_last_csv or csv_path}")
        if not _last_csv:
            _last_error = (
                collector.last_error()
                or f"采到 {rows} 行，未生成 CSV（目标 {csv_path or '-'}）"
            )
            print(f"[wt_scpi_session] {_last_error}")
        else:
            exported_ok = True
        _active = False
    return exported_ok


def stop_and_export(config: Optional[Mapping] = None, file_index: int = 0) -> Optional[str]:
    """Force-stop gathering and export (End Test / WAIT_END)."""
    global _active, _last_csv
    request_stop("external")
    collector = _collector
    if collector is None:
        _active = False
        return None
    collector.stop_gathering()
    path = ""
    if isinstance(config, Mapping):
        path = resolve_csv_path(config, file_index)
    exported = collector.export_to_csv(path or None)
    _last_csv = exported or _last_csv
    _active = False
    return exported


def shutdown():
    """Stop thread on disconnect / app exit."""
    global _collector
    request_stop("shutdown")
    with _session_lock:
        if _collector is not None:
            try:
                _collector.stop()
            except Exception:
                pass
            _collector = None
    reset_session_state()


def _stoptime_seconds(config: Mapping) -> float:
    raw = str(config.get("textEdit_StopTime") or "").strip()
    if not raw:
        return 5.0
    # HH:MM:SS or MM:SS or seconds
    parts = raw.replace("：", ":").split(":")
    try:
        nums = [float(p) for p in parts if p != ""]
    except ValueError:
        return 5.0
    if len(nums) == 3:
        return nums[0] * 3600 + nums[1] * 60 + nums[2]
    if len(nums) == 2:
        return nums[0] * 60 + nums[1]
    if len(nums) == 1:
        return nums[0]
    return 5.0
