# -*- coding: utf-8 -*-
"""过频降载 / 欠频升载交叉冒烟（命令生成 + step1 EDIT ALL + 结束可中断）。"""
from __future__ import annotations

import ast
import re
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
    ui.checkBox_S3 = _FakeCheck(True)
    ui.textEdit_FrequencyLadder = _FakeText(freq_list)
    ui.textEdit_FrequencyLadder_VOLT = _FakeText(volt)
    ui.textEdit_FrequencyLadder_TIME = _FakeText(dwell)
    ui.comboBox_FrequencyLadder_TIME = _FakeCombo(index=0)
    for i in range(3, 18):
        setattr(ui, f"checkBox_S{i}", _FakeCheck(False))
        setattr(ui, f"textEdit_S{i}_AC_FR", _FakeText("50"))
        setattr(ui, f"textEdit_S{i}_AC_VOLT", _FakeText("230"))
        setattr(ui, f"textEdit_S{i}_TIME", _FakeText("60"))
        setattr(ui, f"comboBox_S{i}_TIME", _FakeCombo(index=0))
    ui.checkBox_S3 = _FakeCheck(True)
    ui._wtStacked = None
    return ui


def _is_async(v):
    return str(v).strip().upper() in ("ASYNC_START", "WT_ASYNC_START")


def _is_wait(v):
    return str(v).strip().upper() in ("WAIT_END", "WT_WAIT_END")


