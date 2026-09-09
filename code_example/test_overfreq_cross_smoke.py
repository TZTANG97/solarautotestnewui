# -*- coding: utf-8 -*-
"""过频降载交叉扫频冒烟：list 往返 + 连续录改写。"""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from utils.overfreq_ladder_commands import (  # noqa: E402
    append_freq_ladder_commands,
    collect_freq_points_with_per_step_dwell,
    parse_freq_hz_list,
    sync_freq_list_to_legacy_cards,
)
from utils.time_helpers import SetTimeFunction  # noqa: E402


class _FakeCheck:
    def __init__(self, checked=True):
        self._c = checked

    def isChecked(self):
        return self._c

    def setChecked(self, v):
        self._c = bool(v)


class _FakeText:
    def __init__(self, text=""):
        self._t = text

    def toPlainText(self):
        return self._t

    def setPlainText(self, t):
        self._t = str(t)

    def setText(self, t):
        self.setPlainText(t)


class _FakeCombo:
    def __init__(self, items=("秒", "毫秒", "分钟"), index=0):
        self._items = list(items)
        self._i = index

    def currentText(self):
        return self._items[self._i]

    def currentIndex(self):
        return self._i

    def setCurrentIndex(self, i):
        self._i = int(i)

    def setCurrentText(self, t):
        if t in self._items:
            self._i = self._items.index(t)


def _make_ui(freq_list: str, dwell="10", volt="230"):
    ui = SimpleNamespace()
    ui.checkBox_S2 = _FakeCheck(True)
    ui.checkBox_S3 = _FakeCheck(True)  # 主开关：启用频率台阶
    ui.textEdit_FrequencyLadder = _FakeText(freq_list)
    ui.textEdit_FrequencyLadder_VOLT = _FakeText(volt)
    ui.textEdit_FrequencyLadder_TIME = _FakeText(dwell)
    ui.comboBox_FrequencyLadder_TIME = _FakeCombo(index=0)  # 秒
    # legacy cards S4~S17（S3 主开关单独保留，不被覆盖）
    for i in range(3, 18):
        if i == 3:
            # 隐藏卡上的 S3 仍要有 FR/VOLT/TIME，但复选框用独立对象
            setattr(ui, "checkBox_S3_card", _FakeCheck(False))
        else:
            setattr(ui, f"checkBox_S{i}", _FakeCheck(False))
        setattr(ui, f"textEdit_S{i}_AC_FR", _FakeText("50"))
        setattr(ui, f"textEdit_S{i}_AC_VOLT", _FakeText("230"))
        setattr(ui, f"textEdit_S{i}_TIME", _FakeText("60"))
        setattr(ui, f"comboBox_S{i}_TIME", _FakeCombo(index=0))
    # sync 会写 checkBox_S3；保证主开关仍在
    ui.checkBox_S3 = _FakeCheck(True)
    ui._wtStacked = None
    return ui


def _is_async(v):
    return str(v).strip().upper() in ("ASYNC_START", "WT_ASYNC_START")


def _is_wait(v):
    return str(v).strip().upper() in ("WAIT_END", "WT_WAIT_END")


