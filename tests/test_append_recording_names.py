# -*- coding: utf-8 -*-
from utils.wt_recording_mode import (
    apply_run_tag,
    collect_progress_file_names,
    finalize_append_file_names,
    should_merge_append_filenames,
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


def test_should_merge_append_filenames_same_vs_cross_project():
    """同项追加才 merge；跨项 project_change=1 禁止把上一项文件名拼进来。"""
    assert should_merge_append_filenames("1", "0") is True
    assert should_merge_append_filenames("1", "1") is False
    assert should_merge_append_filenames("0", "0") is False
    assert should_merge_append_filenames("0", "1") is False


def test_cross_project_finalize_does_not_merge_when_is_append_false():
    cmds = [["Upper_WT_Config", "", "", "", {"textEdit_FileNameList": "Harmonic_BR_111111"}]]
    # 跨项：调用方应传 is_append=False（与 should_merge_append_filenames 一致）
    out = finalize_append_file_names(
        ["OVUF_BR"], cmds, is_append=False, run_tag="222222"
    )
    assert out == ["OVUF_BR_222222"]
    assert "Harmonic_BR_111111" not in out


def test_should_refresh_on_same_project_append():
    assert should_refresh_wt_config("0", "0") is True
    assert should_refresh_wt_config("1", "0") is True
    assert should_refresh_wt_config("1", "1") is True


def test_collect_progress_prefers_all_queue_segments_over_config_dict():
    """跨项：config_dict 只有末项时，仍须拼齐队列里多段 FileNameList。"""
    cmds = [
        ["Upper_WT_Config", "", "", "", {"textEdit_FileNameList": "Harmonic_BR_1"}],
        ["QUEUE", "end_test", "谐波电流"],
        ["Upper_WT_Config", "", "", "", {"textEdit_FileNameList": "OVUF_P1_2,OVUF_P2_2"}],
    ]
    cfg = {"textEdit_FileNameList": "OVUF_P1_2,OVUF_P2_2"}
    assert collect_progress_file_names(cmds, cfg) == [
        "Harmonic_BR_1",
        "OVUF_P1_2",
        "OVUF_P2_2",
    ]


def test_collect_progress_falls_back_to_config_when_queue_empty():
    assert collect_progress_file_names([], {"textEdit_FileNameList": "A,B"}) == ["A", "B"]
