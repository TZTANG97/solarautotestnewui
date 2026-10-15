# -*- coding: utf-8 -*-
"""本地开测上报：Dialog widgets 补全 + 本机实际命令序列快照。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence


def enrich_widgets_for_upload(widgets: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """空 AC 电压/频率用德威创额定或加权类型回填，避免云端 Blockly 与本机工况脱节。"""
    w = dict(widgets or {}) if isinstance(widgets, dict) else {}
    volt = str(w.get("textEdit_S1_AC_VOLT") or "").strip()
    if not volt:
        nom = str(w.get("textEdit_DEW_NominalVoltage") or "").strip()
        if nom:
            w["textEdit_S1_AC_VOLT"] = nom
    freq = str(w.get("textEdit_S1_AC_FR") or "").strip()
    if not freq:
        weighting = str(w.get("comboBox_DEW_WeightingType") or "")
        if "60Hz" in weighting.replace(" ", "") or "/60" in weighting:
            w["textEdit_S1_AC_FR"] = "60"
        elif "50Hz" in weighting.replace(" ", "") or "/50" in weighting:
            w["textEdit_S1_AC_FR"] = "50"
        elif str(w.get("textEdit_DEW_NominalVoltage") or "").strip():
            # 有额定电压时至少给 50，与经典 Blockly 默认一致
            w["textEdit_S1_AC_FR"] = "50"
    return w


def snapshot_run_commands(rows: Optional[Sequence[Any]]) -> List[Dict[str, Any]]:
    """把 strArrayTest 压成可 JSON 上报的本机实际步骤。"""
    out: List[Dict[str, Any]] = []
    if not rows:
        return out
    for i, row in enumerate(rows):
        if not isinstance(row, (list, tuple)) or not row:
            continue
        device = str(row[0] if len(row) > 0 else "")
        action = str(row[1] if len(row) > 1 else "")
        command = str(row[2] if len(row) > 2 else "")
        # 空行或纯占位跳过
        if not device and not command:
            continue
        item: Dict[str, Any] = {
            "index": i + 1,
            "device": device,
            "action": action,
            "command": command,
        }
        if len(row) > 6 and row[6] not in (None, ""):
            item["flag"] = row[6]
        if len(row) > 8 and row[8] not in (None, ""):
            item["wait01"] = row[8]
        if len(row) > 9 and row[9] not in (None, ""):
            item["wait01b"] = row[9]
        out.append(item)
    return out


def procedure_steps_from_run_commands(
    commands: Optional[Sequence[Dict[str, Any]]],
) -> List[Dict[str, str]]:
    """本机 runCommands → job.procedureSteps 轻量展示。"""
    steps: List[Dict[str, str]] = []
    if not commands:
        return steps
    for i, c in enumerate(commands):
        if not isinstance(c, dict):
            continue
        device = str(c.get("device") or "")
        action = str(c.get("action") or "")
        command = str(c.get("command") or "")
        label = f"{device} {action}".strip() or "step"
        steps.append(
            {
                "index": str(c.get("index") or (i + 1)),
                "blocklyName": action or device or f"step{i+1}",
                "label": label[:64],
                "equId": device,
                "value": command[:200],
                "unit": "",
            }
        )
    return steps
