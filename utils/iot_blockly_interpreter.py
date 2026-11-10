# -*- coding: utf-8 -*-
"""
光伏 Blockly 解释器（终态 B 试点）。

默认路径仍是 Dialog Append；仅当 job.executionMode=blockly_interpret
且试验类型支持时进入。失败可回退 Append。

解析语义对齐 IOT solar_procedure_package._parse_write_lines。
"""
from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

EXECUTION_DIALOG_APPEND = "dialog_append"
EXECUTION_BLOCKLY_INTERPRET = "blockly_interpret"

# 过欠压扫段：积木 writeKey / 字段名 → Dialog checkBox_SN
_OVUF_SEG_FIELD_RE = re.compile(
    r"(?:textEdit|comboBox)_S([3-8])_(?:AC_VOLT|AC_FR|Step_Size|TIME)",
    flags=re.I,
)
_OVUF_SCAN_TYPE_RE = re.compile(r"mid_ovuf_s([3-8])_scan", flags=re.I)
_OVUF_MAIN_KEYS = frozenset(
    {
        "solar_ovuf",
        "solar_guoqianya_pin",
        "guoqianya_pin",
        "过欠压_过欠频",
    }
)


def normalize_execution_mode(raw: Any) -> str:
    s = str(raw or "").strip().lower()
    # 仅显式 blockly_interpret（及同义 interpret）才进灰度；勿认 "blockly"/"b" 以免误开
    if s in ("blockly_interpret", "interpret"):
        return EXECUTION_BLOCKLY_INTERPRET
    return EXECUTION_DIALOG_APPEND


def parse_blockly_write_steps(code: str) -> List[Dict[str, str]]:
    """解析 EQID^…,write^key^val^unit; → 保序步骤。"""
    out: List[Dict[str, str]] = []
    for m in re.finditer(
        r"EQID\^([^,]+),write\^([^;\n]+);",
        code or "",
        flags=re.I,
    ):
        equ = (m.group(1) or "").strip()
        rest = (m.group(2) or "").strip()
        parts = rest.split("^")
        key = (parts[0] or "").strip() if parts else ""
        val = (parts[1] or "").strip() if len(parts) > 1 else ""
        unit = (parts[2] or "").strip() if len(parts) > 2 else ""
        if not key:
            continue
        out.append({"equId": equ, "writeKey": key, "value": val, "unit": unit})
    return out


def ovuf_segment_order_from_steps(steps: Sequence[Dict[str, Any]]) -> List[int]:
    """从积木步骤推断扫段顺序（首次出现的 S3~S8）。删掉的段不会出现。"""
    order: List[int] = []
    seen = set()
    for st in steps or []:
        key = str(st.get("writeKey") or st.get("blocklyName") or "")
        sn: Optional[int] = None
        m = _OVUF_SEG_FIELD_RE.search(key)
        if m:
            sn = int(m.group(1))
        else:
            m2 = _OVUF_SCAN_TYPE_RE.search(key)
            if m2:
                sn = int(m2.group(1))
        if sn is None or sn in seen:
            continue
        seen.add(sn)
        order.append(sn)
    return order


