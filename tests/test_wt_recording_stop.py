# -*- coding: utf-8 -*-
from utils.wt_recording_stop import decide_wt_recording_stop


def test_single_file_one_project_is_all_done():
    assert (
        decide_wt_recording_stop(
            count_now=0, total_save_file=1, name_count=1, program_count=1
        )
        == "all_done"
    )


def test_multi_file_same_project_advances():
    assert (
        decide_wt_recording_stop(
            count_now=0, total_save_file=3, name_count=3, program_count=1
        )
        == "next_file"
    )
    assert (
        decide_wt_recording_stop(
            count_now=2, total_save_file=3, name_count=3, program_count=1
        )
        == "all_done"
    )


def test_filename_list_shorter_than_planned_saves_hands_off_next_project():
    """静态 QU 录完时文件名被收成 1 个，但后面还有动态 QU。"""
    assert (
        decide_wt_recording_stop(
            count_now=0, total_save_file=2, name_count=1, program_count=2
        )
        == "project_done"
    )


def test_last_save_of_multi_project_is_all_done():
    assert (
        decide_wt_recording_stop(
            count_now=1, total_save_file=2, name_count=2, program_count=2
        )
        == "all_done"
    )


def test_one_name_but_no_extra_project_still_finishes():
    """total_save_file 残留大于文件名个数、且没有下一项时，仍按整单结束。"""
    assert (
        decide_wt_recording_stop(
            count_now=0, total_save_file=2, name_count=1, program_count=1
        )
        == "all_done"
    )
