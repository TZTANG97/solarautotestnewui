# -*- coding: utf-8 -*-
from utils.wt_recording_mode import (
    apply_run_tag,
    finalize_append_file_names,
    should_refresh_wt_config,
)


def test_apply_run_tag():
    assert apply_run_tag(["Overload_BR"], "120001") == ["Overload_BR_120001"]
    assert apply_run_tag(["A", "B"], "") == ["A", "B"]


def test_finalize_append_merges_previous():
    first = finalize_append_file_names(["AntiBackflow_BR"], None, is_append=False, run_tag="111111")
    assert first == ["AntiBackflow_BR_111111"]
    cmds = [["Upper_WT_Config", "", "", "", {"textEdit_FileNameList": "AntiBackflow_BR_111111"}]]
    second = finalize_append_file_names(
        ["AntiBackflow_BR"], cmds, is_append=True, run_tag="222222"
    )
    assert second == ["AntiBackflow_BR_111111", "AntiBackflow_BR_222222"]


def test_should_refresh_on_same_project_append():
    assert should_refresh_wt_config("0", "0") is True
    assert should_refresh_wt_config("1", "0") is True
    assert should_refresh_wt_config("1", "1") is True