def _assert_ladder_pipeline(label: str, freq_list: str, file_default: str):
    freqs = parse_freq_hz_list(freq_list)
    assert len(freqs) >= 5, (label, freqs)

    ui = _make_ui(freq_list, dwell="5")
    sync_freq_list_to_legacy_cards(ui)
    pts, src = collect_freq_points_with_per_step_dwell(ui)
    assert src == "list"
    assert [p[0] for p in pts] == freqs

    rows = []
    rows.append(["AC", "write", "OUTP ON", "", "", "", "", "", "", ""])
    rows.append(["AC", "query", "*IDN?", "", "", "", "", "", "", "300"])
    steps = []
    n = append_freq_ladder_commands(rows, steps, "三相", pts)
    assert n[0] == len(freqs)
    assert n[1] == 2

    freq_seq = [
        str(r[2]).split()[1]
        for r in rows
        if r[1] == "write" and str(r[2]).startswith("FREQ ")
    ]
    assert freq_seq == freqs, (label, freq_seq, freqs)
    assert sum(1 for r in rows if r[2] == "INST:EDIT ALL") == len(freqs)
    assert not any(str(r[2]).startswith("INST:NSEL") for r in rows)
    assert not any(str(r[2]) == "INST:EDIT EACH" for r in rows)

    import SCPITestWave as M

    class _Msg:
        def append(self, *_a, **_k):
            pass

    M.ui = SimpleNamespace(textEdit_ReturnMessage=_Msg())
    rows.insert(
        0,
        [
            "Upper_WT_Config",
            "",
            "",
            "config_dict",
            {
                "textEdit_FileNameList": f"cross_{file_default},other",
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
        rows, ui, file_default=file_default, log_label=label, ladder_start_index=n[1] + 1
    )
    assert ok is True

    async_i = [i for i, r in enumerate(rows) if _is_async(r[6])]
    wait_i = [i for i, r in enumerate(rows) if _is_wait(r[6])]
    assert len(async_i) == 1 and len(wait_i) == 1
    assert async_i[0] < wait_i[0]

    outp = next(i for i, r in enumerate(rows) if r[1] == "write" and r[2] == "OUTP ON")
    first_freq = next(
        i for i, r in enumerate(rows) if r[1] == "write" and str(r[2]).startswith("FREQ ")
    )
    assert outp < async_i[0] < first_freq

    cfg = rows[0][4]
    assert cfg["textEdit_FileNameList"] == f"cross_{file_default}"
    expected_sec = int(round(len(freqs) * 5 + 15))
    hh, rem = divmod(expected_sec, 3600)
    mm, ss = divmod(rem, 60)
    assert cfg["textEdit_StopTime"] == f"{hh:02d}:{mm:02d}:{ss:02d}"
    print(f"LADDER_OK {label} points={len(freqs)} StopTime={cfg['textEdit_StopTime']}")


def _extract_function_source(src: str, func_name: str) -> str:
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            return ast.get_source_segment(src, node) or ""
    raise AssertionError(f"function not found: {func_name}")


def _assert_step1_three_phase_edit_all(func_src: str, label: str):
    """step1 三相分支：必须 EDIT ALL，禁止 EACH/NSEL 逐相 FREQ。"""
    # 取 S1 三相到 OUTP ON 之间的片段
    m = re.search(
        r'elif S1ACEACHStatus == "三相":(.*?)strArraySingle\[2\] = "OUTP ON"',
        func_src,
        flags=re.S,
    )
    assert m, f"{label}: step1 三相分支未找到"
    block = m.group(1)
    assert "INST:EDIT ALL" in block, f"{label}: step1 缺少 EDIT ALL"
    assert "INST:EDIT EACH" not in block, f"{label}: step1 仍含 EDIT EACH"
    assert "INST:NSEL" not in block, f"{label}: step1 仍含 NSEL"
    # 三相 step1 只应有一次 FREQ
    freq_writes = re.findall(r'FREQ\s*"\s*\+|FREQ\s*"\s*\+|S1Command = "FREQ ', block)
    # 源码形态：S1Command = "FREQ " + S1ACFR
    freq_assigns = re.findall(r'S1Command = "FREQ "', block)
    assert len(freq_assigns) == 1, f"{label}: step1 FREQ 次数={len(freq_assigns)} (期望1)"
    print(f"STEP1_OK {label}")


def test_step1_source_guards():
    src = (ROOT / "SCPITestWave.py").read_text(encoding="utf-8")
    over = _extract_function_source(src, "thaiguopinjiangzaiSend")
    under = _extract_function_source(src, "thaiqianpinshengzaiSend")
    _assert_step1_three_phase_edit_all(over, "过频降载")
    _assert_step1_three_phase_edit_all(under, "欠频升载")


def test_messure_testing_abort_logic():
    """结束试验时测量计时应可中断（契约：循环内检查 strTestStatusFlag）。"""
    src = (ROOT / "SCPITestWave.py").read_text(encoding="utf-8")
    fn = _extract_function_source(src, "messure_testing")
    assert 'strTestStatusFlag == "结束"' in fn
    assert "aborted by EndProject" in fn
    assert "global test_status, save_file_name, strTestStatusFlag" in fn
    print("ABORT_OK messure_testing")


def test_over_under_cross():
    # 过频：升→降→再升交叉
    over = "50,50.25,50.5,50.75,51.0,50.75,50.5,50.25,50,50.5,51.0,50.5,50"
    _assert_ladder_pipeline("过频降载", over, "OF_curve")

    # 欠频：降→升→再降交叉
    under = "50,49.75,49.5,49.25,49.0,49.25,49.5,49.75,50,49.5,49.0,49.5,50"
    _assert_ladder_pipeline("欠频升载", under, "UF_curve")

    # 单相欠频也不应写 NSEL
    under_pts = parse_freq_hz_list(under)
    pts = [(f, "230", SetTimeFunction(1.0, "秒")) for f in under_pts]
    rows, steps = [], []
    n_u, _ = append_freq_ladder_commands(rows, steps, "单相", pts)
    assert n_u == len(under_pts)
    assert not any(str(r[2]).startswith("INST:NSEL") for r in rows)
    assert not any(str(r[2]) == "INST:EDIT EACH" for r in rows)
    print("SINGLE_PHASE_OK 欠频升载")

    # 首点与 S1 同频：只驻留、不重发 FREQ
    rows3, steps3 = [], []
    n3, start3 = append_freq_ladder_commands(
        rows3,
        steps3,
        "三相",
        [("50", "230", 100), ("50.5", "230", 100), ("51", "230", 100)],
        initial_freq="50",
    )
    assert n3 == 3 and start3 == 0
    freq3 = [str(r[2]).split()[1] for r in rows3 if str(r[2]).startswith("FREQ ")]
    assert freq3 == ["50.5", "51"], freq3
    assert sum(1 for r in rows3 if r[2] == "INST:EDIT ALL") == 2
    print("SKIP_SAME_FREQ_OK")


if __name__ == "__main__":
    test_step1_source_guards()
    test_messure_testing_abort_logic()
    test_over_under_cross()
    # 复用原过频交叉冒烟
    from test_overfreq_cross_smoke import test_cross_sweep_command_pipeline

    test_cross_sweep_command_pipeline()
    print("CROSS_OK")
