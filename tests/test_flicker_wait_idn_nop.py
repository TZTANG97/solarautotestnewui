"""闪变驻留：*IDN? 改写成 wait 后必须保留 col8+col9 总时长。"""

from __future__ import annotations

from utils.ovuf_recording import rewrite_ac_idn_queries_as_wait


def _dwell_01(row) -> int:
    total = 0
    for idx in (8, 9):
        if len(row) <= idx:
            continue
        val = row[idx]
        if val in ("", None):
            continue
        total += int(float(val))
    return total


def test_rewrite_preserves_flicker_cycle_col8_and_col9():
    """回归：job142/143 墙钟约 50min≈只跑了 wait01b，col8 的主等待被 wait 分支丢掉。"""
    rows = [
        ["WT3000", "write", "FLICKER:START", "", "", "", "", "", "", 20],
        ["AC", "query", "*IDN?", "", "", "", "", "", 2400, ""],
        ["DC1", "write", "OUTP OFF", "", "", "", "", "", "", ""],
        ["AC", "query", "*IDN?", "", "", "", "", "", "", 1200],
        ["DC1", "write", "OUTP ON", "", "", "", "", "", "", ""],
        ["AC", "query", "*IDN?", "", "", "", "", "", 750, ""],
    ]
    idn_before = sum(_dwell_01(r) for r in rows if r[0] == "AC" and r[1] == "query")
    assert rewrite_ac_idn_queries_as_wait(rows) == 3
    idn_after = sum(_dwell_01(r) for r in rows if r[0] == "AC" and r[1] == "wait")
    assert idn_before == idn_after == 2400 + 1200 + 750
    assert rows[1][1] == "wait" and rows[1][2] == "IDN_NOP" and rows[1][8] == 2400
    assert rows[3][1] == "wait" and rows[3][9] == 1200
    assert rows[5][1] == "wait" and rows[5][8] == 750


def test_twelve_cycle_col9_only_is_about_half():
    """12×(2400+1200+1200+750)：只跑 col9≈48min；两列都跑≈111min（贴近 COUNT12 窗口）。"""
    rows = [["WT3000", "write", "FLICKER:START", "", "", "", "", "", "", 20]]
    for _ in range(12):
        rows.append(["AC", "query", "*IDN?", "", "", "", "", "", 2400, ""])
        rows.append(["DC1", "write", "OUTP OFF", "", "", "", "", "", "", ""])
        rows.append(["AC", "query", "*IDN?", "", "", "", "", "", "", 1200])
        rows.append(["DC1", "write", "OUTP OFF", "", "", "", "", "", "", ""])
        rows.append(["AC", "query", "*IDN?", "", "", "", "", "", "", 1200])
        rows.append(["DC1", "write", "OUTP OFF", "", "", "", "", "", "", ""])
        rows.append(["AC", "query", "*IDN?", "", "", "", "", "", 750, ""])
    rewrite_ac_idn_queries_as_wait(rows)
    only_col9 = 0
    both = 0
    for row in rows:
        if row[0] != "AC" or row[1] != "wait":
            continue
        if row[9] not in ("", None):
            only_col9 += int(float(row[9]))
        both += _dwell_01(row)
    assert abs(only_col9 * 0.1 / 60.0 - 48.0) < 0.2
    assert abs(both * 0.1 / 60.0 - 111.0) < 0.2
    # 旧 bug：只跑 col9 会在第 5 回附近截屏；修好后接近满 12 窗
    assert both > only_col9 * 2
