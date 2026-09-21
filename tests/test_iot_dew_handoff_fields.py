# -*- coding: utf-8 -*-
"""桌面 handoff：dew_export_fields / radio_dewetron 写入逻辑（无 Qt）。"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any, List


def _apply_dew_export_like_handoff(real_ui: Any, widgets: dict) -> List[str]:
    """镜像 utils/iot_ui_handoff.py 德威创导出字段写入分支。"""
    logs: List[str] = []
    raw_fields = widgets.get("dew_export_fields")
    if raw_fields is not None and hasattr(real_ui, "set_checked_export_fields"):
        if isinstance(raw_fields, str):
            field_list = [
                x.strip() for x in raw_fields.replace("，", ",").split(",") if x.strip()
            ]
        elif isinstance(raw_fields, (list, tuple)):
            field_list = [str(x).strip() for x in raw_fields if str(x).strip()]
        else:
            field_list = []
        if field_list:
            real_ui.set_checked_export_fields(field_list)
            logs.append(f"wrote:{len(field_list)}")
    if widgets.get("radio_dewetron") in (True, "1", 1, "true", "True"):
        radio = getattr(real_ui, "radio_dewetron", None)
        if radio is not None and hasattr(radio, "setChecked"):
            radio.setChecked(True)
            logs.append("dewetron_on")
    return logs


def test_handoff_writes_export_fields_and_toggles_radio():
    checked: List[str] = []
    radio_state = {"on": False}

    def set_checked_export_fields(fields):
        checked.clear()
        checked.extend(fields)

    radio = SimpleNamespace(
        setChecked=lambda v: radio_state.__setitem__("on", bool(v)),
        click=lambda: None,
    )
    ui = SimpleNamespace(
        set_checked_export_fields=set_checked_export_fields,
        radio_dewetron=radio,
    )
    logs = _apply_dew_export_like_handoff(
        ui,
        {
            "radio_dewetron": True,
            "dew_export_fields": ["U1_tRMS", "I1_tRMS", "Freq"],
        },
    )
    assert checked == ["U1_tRMS", "I1_tRMS", "Freq"]
    assert radio_state["on"] is True
    assert "wrote:3" in logs
    assert "dewetron_on" in logs


def test_handoff_accepts_comma_string_fields():
    checked: List[str] = []
    ui = SimpleNamespace(
        set_checked_export_fields=lambda fields: checked.extend(fields),
        radio_dewetron=None,
    )
    _apply_dew_export_like_handoff(
        ui, {"dew_export_fields": "U1_tRMS, I2_tRMS，P_sum"}
    )
    assert checked == ["U1_tRMS", "I2_tRMS", "P_sum"]
