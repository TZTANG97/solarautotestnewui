# -*- coding: utf-8 -*-
"""软件急停：强制关输出 → 中止试验，顺序可测。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from utils.iot_software_estop import (
    ESTOP_FAIL_REASON_ZH,
    ESTOP_LOG_ZH,
    estop_software,
)


def test_estop_software_calls_force_off_then_end_project():
    order = []

    def force_off():
        order.append("force_off")

    def end_project():
        order.append("end_project")

    logs = []
    estop_software(
        force_off=force_off,
        end_project=end_project,
        log=logs.append,
    )
    assert order == ["force_off", "end_project"]
    assert logs == [ESTOP_LOG_ZH]
    assert "直流先关" in ESTOP_LOG_ZH
    assert "急停" in ESTOP_LOG_ZH


def test_estop_software_notify_handoff_after_end():
    order = []

    estop_software(
        force_off=lambda: order.append("force_off"),
        end_project=lambda: order.append("end_project"),
        notify_handoff=lambda: order.append("handoff"),
        log=lambda m: order.append(m),
    )
    assert order[:3] == ["force_off", "end_project", "handoff"]
    assert order[3] == ESTOP_LOG_ZH


def test_estop_fail_reason_chinese():
    assert ESTOP_FAIL_REASON_ZH == "软件急停"
