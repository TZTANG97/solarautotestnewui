# -*- coding: utf-8 -*-
"""WT 自动化门闩：试验结束后换项追加应能 reset。"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def sw_module():
    import SCPITestWave as sw

    return importlib.reload(sw)


def test_reset_allowed_after_run_finished_but_flag_still_running(sw_module):
    sw = sw_module
    sw.strTestStatusFlag = "运行"
    sw.strTestFlag = "0"
    sw.strArrayTest = []
    sw.first_test = "1"
    sw.setting_status = "1"
    sw.messure_status = "1"

    sw.reset_wt_automation_state()

    assert sw.first_test == ""
    assert sw.setting_status == ""
    assert sw.messure_status == ""


def test_reset_blocked_while_commands_pending(sw_module):
    sw = sw_module
    sw.strTestStatusFlag = "运行"
    sw.strTestFlag = "0"
    sw.strArrayTest = [["AC", "write", "OUTP ON"] + [""] * 7]
    sw.first_test = "1"

    sw.reset_wt_automation_state()

    assert sw.first_test == "1"


def test_reset_blocked_while_start_pending(sw_module):
    sw = sw_module
    sw.strTestStatusFlag = "运行"
    sw.strTestFlag = "1"
    sw.strArrayTest = []
    sw.first_test = "1"

    sw.reset_wt_automation_state()

    assert sw.first_test == "1"
