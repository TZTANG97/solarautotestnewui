# -*- coding: utf-8 -*-
from utils.iot_device_cmd_inbox import execute_device_cmd


def test_apply_setpoints_calls_callback_with_widgets():
    seen = {}

    def apply_setpoints(instrument, widgets):
        seen["instrument"] = instrument
        seen["widgets"] = widgets
        return {"ok": True, "message": "ac 参数已下发"}

    result = execute_device_cmd(
        {
            "action": "apply_setpoints",
            "instrument": {"slot": "ac", "kind": "ac", "brand": "itech"},
            "widgets": {"comboBox_Phase": "三相", "textEdit_AC_VOLT": "230"},
        },
        apply_setpoints=apply_setpoints,
    )
    assert result["ok"] is True
    assert seen["instrument"]["slot"] == "ac"
    assert seen["widgets"]["comboBox_Phase"] == "三相"
    assert seen["widgets"]["_iot_brand"] == "itech"


def test_apply_setpoints_without_callback():
    result = execute_device_cmd(
        {"action": "apply_setpoints", "instrument": {"slot": "ac"}, "widgets": {}},
    )
    assert result["ok"] is False
    assert "未注册" in result["message"]