def plan_from_blockly(
    code: str,
    *,
    procedure_steps: Optional[Sequence[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """生成可观测执行计划（不驱动设备）。"""
    writes = parse_blockly_write_steps(code or "")
    if not writes and procedure_steps:
        for i, row in enumerate(procedure_steps):
            if not isinstance(row, dict):
                continue
            key = str(row.get("blocklyName") or row.get("writeKey") or "").strip()
            if not key:
                continue
            writes.append(
                {
                    "equId": str(row.get("equId") or ""),
                    "writeKey": key,
                    "value": str(row.get("value") or ""),
                    "unit": str(row.get("unit") or ""),
                    "index": str(row.get("index") or i + 1),
                }
            )
    seg_order = ovuf_segment_order_from_steps(writes)
    widget_writes = [
        w
        for w in writes
        if str(w.get("writeKey") or "").startswith(
            ("textEdit_", "comboBox_", "checkBox_", "radio_", "spinBox_")
        )
    ]
    return {
        "steps": writes,
        "widgetWrites": widget_writes,
        "ovufSegmentOrder": seg_order,
        "stepCount": len(writes),
    }


def _set_checkbox(ui: Any, name: str, on: bool) -> None:
    cb = getattr(ui, name, None)
    if cb is None:
        return
    try:
        if hasattr(cb, "setChecked"):
            cb.setChecked(bool(on))
        elif hasattr(cb, "setCheckState"):
            from PyQt5.QtCore import Qt  # type: ignore

            cb.setCheckState(Qt.Checked if on else Qt.Unchecked)
    except Exception:
        pass


def sync_ovuf_checkboxes_from_plan(ui: Any, plan: Dict[str, Any]) -> List[int]:
    """按积木出现的扫段开关 Dialog checkBox_S3~S8；返回启用顺序。

    积木未带任何 S3~S8 字段时不改 Dialog 勾选（保持 handoff/表单原状）。
    """
    order = list(plan.get("ovufSegmentOrder") or [])
    if not order:
        try:
            ui._iot_blockly_segment_order = []
        except Exception:
            pass
        return []
    enabled = set(order)
    for sn in (3, 4, 5, 6, 7, 8):
        _set_checkbox(ui, f"checkBox_S{sn}", sn in enabled)
    try:
        ui._iot_blockly_segment_order = list(order)
    except Exception:
        pass
    return order


def apply_widget_writes_from_plan(
    ui: Any,
    plan: Dict[str, Any],
    *,
    apply_widget_values: Optional[Callable[[Any, Dict[str, Any]], List[str]]] = None,
) -> List[str]:
    """把积木 write^textEdit_/comboBox_ 保序合并后写入 Dialog。"""
    widgets: Dict[str, Any] = {}
    for w in plan.get("widgetWrites") or []:
        key = str(w.get("writeKey") or "").strip()
        if not key:
            continue
        widgets[key] = w.get("value")
        unit = str(w.get("unit") or "").strip()
        if unit and key.startswith("textEdit_"):
            ukey = key.replace("textEdit_", "comboBox_", 1)
            if ukey not in widgets:
                widgets[ukey] = unit
    if not widgets:
        return []
    if apply_widget_values is None:
        from utils.iot_ui_handoff import apply_widget_values as _apply

        apply_widget_values = _apply
    return list(apply_widget_values(ui, widgets) or [])


def shadow_compare_plan(
    plan: Dict[str, Any],
    *,
    procedure_steps: Optional[Sequence[Dict[str, Any]]] = None,
    widgets: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """影子对照：积木步骤 vs procedureSteps / widgets（不驱动设备）。"""
    keys_plan = [str(s.get("writeKey") or "") for s in (plan.get("steps") or [])]
    keys_proc: List[str] = []
    for row in procedure_steps or []:
        if isinstance(row, dict):
            keys_proc.append(str(row.get("blocklyName") or row.get("writeKey") or ""))
    missing_in_proc = [k for k in keys_plan if k and k not in keys_proc]
    extra_in_proc = [k for k in keys_proc if k and k not in keys_plan]
    w = widgets if isinstance(widgets, dict) else {}
    widget_mismatches: List[str] = []
    for step in plan.get("widgetWrites") or []:
        key = str(step.get("writeKey") or "")
        if not key or key not in w:
            continue
        if str(w.get(key) or "") != str(step.get("value") or ""):
            widget_mismatches.append(key)
    return {
        "planStepCount": len(keys_plan),
        "procedureStepCount": len(keys_proc),
        "missingInProcedure": missing_in_proc[:40],
        "extraInProcedure": extra_in_proc[:40],
        "widgetMismatches": widget_mismatches[:40],
        "ovufSegmentOrder": list(plan.get("ovufSegmentOrder") or []),
    }


def _supports_interpret(test_type: str) -> bool:
    key = str(test_type or "").strip().lower().replace("-", "_")
    return key in ("ovuf", "guoqianya_pin", "volt_freq")


def try_run_blockly_interpret(
    *,
    ui: Any,
    test_type: str,
    params: Dict[str, Any],
    append_fn: Optional[Callable[[], None]],
    log: Optional[Callable[[str], None]] = None,
    apply_widget_values: Optional[Callable[[Any, Dict[str, Any]], List[str]]] = None,
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    尝试按积木解释执行 OVUF。

    返回 (handled, message, detail)：
    - handled=False：调用方应走原 Append
    - handled=True：已按积木路径处理（含回退 Append）
    """
    _log = log or (lambda _m: None)
    mode = normalize_execution_mode(
        (params or {}).get("executionMode") or (params or {}).get("execution_mode")
    )
    if mode != EXECUTION_BLOCKLY_INTERPRET:
        return False, "executionMode!=blockly_interpret", {}
    if not _supports_interpret(test_type):
        _log(f"blockly_interpret 暂不支持 testType={test_type}，回退 Append")
        return False, "unsupported_test_type", {"testType": test_type}

    code = str((params or {}).get("blocklyCode") or (params or {}).get("blockly_code") or "")
    proc = (params or {}).get("procedureSteps")
    plan = plan_from_blockly(
        code, procedure_steps=proc if isinstance(proc, list) else None
    )
    if not plan.get("steps"):
        fb = (params or {}).get("fallbackDialogAppend", True)
        msg = "积木步骤为空"
        _log(msg + ("，回退 Append" if fb else ""))
        if fb is False:
            return True, msg, {"plan": plan, "appended": False}
        return False, msg, {"plan": plan}

    detail: Dict[str, Any] = {"plan": plan, "mode": mode}
    try:
        missing = apply_widget_writes_from_plan(
            ui, plan, apply_widget_values=apply_widget_values
        )
        detail["missingWidgets"] = missing
        order = sync_ovuf_checkboxes_from_plan(ui, plan)
        detail["ovufSegmentOrder"] = order
        _log(
            f"blockly_interpret OVUF 计划 steps={plan.get('stepCount')} "
            f"segments={order} missing={len(missing)}"
        )

        if not append_fn:
            return True, "无 append 回调", {**detail, "appended": False}

        # 积木未声明任何 S3~S8 扫段字段：尊重 Dialog 勾选，整段 Append 一次
        # （勿把「Dialog 已勾选的段」拆成多次 Append，否则会改跑法）
        if not order:
            append_fn()
            detail["appended"] = True
            detail["segmentPasses"] = "dialog_checkboxes"
            return True, "ok_single_append", detail

        # 按积木段序逐段 Append（每段只勾选一个 checkBox），实现拖块改序
        saved = {}
        for sn in (3, 4, 5, 6, 7, 8):
            cb = getattr(ui, f"checkBox_S{sn}", None)
            saved[sn] = bool(cb.isChecked()) if cb is not None and hasattr(cb, "isChecked") else False

        sw = None
        try:
            import SCPITestWave as sw  # type: ignore  # 与 handoff 同进程
        except Exception:
            sw = None

        segs = list(order)
        for i, sn in enumerate(segs):
            for n in (3, 4, 5, 6, 7, 8):
                _set_checkbox(ui, f"checkBox_S{n}", n == sn)
            # 首段覆盖队列，后续追加
            if sw is not None:
                try:
                    sw.strAddTestFlag = "0" if i == 0 else "1"
                except Exception:
                    pass
            append_fn()
            _log(f"blockly_interpret 已追加扫段 S{sn} ({i + 1}/{len(segs)})")

        for sn, on in saved.items():
            _set_checkbox(ui, f"checkBox_S{sn}", on)

        detail["appended"] = True
        detail["segmentPasses"] = segs
        return True, "ok_segmented", detail
    except Exception as exc:
        fb = (params or {}).get("fallbackDialogAppend", True)
        _log(f"blockly_interpret 失败: {exc}")
        detail["error"] = str(exc)
        if fb is False:
            return True, f"interpret_failed:{exc}", {**detail, "appended": False}
        _log("blockly_interpret 失败，回退 Dialog Append")
        if append_fn:
            append_fn()
            detail["appended"] = True
            detail["fallback"] = True
            return True, "fallback_append", detail
        return True, f"interpret_failed:{exc}", detail


def format_plan_log_lines(plan: Dict[str, Any], *, limit: int = 40) -> List[str]:
    lines = [
        f"blockly plan steps={plan.get('stepCount')} "
        f"ovufSegments={plan.get('ovufSegmentOrder')}"
    ]
    for i, st in enumerate((plan.get("steps") or [])[:limit]):
        lines.append(
            f"  [{i + 1}] {st.get('writeKey')}={st.get('value')}"
            f"{('^' + st['unit']) if st.get('unit') else ''}"
        )
    return lines
