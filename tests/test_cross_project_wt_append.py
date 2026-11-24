# -*- coding: utf-8 -*-
"""跨项目追加：上一项结束(GAP) → 下一项像单独开测一样重配。"""
from utils.wt_recording_mode import (
    advance_test_program_after_project_gap,
    insert_project_gap_before_last_wt_config,
    last_upper_wt_config_row,
    make_project_gap_row,
    patch_last_upper_wt_config,
    previous_wt_filename_list,
)
from utils.wt_recording_stop import decide_wt_recording_stop


def test_make_project_gap_row_is_explicit():
    row = make_project_gap_row(20)
    assert row[0] == "AC"
    assert row[1] == "wait"
    assert row[2] == "PROJECT_GAP"
    assert row[9] == 20


def test_insert_gap_before_last_wt_config_order():
    """队列必须是 GAP 在本项 Upper_WT_Config 之前。"""
    cmds = [
        ["Upper_WT_Config", "", "", "", {"textEdit_FileNameList": "OVUF_BR"}],
        ["Upper_WT_Config", "", "", "", {"textEdit_FileNameList": "FixedPF"}],
    ]
    out = insert_project_gap_before_last_wt_config(cmds)
    assert out[0][4]["textEdit_FileNameList"] == "OVUF_BR"
    assert out[1][2] == "PROJECT_GAP"
    assert out[2][4]["textEdit_FileNameList"] == "FixedPF"
    # 幂等
    out2 = insert_project_gap_before_last_wt_config(out)
    assert len(out2) == len(out)


def test_patch_last_upper_wt_config_does_not_touch_first_project():
    cmds = [
        ["Upper_WT_Config", "", "", "", {"textEdit_FileNameList": "OVUF_BR_111111", "comboBox_AutoSave": 1}],
        ["AC", "wait", "PROJECT_GAP", "", "", "", "", "", "", 20],
        ["Upper_WT_Config", "", "", "", {"textEdit_FileNameList": "", "comboBox_AutoSave": 0}],
    ]
    patch_last_upper_wt_config(
        cmds,
        file_list_text="FixedPF_P100_222222",
        stop_time="00:05:00",
    )
    assert cmds[0][4]["textEdit_FileNameList"] == "OVUF_BR_111111"
    assert cmds[2][4]["textEdit_FileNameList"] == "FixedPF_P100_222222"
    assert cmds[2][4]["textEdit_StopTime"] == "00:05:00"
    assert cmds[2][4]["comboBox_AutoSave"] == 1
    assert previous_wt_filename_list(cmds) == ["FixedPF_P100_222222"]
    assert last_upper_wt_config_row(cmds) is cmds[2]


def test_advance_test_program_after_project_gap_pops_finished():
    prog = [["7", "WT5000"], ["8", "WT5000"]]
    next_prog, now_save, total_save, advanced = advance_test_program_after_project_gap(
        prog, now_save_file=3, total_save_file=5
    )
    assert advanced is True
    assert next_prog == [["8", "WT5000"]]
    assert now_save == 0
    assert total_save == 2


def test_ovuf_then_fixedpf_stop_decision_is_project_done():
    """过欠压录完、后面还有固定 PF：必须 project_done，不能 all_done。"""
    assert (
        decide_wt_recording_stop(
            count_now=0, total_save_file=2, name_count=1, program_count=2
        )
        == "project_done"
    )