def test_cross_sweep_command_pipeline():
    # 交叉：升 → 降 → 再升，共 13 点（含往返）
    cross = "50,50.25,50.5,50.75,51.0,50.75,50.5,50.25,50,50.5,51.0,50.5,50"
    freqs = parse_freq_hz_list(cross)
    assert len(freqs) == 13
    assert freqs[0] == "50" and freqs[4] == "51" and freqs[8] == "50"
    assert freqs[10] == "51" and freqs[-1] == "50"

    ui = _make_ui(cross, dwell="5")
    sync_freq_list_to_legacy_cards(ui)
    # 前 13 张卡应启用，后面关闭
    assert ui.checkBox_S3.isChecked() and ui.checkBox_S15.isChecked()
    assert not ui.checkBox_S16.isChecked()
    assert ui.textEdit_S3_AC_FR.toPlainText() == "50"
    assert ui.textEdit_S7_AC_FR.toPlainText() == "51"

    pts, src = collect_freq_points_with_per_step_dwell(ui)
    assert src == "list"
    assert len(pts) == 13
    assert [p[0] for p in pts] == freqs

    # 模拟 S1 已 OUTP ON 后的命令队列
    rows = []
    rows.append(["AC", "write", "OUTP ON", "", "", "", "", "", "", ""])
    rows.append(["AC", "query", "*IDN?", "", "", "", "", "", "", "300"])  # S1 稳定
    steps = []
    n, start = append_freq_ladder_commands(rows, steps, "三相", pts)
    assert n == 13
    assert start == 2

    freq_seq = []
    for r in rows:
        if r[1] == "write" and str(r[2]).startswith("FREQ "):
            freq_seq.append(str(r[2]).split()[1])
    # 三相：每点一次 FREQ（EDIT ALL 同步），不再分相写 3 次
    assert len(freq_seq) == 13
    assert freq_seq == freqs
    assert sum(1 for r in rows if r[2] == "INST:EDIT ALL") == 13
    assert not any(str(r[2]).startswith("INST:NSEL") for r in rows)

    # 连续录包装（与 SCPITestWave 同逻辑）
    import SCPITestWave as M

    class _Msg:
        def append(self, *_a, **_k):
            pass

    M.ui = SimpleNamespace(textEdit_ReturnMessage=_Msg())
    # Upper_WT_Config dict
    rows.insert(
        0,
        [
            "Upper_WT_Config",
            "",
            "",
            "config_dict",
            {
                "textEdit_FileNameList": "cross_OF,other",
                "textEdit_StopTime": "00:02:00",
                "comboBox_AutoSave": 1,
            },
            "",
            "",
            "",
            "",
            "",
        ],
    )
    ok = M._enable_freq_step_continuous_record(
        rows, ui, file_default="OF_curve", log_label="过频降载"
    )
    assert ok is True

    async_i = [i for i, r in enumerate(rows) if _is_async(r[6])]
    wait_i = [i for i, r in enumerate(rows) if _is_wait(r[6])]
    assert len(async_i) == 1 and len(wait_i) == 1
    assert async_i[0] < wait_i[0]

    # ASYNC 在 OUTP ON 后、第一个 FREQ 前
    outp = next(i for i, r in enumerate(rows) if r[1] == "write" and r[2] == "OUTP ON")
    first_freq = next(
        i for i, r in enumerate(rows) if r[1] == "write" and str(r[2]).startswith("FREQ ")
    )
    assert outp < async_i[0] < first_freq

    # 无残留数字 col6 单点测量
    for r in rows:
        if r[0] == "AC" and r[1] == "query" and r[6] not in ("", None):
            assert _is_async(r[6]) or _is_wait(r[6]), r[6]

    cfg = rows[0][4]
    assert cfg["textEdit_FileNameList"] == "cross_OF"
    # 13*5s + 15s margin = 80s → 00:01:20
    assert cfg["textEdit_StopTime"] == "00:01:20"

    # >15 点交叉也不截断
    long_list = ",".join(["50", "50.2", "50.4", "50.6", "50.8", "51.0"] * 4)  # 24 点
    ui2 = _make_ui(long_list, dwell="2")
    pts2, src2 = collect_freq_points_with_per_step_dwell(ui2)
    assert src2 == "list" and len(pts2) == 24
    rows2, steps2 = [["AC", "write", "OUTP ON"] + [""] * 7], []
    assert append_freq_ladder_commands(rows2, steps2, "单相", pts2)[0] == 24
    assert M._enable_freq_step_continuous_record(
        rows2, ui2, file_default="OF_curve", log_label="过频降载"
    )
    dwell_total, n = M._freq_ladder_dwell_01s(ui2)
    assert n == 24
    assert abs(dwell_total - SetTimeFunction(2.0, "秒") * 24) < 1e-6


if __name__ == "__main__":
    test_cross_sweep_command_pipeline()
    print("CROSS_OK")
