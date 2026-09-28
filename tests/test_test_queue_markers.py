# -*- coding: utf-8 -*-
from utils.test_queue_markers import (
    is_queue_end_row,
    make_queue_end_row,
    parse_queue_segments,
    row_pause_after,
    segment_at_command,
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
