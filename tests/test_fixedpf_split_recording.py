# -*- coding: utf-8 -*-
"""固定 PF 分开录：停止时间对齐数据采集，各档文件不互相覆盖。"""

from utils.wt_acquire_mode import resolve_csv_path, scpi_file_slot
from utils.wt_recording_mode import (
    MODE_CONTINUOUS,
    MODE_SPLIT,
    align_fixed_pf_recording,
    fixed_pf_recommended_filenames,
    fixed_pf_stop_seconds,
    stoptime_str_from_seconds,
)


def _config_row(names, stop="00:05:00"):
    return [
        "Upper_WT_Config",
        "",
        "",
        "config_dict",
        {
            "textEdit_FileNameList": ",".join(names),
            "textEdit_StopTime": stop,
            "comboBox_AutoSave": 0,
        },
    ]


def test_split_stop_is_collect_not_panel_default():
    # 2 分钟 = 1200 个 0.1 秒
    assert fixed_pf_stop_seconds(1200, 10, 5, continuous=False) == 120
    assert stoptime_str_from_seconds(120) == "00:02:00"


def test_continuous_stop_sums_every_point():
    # 2 档：每档等待 1 秒 + 采集 2 分钟
    assert fixed_pf_stop_seconds(1200, 10, 2, continuous=True) == 242


def test_align_split_rewrites_stop_and_keeps_distinct_files():
    names = fixed_pf_recommended_filenames([100, 75], MODE_SPLIT)
    cmds = [_config_row([n + "_151827" for n in names], stop="00:05:00")]
    text, stop = align_fixed_pf_recording(
        cmds, [100, 75], MODE_SPLIT, 1200, 10, n_points=2
    )
    assert stop == "00:02:00"
    assert text == "FixedPF_P100_151827,FixedPF_P75_151827"
    assert cmds[0][4]["textEdit_StopTime"] == "00:02:00"


def test_align_replaces_single_name_when_mode_is_split():
    cmds = [_config_row(["FixedPF_BR_151827"], stop="00:05:00")]
    text, stop = align_fixed_pf_recording(
        cmds, [100, 75, 50], MODE_SPLIT, 1200, 10, n_points=3
    )
    assert stop == "00:02:00"
    assert text.split(",") == [
        "FixedPF_P100_151827",
        "FixedPF_P75_151827",
        "FixedPF_P50_151827",
    ]


def test_duplicate_power_points_do_not_share_a_filename():
    names = fixed_pf_recommended_filenames([100, 100], MODE_SPLIT)
    assert names == ["FixedPF_P100", "FixedPF_P100_2"]


def test_scpi_slot_advances_after_filename_is_remembered():
    cfg = {
        "textEdit_SavePath": "",
        "textEdit_FileNameList": "FixedPF_P100_151827,FixedPF_P75_151827",
    }
    now = 0
    save_name = ""
    idx, name = scpi_file_slot(cfg, now)
    assert (idx, name) == (0, "FixedPF_P100_151827")
    save_name = name
    if not (now == 0 and save_name == ""):
        now = now + 1
    idx2, name2 = scpi_file_slot(cfg, now)
    assert (idx2, name2) == (1, "FixedPF_P75_151827")
    assert resolve_csv_path(cfg, idx2).endswith("FixedPF_P75_151827.csv")


def test_continuous_stop_uses_point_count_not_single_filename():
    cmds = [_config_row(["FixedPF_BR_151827"])]
    _text, stop = align_fixed_pf_recording(
        cmds, [100, 75], MODE_CONTINUOUS, 1200, 10, n_points=2
    )
    assert stop == "00:04:02"
    assert cmds[0][4]["textEdit_FileNameList"] == "FixedPF_BR_151827"
