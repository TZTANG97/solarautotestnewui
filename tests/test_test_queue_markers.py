# -*- coding: utf-8 -*-
from utils.test_queue_markers import (
    is_queue_end_row,
    make_queue_end_row,
    parse_queue_segments,
    row_pause_after,
    segment_at_command,
    settle_finished_round_note,
    stamp_queue_times,
)


def test_make_and_parse_pause_marker():
    row = make_queue_end_row("谐波电流", pause_after=True)
    assert is_queue_end_row(row)
    assert row_pause_after(row) is True
    cmds = [
        ["AC", "write", "OUTP ON", "", "", "", "", "", "", "10"],
        row,
        ["AC", "write", "OUTP OFF", "", "", "", "", "", "", "5"],
        make_queue_end_row("过载", pause_after=False),
    ]
    segs = parse_queue_segments(cmds, fallback_name="X")
    assert len(segs) == 2
    assert segs[0]["name"] == "谐波电流"
    assert segs[0]["pause_after"] is True
    assert segs[1]["name"] == "过载"
    hit = segment_at_command(segs, 1)
    assert hit["name"] == "谐波电流"
    hit2 = segment_at_command(segs, 3)
    assert hit2 is not None
    assert hit2["name"] == "过载"


def test_stamp_queue_start_and_finish():
    q = [
        {"name": "电压闪变", "status": "进行中"},
        {"name": "电压闪变", "status": "完成", "started_at": "2026-10-28 09:00:00"},
    ]
    stamp_queue_times(q, now_text="2026-10-28 10:00:00")
    assert q[0]["started_at"] == "2026-10-28 10:00:00"
    assert "finished_at" not in q[0]
    assert q[1]["started_at"] == "2026-10-28 09:00:00"
    assert q[1]["finished_at"] == "2026-10-28 10:00:00"
    stamp_queue_times(q, now_text="2026-10-28 11:00:00")
    assert q[1]["finished_at"] == "2026-10-28 10:00:00"


def test_seal_unstarted_queue_items_stops_counting():
    from utils.test_queue_markers import seal_unstarted_queue_items

    q = [
        {"name": "电压闪变", "status": "完成", "started_at": "2026-10-30 18:04:48"},
        {"name": "过载", "status": "等待"},
        {"name": "谐波", "status": "等待"},
    ]
    seal_unstarted_queue_items(q)
    assert q[0]["status"] == "完成"
    assert "started_at" not in q[1]
    assert q[1]["status"] == "中止"
    assert q[2]["status"] == "中止"


def test_close_queue_clocks_keeps_unstarted():
    from utils.test_queue_markers import close_queue_clocks

    q = [
        {"name": "电压闪变", "status": "完成", "started_at": "2026-10-30 18:04:48", "finished_at": "2026-10-30 20:11:05"},
        {"name": "电压闪变", "status": "进行中", "started_at": "2026-10-30 20:11:05"},
        {"name": "电压闪变", "status": "等待"},
    ]
    close_queue_clocks(q, now_text="2026-10-30 22:17:22", aborted=False)
    assert q[0]["finished_at"] == "2026-10-30 20:11:05"
    assert q[1]["status"] == "完成"
    assert q[1]["finished_at"] == "2026-10-30 22:17:22"
    assert "started_at" not in q[2]
    assert q[2]["status"] == "等待"
    missing_start = [{"name": "电压闪变", "status": "完成"}]
    close_queue_clocks(missing_start, now_text="2026-10-30 22:17:22", aborted=False)
    assert "started_at" not in missing_start[0]
    assert missing_start[0]["finished_at"] == "2026-10-30 22:17:22"


def test_finished_round_drops_inflight_note():
    assert settle_finished_round_note("执行中") == ""
    assert settle_finished_round_note("测量中: QCap_BR") == ""
    assert settle_finished_round_note("本轮完成") == "本轮完成"
    assert settle_finished_round_note("") == ""
