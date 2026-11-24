# -*- coding: utf-8 -*-
"""德威创开跑门闩：队列有 DEWETRON 就必须 prepare，错误信息要可区分。"""

from utils.active_project_resolve import (
    collect_handoff_project_candidates,
    is_plausible_desktop_project_name,
    pick_active_project_name,
)
from utils.dewetron_recording import command_queue_has_dewetron


def test_command_queue_has_dewetron_detects_start_stop():
    assert not command_queue_has_dewetron([])
    assert not command_queue_has_dewetron([["AC", "write", "OUTP ON"]])
    assert command_queue_has_dewetron(
        [["AC", "wait", "*IDN?"], ["DEWETRON", "write", ":ACQUISITION:START"]]
    )


def test_start_gathering_reports_missing_prepare_not_wt(tmp_path):
    from devices.dewetron_data_collector import DewetronDataCollector

    class _Ctrl:
        connected = True

        def query_command(self, *a, **k):
            return None

        def send_command(self, *a, **k):
            return True

    class _Log:
        def info(self, *a, **k):
            return None

    collector = DewetronDataCollector(_Ctrl(), _Log(), db_path=str(tmp_path / "dew.db"))
    assert not collector.start_gathering()
    err = collector._last_gather_error or ""
    assert "未 prepare" in err
    assert "Soft Panel" in err


def test_pick_active_project_from_handoff_when_combo_empty():
    def _resolve(token):
        if token == "solar_reactive_qcap":
            return {"project_name": "无功能力范围", "key": token}
        return None

    name = pick_active_project_name(
        ["", None, "solar_reactive_qcap"],
        resolve_handler=_resolve,
        is_known=lambda n: n == "无功能力范围",
    )
    assert name == "无功能力范围"


def test_pick_active_project_fallback_chinese_even_if_unknown():
    name = pick_active_project_name(
        ["", "无功能力范围"],
        is_known=lambda _n: False,
    )
    assert name == "无功能力范围"
    assert is_plausible_desktop_project_name("无功能力范围")
    assert not is_plausible_desktop_project_name("solar_reactive_qcap")


def test_collect_handoff_candidates_from_awaiting_handler():
    class _Svc:
        _job_ctx = None
        _awaiting = {
            "test_type": "solar_reactive_qcap",
            "handler": {"project_name": "无功能力范围", "key": "solar_reactive_qcap"},
        }

    got = collect_handoff_project_candidates(_Svc())
    assert "无功能力范围" in got
    assert "solar_reactive_qcap" in got
