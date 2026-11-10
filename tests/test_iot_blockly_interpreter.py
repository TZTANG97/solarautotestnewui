# -*- coding: utf-8 -*-
"""光伏 Blockly 解释器：解析保序、扫段启用、默认不进 interpret。"""
from utils.iot_blockly_interpreter import (
    EXECUTION_BLOCKLY_INTERPRET,
    EXECUTION_DIALOG_APPEND,
    normalize_execution_mode,
    ovuf_segment_order_from_steps,
    parse_blockly_write_steps,
    plan_from_blockly,
    shadow_compare_plan,
    sync_ovuf_checkboxes_from_plan,
    try_run_blockly_interpret,
)


SAMPLE_CODE = """
ldw^control^start;
EQID^AC1,write^VOLT^230^;
EQID^AC1,write^FREQ^50^;
EQID^DC1,write^Vmp^750^;
EQID^B1,write^textEdit_S1_TIME^2^min;
EQID^B1,write^textEdit_ovuf_grid_wait^5^s;
EQID^AC1,write^textEdit_S3_AC_VOLT_Start^230^;
EQID^AC1,write^textEdit_S3_AC_VOLT_End^255^;
EQID^AC1,write^textEdit_S5_AC_FR_Start^50^;
EQID^AC1,write^textEdit_S5_AC_FR_End^51.5^;
EQID^AC1,write^textEdit_S4_AC_VOLT_Start^230^;
EQID^AC1,write^textEdit_S4_AC_VOLT_End^182^;
EQID^B1,write^solar_guoqianya_pin^;
ldw^control^stop;
"""


def test_normalize_default_append():
    assert normalize_execution_mode(None) == EXECUTION_DIALOG_APPEND
    assert normalize_execution_mode("blockly_interpret") == EXECUTION_BLOCKLY_INTERPRET


def test_parse_preserves_order_and_skips_empty():
    steps = parse_blockly_write_steps(SAMPLE_CODE)
    keys = [s["writeKey"] for s in steps]
    assert keys[0] == "VOLT"
    assert "textEdit_S3_AC_VOLT_Start" in keys
    assert "textEdit_S5_AC_FR_Start" in keys
    assert "textEdit_S4_AC_VOLT_Start" in keys
    # 过压 → 过频 → 欠压（积木顺序，非自然 3,4,5）
    i3 = keys.index("textEdit_S3_AC_VOLT_Start")
    i5 = keys.index("textEdit_S5_AC_FR_Start")
    i4 = keys.index("textEdit_S4_AC_VOLT_Start")
    assert i3 < i5 < i4


def test_ovuf_segment_order_follows_blockly_not_natural():
    plan = plan_from_blockly(SAMPLE_CODE)
    assert plan["ovufSegmentOrder"] == [3, 5, 4]


def test_ovuf_segment_order_omits_deleted_scan():
    # 无 S5 字段 → 不含 5
    code = """
EQID^AC1,write^textEdit_S3_AC_VOLT_Start^230^;
EQID^AC1,write^textEdit_S4_AC_VOLT_End^182^;
"""
    assert ovuf_segment_order_from_steps(parse_blockly_write_steps(code)) == [3, 4]


class _FakeCb:
    def __init__(self, on=False):
        self._on = on

    def isChecked(self):
        return self._on

    def setChecked(self, v):
        self._on = bool(v)


class _FakeUi:
    def __init__(self):
        for sn in (3, 4, 5, 6, 7, 8):
            setattr(self, f"checkBox_S{sn}", _FakeCb(True))


def test_sync_checkboxes_disables_missing_segments():
    ui = _FakeUi()
    plan = plan_from_blockly(SAMPLE_CODE)
    order = sync_ovuf_checkboxes_from_plan(ui, plan)
    assert order == [3, 5, 4]
    assert ui.checkBox_S3.isChecked()
    assert ui.checkBox_S5.isChecked()
    assert ui.checkBox_S4.isChecked()
    assert not ui.checkBox_S6.isChecked()
    assert getattr(ui, "_iot_blockly_segment_order") == [3, 5, 4]


def test_try_run_skips_when_default_mode():
    calls = []
    handled, msg, _ = try_run_blockly_interpret(
        ui=_FakeUi(),
        test_type="ovuf",
        params={"executionMode": "dialog_append", "blocklyCode": SAMPLE_CODE},
        append_fn=lambda: calls.append(1),
    )
    assert handled is False
    assert calls == []


def test_try_run_segmented_append_in_blockly_order():
    ui = _FakeUi()
    passes = []

    def append_fn():
        on = [sn for sn in (3, 4, 5, 6, 7, 8) if getattr(ui, f"checkBox_S{sn}").isChecked()]
        passes.append(on)

    handled, msg, detail = try_run_blockly_interpret(
        ui=ui,
        test_type="ovuf",
        params={
            "executionMode": "blockly_interpret",
            "blocklyCode": SAMPLE_CODE,
            "fallbackDialogAppend": True,
        },
        append_fn=append_fn,
        apply_widget_values=lambda _ui, _w: [],
    )
    assert handled is True
    assert detail.get("appended") is True
    assert passes == [[3], [5], [4]]
    assert msg.startswith("ok_")


def test_shadow_compare_reports_segment_order():
    plan = plan_from_blockly(SAMPLE_CODE)
    cmp_ = shadow_compare_plan(plan, procedure_steps=[], widgets={})
    assert cmp_["ovufSegmentOrder"] == [3, 5, 4]
    assert cmp_["planStepCount"] > 0


def test_sync_empty_order_keeps_dialog_checkboxes():
    ui = _FakeUi()
    # 全部勾选后，空 order 不得清掉
    order = sync_ovuf_checkboxes_from_plan(ui, {"ovufSegmentOrder": []})
    assert order == []
    assert all(getattr(ui, f"checkBox_S{sn}").isChecked() for sn in (3, 4, 5, 6, 7, 8))


def test_interpret_without_scan_fields_single_append():
    """真实实验常见：积木只有主块/等待，无 S3~S8 → 整段一次 Append。"""
    ui = _FakeUi()
    passes = []

    def append_fn():
        on = [sn for sn in (3, 4, 5, 6, 7, 8) if getattr(ui, f"checkBox_S{sn}").isChecked()]
        passes.append(on)

    code = """
EQID^DC1,write^Vmp^750^;
EQID^B1,write^textEdit_ovuf_grid_wait^5^s;
EQID^B1,write^solar_guoqianya_pin^;
"""
    handled, msg, detail = try_run_blockly_interpret(
        ui=ui,
        test_type="ovuf",
        params={"executionMode": "blockly_interpret", "blocklyCode": code},
        append_fn=append_fn,
        apply_widget_values=lambda *_a, **_k: [],
    )
    assert handled is True
    assert msg == "ok_single_append"
    assert detail.get("segmentPasses") == "dialog_checkboxes"
    assert len(passes) == 1
    assert passes[0] == [3, 4, 5, 6, 7, 8]
