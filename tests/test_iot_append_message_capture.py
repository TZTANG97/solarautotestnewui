# -*- coding: utf-8 -*-
"""IOT 追加：information 弹窗一律视为失败（含 cosφ 未勾）。"""

from PyQt5.QtWidgets import QMessageBox

from utils.iot_ui_handoff import _append_with_message_capture
from utils.iot_reactiveqcap_standard import ensure_reactiveqcap_capability_widgets


def test_append_capture_cos_missing_is_failure():
    def _append():
        QMessageBox.information(
            None,
            "错误提示信息",
            "无功能力范围 请至少勾选一个极限 cosφ",
        )

    fail_msg, err = _append_with_message_capture(_append)
    assert err is None
    assert fail_msg and "cosφ" in fail_msg


def test_ensure_reactiveqcap_fills_default_cos():
    out = ensure_reactiveqcap_capability_widgets(
        {"checkBox_S3": False, "checkBox_cos_pos09": False, "checkBox_cos_neg09": False}
    )
    assert out["checkBox_S3"] is True
    assert out["checkBox_cos_pos09"] is True
    assert out["checkBox_cos_neg09"] is True
