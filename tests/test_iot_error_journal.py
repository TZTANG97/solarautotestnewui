# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from pathlib import Path

from utils.iot_error_journal import (
    RETENTION_DAYS,
    mark_uploaded,
    peek_unsent,
    prune_daily_logs,
    record_error,
)


def test_record_peek_and_mark_uploaded(tmp_path: Path):
    eid = record_error(
        "ui",
        "交流电源未连接，请先连接",
        base_dir=tmp_path,
        source="提示",
        now=datetime(2026, 10, 29, 14, 0, 0),
    )
    assert eid
    pending = peek_unsent(tmp_path)
    assert len(pending) == 1
    assert pending[0]["id"] == eid
    assert pending[0]["message"] == "交流电源未连接，请先连接"
    assert pending[0]["category"] == "ui"
    mark_uploaded(tmp_path, [eid])
    assert peek_unsent(tmp_path) == []


def test_start_experiment_wording_is_tagged(tmp_path: Path):
    eid = record_error(
        "ui",
        "实验执行代码格式：start 模块开头且需要包含 stop 模块",
        base_dir=tmp_path,
        source="开始实验",
        now=datetime(2026, 10, 29, 14, 1, 0),
    )
    assert eid
    row = peek_unsent(tmp_path)[0]
    assert row["category"] == "start"
    assert row["source"] == "开始实验"


def test_same_message_within_a_minute_is_not_duplicated(tmp_path: Path):
    now = datetime(2026, 10, 29, 14, 2, 0)
    first = record_error("log", "下发失败", base_dir=tmp_path, source="ac", now=now)
    second = record_error(
        "log",
        "下发失败",
        base_dir=tmp_path,
        source="ac",
        now=now + timedelta(seconds=10),
    )
    assert first
    assert second is None
    assert len(peek_unsent(tmp_path)) == 1


def test_entries_older_than_90_days_are_dropped(tmp_path: Path):
    old = datetime(2026, 10, 29, 12, 0, 0) - timedelta(days=RETENTION_DAYS + 1)
    record_error("log", "过期报错", base_dir=tmp_path, now=old)
    fresh = datetime(2026, 10, 29, 12, 0, 0)
    record_error("log", "仍保留", base_dir=tmp_path, now=fresh)
    pending = peek_unsent(tmp_path)
    assert [row["message"] for row in pending] == ["仍保留"]


def test_daily_log_files_older_than_90_days_are_removed(tmp_path: Path):
    log_dir = tmp_path / "data_logs"
    log_dir.mkdir()
    old_day = (datetime(2026, 10, 29) - timedelta(days=RETENTION_DAYS + 3)).strftime("%Y-%m-%d")
    keep_day = datetime(2026, 10, 29).strftime("%Y-%m-%d")
    (log_dir / f"auto_test_{old_day}.log").write_text("old", encoding="utf-8")
    (log_dir / f"auto_test_{keep_day}.log").write_text("new", encoding="utf-8")
    (log_dir / "notes.txt").write_text("keep", encoding="utf-8")
    removed = prune_daily_logs(tmp_path, now=datetime(2026, 10, 29, 8, 0, 0))
    assert removed == 1
    assert not (log_dir / f"auto_test_{old_day}.log").exists()
    assert (log_dir / f"auto_test_{keep_day}.log").is_file()
    assert (log_dir / "notes.txt").is_file()


def test_sensitive_line_is_redacted(tmp_path: Path):
    record_error(
        "log",
        "连接失败 password=secret-value",
        base_dir=tmp_path,
        now=datetime(2026, 10, 29, 15, 0, 0),
    )
    row = peek_unsent(tmp_path)[0]
    assert "secret-value" not in row["message"]
    assert "已省略敏感字段" in row["message"]
