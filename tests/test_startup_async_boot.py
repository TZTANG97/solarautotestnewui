# -*- coding: utf-8 -*-
"""Startup must not require sync VISA RM before helpers are callable."""
from __future__ import annotations


def test_visa_rm_boot_helpers_exist():
    import SCPITestWave as m

    assert callable(m._start_visa_rm_boot)
    assert callable(m._wait_visa_rm_boot)
    assert callable(m._schedule_startup_auto_connect)
    assert callable(m._run_startup_connect_jobs_stepwise)
    assert "done" in m._VISA_RM_BOOT


def test_stepwise_empty_jobs_no_crash(qtbot=None):
    import SCPITestWave as m

    class _T:
        def append(self, _msg):
            pass

    class _U:
        textEdit_ReturnMessage = _T()

    m.ui = _U()
    m._run_startup_connect_jobs_stepwise([], [])
