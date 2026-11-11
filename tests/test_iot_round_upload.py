# -*- coding: utf-8 -*-
"""分开录：每轮 CSV 查找与上传调度。"""
from __future__ import annotations

import time
from pathlib import Path

from utils.iot_round_upload import find_round_csv, schedule_round_csv_upload


def test_find_round_csv_by_label(tmp_path: Path):
    name = "OVUF_S3_V230_255_223359"
    csv_path = tmp_path / f"{name}.csv"
    csv_path.write_text("t,v\n0,1\n", encoding="utf-8")
    hit = find_round_csv(
        name,
        config_dict={"textEdit_SavePath": str(tmp_path)},
        wait_s=0.2,
    )
    assert hit is not None
    assert Path(hit).name.lower().startswith("ovuf_s3")


def test_finalize_recording_round_marks_done_and_keeps_path(tmp_path: Path):
    from utils.recording_round import finalize_recording_round

    csv_path = tmp_path / "OVUF_S3.csv"
    csv_path.write_text("t,v\n0,1\n", encoding="utf-8")
    marked = []

    def _set(idx, status, note=None):
        marked.append((idx, status, note))

    label = finalize_recording_round(
        0,
        ["OVUF_S3"],
        csv_path=str(csv_path),
        rounds=[{"index": 1, "filename": "OVUF_S3", "status": "进行中"}],
        set_round=_set,
    )
    assert label == "OVUF_S3"
    assert marked == [(0, "完成", "本轮完成")]


def test_schedule_round_csv_upload_no_job_does_not_raise(tmp_path: Path):
    name = "OVUF_S4_V230_253_223359"
    (tmp_path / f"{name}.csv").write_text("t,v\n0,1\n", encoding="utf-8")
    schedule_round_csv_upload(
        round_index=0,
        file_label=name,
        config_dict={"textEdit_SavePath": str(tmp_path)},
        job_id=0,
        wait_s=0.2,
    )
    time.sleep(0.4)
