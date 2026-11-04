# -*- coding: utf-8 -*-
"""IOT 仪器控制 inbox：Agent 写 pending，桌面 SolarAutoTest 执行后写 results。

目录：iot_job_inbox/device_cmds/{pending,results}/
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


def device_cmds_root(repo_root: Path) -> Path:
    return Path(repo_root) / "iot_job_inbox" / "device_cmds"


def write_pending(repo_root: Path, request_id: str, payload: Dict[str, Any]) -> Path:
    root = device_cmds_root(repo_root)
    pending = root / "pending"
    pending.mkdir(parents=True, exist_ok=True)
    (root / "results").mkdir(parents=True, exist_ok=True)
    path = pending / f"cmd_{request_id}.json"
    body = dict(payload or {})
    body["requestId"] = request_id
    body["writtenAt"] = time.strftime("%Y-%m-%d %H:%M:%S")
    path.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def result_path(repo_root: Path, request_id: str) -> Path:
    return device_cmds_root(repo_root) / "results" / f"cmd_{request_id}.json"


def write_result(repo_root: Path, request_id: str, result: Dict[str, Any]) -> Path:
    root = device_cmds_root(repo_root)
    out_dir = root / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"cmd_{request_id}.json"
    body = dict(result or {})
    body["requestId"] = request_id
    body["finishedAt"] = time.strftime("%Y-%m-%d %H:%M:%S")
    path.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def wait_result(
    repo_root: Path,
    request_id: str,
    *,
    timeout_sec: float = 90.0,
    poll_sec: float = 0.4,
) -> Optional[Dict[str, Any]]:
    path = result_path(repo_root, request_id)
    deadline = time.time() + float(timeout_sec)
    while time.time() < deadline:
        if path.is_file():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else {"ok": False, "message": "结果格式错误"}
            except Exception as exc:
                return {"ok": False, "message": f"读取结果失败: {exc}"}
        time.sleep(poll_sec)
    return None


def list_pending(repo_root: Path) -> List[Path]:
    pending = device_cmds_root(repo_root) / "pending"
    if not pending.is_dir():
        return []
    return sorted(pending.glob("cmd_*.json"))


def execute_device_cmd(
    payload: Dict[str, Any],
    *,
    apply_connect: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    apply_disconnect: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    output_on: Optional[Callable[[str], bool]] = None,
    output_off: Optional[Callable[[str], bool]] = None,
    dew_build: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    switch_flicker: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    log: Optional[Callable[[str], None]] = None,
) -> Dict[str, Any]:
    """在桌面主线程执行一条控制命令。"""
    _log = log or (lambda m: None)
    action = str(payload.get("action") or "").strip().lower()
    instrument = payload.get("instrument") if isinstance(payload.get("instrument"), dict) else {}
    slot = str(instrument.get("slot") or "").strip().lower()
    widgets = payload.get("widgets") if isinstance(payload.get("widgets"), dict) else {}

    try:
        if action == "connect":
            if not apply_connect:
                return {"ok": False, "message": "桌面未注册连接回调"}
            # 把 Web 下发的 widgets（如 AC 单相/三相）带进连接回调
            inst_payload = dict(instrument or {})
            if widgets:
                inst_payload["widgets"] = dict(widgets)
            summary = apply_connect(inst_payload)
            ok = bool((summary or {}).get("ok", True))
            msg = str((summary or {}).get("message") or ("连接成功" if ok else "连接失败"))
            _log(f"[仪器控制] connect {slot}: {msg}")
            return {"ok": ok, "message": msg, "detail": summary or {}}

        if action == "disconnect":
            if apply_disconnect:
                summary = apply_disconnect(instrument)
                ok = bool((summary or {}).get("ok", True))
                msg = str((summary or {}).get("message") or ("已断开" if ok else "断开失败"))
                _log(f"[仪器控制] disconnect {slot}: {msg}")
                return {"ok": ok, "message": msg, "detail": summary or {}}
            if output_off and slot:
                try:
                    output_off(slot)
                except Exception:
                    pass
            _log(f"[仪器控制] disconnect {slot}: 已请求关输出（无专用断开回调）")
            return {"ok": True, "message": f"{slot} 已请求断开/关输出"}

        if action == "output_on":
            if not output_on:
                return {"ok": False, "message": "桌面未注册开输出回调"}
            # 兼容旧签名 output_on(slot)；新签名可带 widgets（DC IV 先下发再开输出）
            try:
                w_on = dict(widgets)
                brand_on = str(instrument.get("brand") or "").strip()
                if brand_on and not w_on.get("_iot_brand"):
                    w_on["_iot_brand"] = brand_on
                ok = bool(output_on(slot, w_on))  # type: ignore[call-arg]
            except TypeError:
                ok = bool(output_on(slot))
            msg = f"{slot} 打开输出{'成功' if ok else '失败'}"
            _log(f"[仪器控制] {msg}")
            return {"ok": ok, "message": msg}

        if action == "output_off":
            if not output_off:
                return {"ok": False, "message": "桌面未注册关输出回调"}
            ok = bool(output_off(slot))
            msg = f"{slot} 关闭输出{'成功' if ok else '失败'}"
            _log(f"[仪器控制] {msg}")
            return {"ok": ok, "message": msg}

        if action == "dew_build":
            if not dew_build:
                return {"ok": False, "message": "桌面未注册德威创构造回调"}
            summary = dew_build(widgets)
            ok = bool((summary or {}).get("ok", False))
            msg = str((summary or {}).get("message") or ("构造完成" if ok else "构造失败"))
            _log(f"[仪器控制] dew_build: {msg}")
            return {"ok": ok, "message": msg, "detail": summary or {}}

        if action == "switch_flicker":
            if not switch_flicker:
                return {"ok": False, "message": "桌面未注册切换闪变页面回调（请升级 SolarAutoTest）"}
            summary = switch_flicker(instrument)
            ok = bool((summary or {}).get("ok", False))
            msg = str((summary or {}).get("message") or ("已切换闪变页面" if ok else "切换失败"))
            _log(f"[仪器控制] switch_flicker: {msg}")
            return {"ok": ok, "message": msg, "detail": summary or {}}

        return {"ok": False, "message": f"未知动作: {action}"}
    except Exception as exc:
        _log(f"[仪器控制] 异常 {action}/{slot}: {exc}")
        return {"ok": False, "message": str(exc)[:500]}
