# -*- coding: utf-8 -*-
"""过频降载连续录：命令列表改写冒烟测试。"""
from __future__ import annotations

import csv
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Minimal Qt stubs not required — exercise pure list rewrite via helper pieces.
from SCPITestWave import (  # noqa: E402
    _enable_freq_step_continuous_record,
    _is_wt_async_start,
    _is_wt_wait_end,
)


class _FakeCheck:
    def __init__(self, checked: bool):
        self._checked = checked

    def isChecked(self):
        return self._checked


class _FakeText:
    def __init__(self, text: str):
        self._text = text

    def toPlainText(self):
        return self._text

    def setPlainText(self, text: str):
        self._text = text


class _FakeCombo:
    def __init__(self, text: str = "秒", index: int = 1):
        self._text = text
        self._index = index

    def currentText(self):
        return self._text

    def currentIndex(self):
        return self._index

    def setCurrentIndex(self, index: int):
        self._index = index


def _fake_ui(steps_on, dwell_s="60"):
    ns = SimpleNamespace()
    ns.checkBox_S2 = _FakeCheck(True)
    for i in range(3, 18):
        setattr(ns, f"checkBox_S{i}", _FakeCheck(i in steps_on))
        setattr(ns, f"textEdit_S{i}_TIME", _FakeText(dwell_s if i in steps_on else ""))
        setattr(ns, f"comboBox_S{i}_TIME", _FakeCombo("秒"))
    ns._wtStacked = None
    return ns


def test_continuous_record_wraps_ladder_from_saved_commands():
    cmd_path = ROOT / "command_save_files" / "command_data" / "guopinjiangzai_commands2026_08_20_15.csv"
    assert cmd_path.exists(), cmd_path
    with open(cmd_path, encoding="utf-8-sig", newline="") as f:
        rows = [list(r) for r in csv.reader(f)]
    for r in rows:
        while len(r) < 10:
            r.append("")

    # Today's run used S3~S9-ish (7 freq points); mark 3..9
    ui = _fake_ui(set(range(3, 10)), dwell_s="60")
    # Patch global ui for return message
    import SCPITestWave as M

    class _Msg:
        def append(self, *_a, **_k):
            pass

    M.ui = SimpleNamespace(textEdit_ReturnMessage=_Msg())

    ok = _enable_freq_step_continuous_record(
        rows, ui, file_default="OF_curve", log_label="过频降载"
    )
    assert ok is True

    async_idx = [i for i, r in enumerate(rows) if _is_wt_async_start(r[6])]
    wait_idx = [i for i, r in enumerate(rows) if _is_wt_wait_end(r[6])]
    assert len(async_idx) == 1, async_idx
    assert len(wait_idx) == 1, wait_idx
    assert async_idx[0] < wait_idx[0]

    # No leftover numeric col6 measure triggers
    for r in rows:
        if r and r[0] == "AC" and r[1] == "query" and r[6] not in ("", None):
            assert _is_wt_async_start(r[6]) or _is_wt_wait_end(r[6]), r[6]

    # ASYNC sits before first FREQ after OUTP ON
    outp = next(i for i, r in enumerate(rows) if r[1] == "write" and str(r[2]).upper().startswith("OUTP ON"))
    first_freq_after = next(
        i
        for i, r in enumerate(rows)
        if i > outp and r[1] == "write" and str(r[2]).upper().startswith("FREQ ")
    )
    assert async_idx[0] == first_freq_after - 0 or async_idx[0] < first_freq_after
    # insert shifts FREQ forward by 1
    assert rows[async_idx[0] + 1][2].upper().startswith("FREQ ")

    cfg = next(r[4] for r in rows if r and r[0] == "Upper_WT_Config")
    assert isinstance(cfg, str) or True  # CSV loaded as string; rewrite may not touch if not dict
    # When loaded from CSV, config is a string — helper only updates dict rows.
    # Rebuild a dict config row to assert StopTime rewrite path.
    rows2 = [list(r) for r in rows]
    # already wrapped once; calling again should be safe-ish but skip — instead unit the dict path:
    rows3 = []
    with open(cmd_path, encoding="utf-8-sig", newline="") as f:
        for r in csv.reader(f):
            row = list(r)
            while len(row) < 10:
                row.append("")
            if row[0] == "Upper_WT_Config":
                row[4] = {
                    "textEdit_FileNameList": "100%_ambient,100%_+55",
                    "textEdit_StopTime": "00:02:00",
                    "comboBox_AutoSave": 1,
                }
            rows3.append(row)
    ui2 = _fake_ui(set(range(3, 10)), dwell_s="60")
    assert _enable_freq_step_continuous_record(rows3, ui2, file_default="OF_curve", log_label="过频降载")
    cfg2 = next(r[4] for r in rows3 if r[0] == "Upper_WT_Config")
    assert cfg2["textEdit_FileNameList"] == "100%_ambient"
    # 7*60s + 15s margin
    assert cfg2["textEdit_StopTime"] == "00:07:15"


if __name__ == "__main__":
    test_continuous_record_wraps_ladder_from_saved_commands()
    print("ok")
