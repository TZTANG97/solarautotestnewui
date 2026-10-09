# -*- coding: utf-8 -*-
"""WT 切换闪变显示页（DISPLAY:MODE FLICker）。

WT3000 / WT3004E 等同系列共用该 SCPI；优先用已连接的 wt3000_controller。
"""
from __future__ import annotations

from typing import Any, Dict, Optional


FLICKER_MODE_CMDS = (
    "DISPLAY:MODE FLICker",
    ":DISPLAY:MODE FLICker",
)


def _controller():
    try:
        from utils.wt_scpi_session import _get_controller

        return _get_controller()
    except Exception:
        return None


def switch_wt_flicker_display(instrument: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """切换仪表到闪变页面。instrument 可带 resource/model，仅用于文案。"""
    inst = instrument if isinstance(instrument, dict) else {}
    model = str(inst.get("model") or "").strip() or "WT"
    resource = str(inst.get("resource") or inst.get("addr") or "").strip()

    ctrl = _controller()
    # 二次兜底：部分启动路径只更新了 __main__ 全局，会话模块偶发读不到
    if ctrl is None or not getattr(ctrl, "connected", False):
        try:
            import sys

            for name in ("__main__", "SCPITestWave"):
                mod = sys.modules.get(name)
                if mod is None:
                    continue
                alt = getattr(mod, "wt3000_controller", None)
                if alt is not None and getattr(alt, "connected", False):
                    ctrl = alt
                    break
        except Exception:
            pass
    if ctrl is None or not getattr(ctrl, "connected", False):
        hint = f"（目标 {model}"
        if resource:
            hint += f" {resource}"
        hint += "）"
        return {
            "ok": False,
            "message": (
                f"WT 未连接{hint}，请先在仪器面板连接功率分析仪后再切闪变页"
                f"（若按钮已是「取消连接」仍见此提示，请断开后重连一次再试）"
            ),
        }

    handle = getattr(ctrl, "handle", None)
    if handle is None or not hasattr(handle, "write"):
        return {"ok": False, "message": "WT 会话无写通道，请断开后重新连接"}

    try:
        from utils.wt_flicker_scpi import ensure_remote

        ok_r, msg_r = ensure_remote(ctrl)
        if not ok_r:
            return {"ok": False, "message": msg_r}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "message": f"切换远程模式失败: {exc}"}

    last_exc: Optional[BaseException] = None
    for cmd in FLICKER_MODE_CMDS:
        try:
            handle.write(cmd)
            # 已在闪变页时面板可能无视觉变化，仍返回成功并提示看 REMOTE 灯
            return {
                "ok": True,
                "message": (
                    f"已下发闪变显示（{model} {cmd}）。"
                    f"请确认面板 REMOTE 灯亮；若本就在闪变页，画面可能不变。"
                ),
                "command": cmd,
            }
        except Exception as exc:  # noqa: BLE001 — 汇总后返回
            last_exc = exc

    return {
        "ok": False,
        "message": f"切换闪变页面失败: {last_exc}",
    }
