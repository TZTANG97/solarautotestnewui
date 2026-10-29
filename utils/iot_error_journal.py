# -*- coding: utf-8 -*-
"""工控机报错流水：界面弹窗、开始实验、运行日志。

本地 data_logs/error_journal.jsonl，超过 90 天的记录和 auto_test_*.log 会删掉。
Agent 心跳把未上传的条目交给 IOT，光伏台架页按台架查看。
"""
from __future__ import annotations

import json
import logging
import os
import re
import threading
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

RETENTION_DAYS = 90
_DEDUP_SEC = 60
_BATCH = 20
_MAX_MESSAGE = 1000
_MAX_DETAIL = 4000
_ID_RE = re.compile(r"^[A-Za-z0-9_-]{8,64}$")
_LOG_NAME_RE = re.compile(r"^auto_test_(\d{4}-\d{2}-\d{2})\.log$")
_START_KEYS = ("开始实验", "开始试验", "开测")
_SENSITIVE = ("agent_token", "password", "accesskey", "secret")

_mem_lock = threading.Lock()
_recent: Dict[str, float] = {}
_installed_loggers: set = set()
_box_hooked = False


def journal_path(base_dir: str | Path) -> Path:
    return Path(base_dir) / "data_logs" / "error_journal.jsonl"


def _sent_path(base_dir: str | Path) -> Path:
    return Path(base_dir) / "data_logs" / "error_journal_sent.json"


def _lock_path(base_dir: str | Path) -> Path:
    return Path(base_dir) / "data_logs" / "error_journal.lock"


def _now() -> datetime:
    return datetime.now()


def _cutoff(now: Optional[datetime] = None) -> datetime:
    return (now or _now()) - timedelta(days=RETENTION_DAYS)


def _redact(text: str, limit: int) -> str:
    lines = []
    for line in str(text or "").splitlines():
        low = line.lower()
        if any(key in low for key in _SENSITIVE):
            lines.append("[已省略敏感字段]")
        else:
            lines.append(line)
    return "\n".join(lines).strip()[:limit]


def _category_for_text(title: str, text: str, default: str) -> str:
    blob = f"{title}\n{text}"
    if any(key in blob for key in _START_KEYS):
        return "start"
    return default


def _parse_at(raw: str) -> Optional[datetime]:
    s = str(raw or "").strip().replace("Z", "")
    if not s:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s[:19], fmt)
        except ValueError:
            continue
    return None


def _lock_file(fh) -> None:
    if os.name == "nt":
        import msvcrt

        fh.seek(0)
        msvcrt.locking(fh.fileno(), msvcrt.LK_LOCK, 1)
        return
    import fcntl

    fcntl.flock(fh.fileno(), fcntl.LOCK_EX)


def _unlock_file(fh) -> None:
    if os.name == "nt":
        import msvcrt

        fh.seek(0)
        msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
        return
    import fcntl

    fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


class _FileLock:
    def __init__(self, base_dir: str | Path) -> None:
        self._path = _lock_path(base_dir)
        self._fh = None

    def __enter__(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(self._path, "a+b")
        if self._fh.seek(0, os.SEEK_END) < 1:
            self._fh.write(b" ")
            self._fh.flush()
        _lock_file(self._fh)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            if self._fh is not None:
                _unlock_file(self._fh)
                self._fh.close()
        except Exception:
            pass
        return None


def _read_rows(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        return []
    rows: List[Dict[str, Any]] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict) and item.get("id") and item.get("message"):
            rows.append(item)
    return rows


def _read_sent(path: Path) -> set:
    if not path.is_file():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    if not isinstance(data, list):
        return set()
    return {str(x) for x in data if str(x).strip()}


def _write_rows(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(body, encoding="utf-8")
    os.replace(tmp, path)


def _write_sent(path: Path, ids: set) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(sorted(ids), ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def prune_daily_logs(base_dir: str | Path, *, now: Optional[datetime] = None) -> int:
    """删除 data_logs 里超过 90 天的 auto_test_YYYY-MM-DD.log。"""
    log_dir = Path(base_dir) / "data_logs"
    if not log_dir.is_dir():
        return 0
    cutoff = _cutoff(now).date()
    removed = 0
    for path in log_dir.glob("auto_test_*.log"):
        match = _LOG_NAME_RE.match(path.name)
        if not match:
            continue
        try:
            day = datetime.strptime(match.group(1), "%Y-%m-%d").date()
        except ValueError:
            continue
        if day < cutoff:
            try:
                path.unlink()
                removed += 1
            except OSError:
                pass
    return removed


def _prune_rows(rows: List[Dict[str, Any]], *, now: Optional[datetime] = None) -> List[Dict[str, Any]]:
    cutoff = _cutoff(now)
    kept = []
    for row in rows:
        at = _parse_at(str(row.get("at") or ""))
        if at is None or at >= cutoff:
            kept.append(row)
    return kept


def record_error(
    category: str,
    message: str,
    *,
    base_dir: str | Path,
    source: str = "",
    detail: str = "",
    now: Optional[datetime] = None,
) -> Optional[str]:
    """写入一条报错。相同内容 60 秒内不重复记。返回条目 id。"""
    msg = _redact(message, _MAX_MESSAGE)
    if not msg:
        return None
    cat = _category_for_text(source, msg, (category or "log").strip()[:32] or "log")
    stamp = now or _now()
    key = f"{cat}|{source}|{msg}"
    with _mem_lock:
        prev = _recent.get(key)
        if prev is not None and (stamp.timestamp() - prev) < _DEDUP_SEC:
            return None
        _recent[key] = stamp.timestamp()
        dead = [k for k, ts in _recent.items() if stamp.timestamp() - ts > _DEDUP_SEC]
        for k in dead:
            _recent.pop(k, None)
    row = {
        "id": uuid.uuid4().hex,
        "at": stamp.strftime("%Y-%m-%dT%H:%M:%S"),
        "category": cat,
        "source": _redact(source, 128),
        "message": msg,
        "detail": _redact(detail, _MAX_DETAIL),
    }
    if not _ID_RE.match(row["id"]):
        return None
    path = journal_path(base_dir)
    with _FileLock(base_dir):
        rows = _prune_rows(_read_rows(path), now=stamp)
        rows.append(row)
        _write_rows(path, rows)
        sent = _read_sent(_sent_path(base_dir))
        live = {str(item.get("id")) for item in rows}
        if sent - live:
            _write_sent(_sent_path(base_dir), sent & live)
    prune_daily_logs(base_dir, now=stamp)
    return row["id"]


def peek_unsent(base_dir: str | Path, *, limit: int = _BATCH) -> List[Dict[str, Any]]:
    path = journal_path(base_dir)
    with _FileLock(base_dir):
        rows = _prune_rows(_read_rows(path))
        _write_rows(path, rows)
        sent = _read_sent(_sent_path(base_dir))
        live = {str(item.get("id")) for item in rows}
        if sent - live:
            _write_sent(_sent_path(base_dir), sent & live)
            sent = sent & live
    out = []
    for row in rows:
        if str(row.get("id")) in sent:
            continue
        out.append(
            {
                "id": str(row.get("id")),
                "at": str(row.get("at") or ""),
                "category": str(row.get("category") or ""),
                "source": str(row.get("source") or ""),
                "message": str(row.get("message") or ""),
                "detail": str(row.get("detail") or ""),
            }
        )
        if len(out) >= max(1, int(limit)):
            break
    return out


def mark_uploaded(base_dir: str | Path, ids: List[str]) -> None:
    wanted = {str(x).strip() for x in ids or [] if str(x).strip()}
    if not wanted:
        return
    with _FileLock(base_dir):
        sent = _read_sent(_sent_path(base_dir))
        sent.update(wanted)
        rows = _read_rows(journal_path(base_dir))
        live = {str(item.get("id")) for item in rows}
        _write_sent(_sent_path(base_dir), sent & live if live else sent)


class ErrorJournalHandler(logging.Handler):
    def __init__(self, base_dir: str | Path) -> None:
        super().__init__(level=logging.ERROR)
        self._base_dir = base_dir

    def emit(self, record: logging.LogRecord) -> None:
        try:
            # stderr 被整段转到 auto_test ERROR，那些行不是一次报错，不上传。
            if record.filename == "logging_setup.py" and record.funcName in ("write", "flush"):
                return
            msg = record.getMessage()
            detail = ""
            if record.exc_info:
                detail = self.format(record)
            record_error(
                "log",
                msg,
                base_dir=self._base_dir,
                source=f"{record.filename}:{record.lineno}",
                detail=detail,
            )
        except Exception:
            self.handleError(record)


def install_error_journal(
    logger: logging.Logger,
    *,
    base_dir: str | Path,
    hook_message_box: bool = True,
) -> None:
    """给指定 logger 加 ERROR 落盘。界面进程再挂钩 QMessageBox.warning/critical。"""
    name = logger.name or ""
    if name not in _installed_loggers:
        logger.addHandler(ErrorJournalHandler(base_dir))
        _installed_loggers.add(name)
    if hook_message_box:
        _hook_message_box(base_dir)
    prune_daily_logs(base_dir)


def _hook_message_box(base_dir: str | Path) -> None:
    global _box_hooked
    if _box_hooked:
        return
    try:
        from PyQt5.QtWidgets import QMessageBox
    except Exception:
        return

    def _wrap(original):
        def wrapped(*args, **kwargs):
            title = str(args[1] if len(args) > 1 else kwargs.get("title") or "")
            text = str(args[2] if len(args) > 2 else kwargs.get("text") or "")
            msg = text.strip() or title.strip()
            if msg:
                try:
                    record_error(
                        _category_for_text(title, text, "ui"),
                        msg,
                        base_dir=base_dir,
                        source=title.strip()[:128],
                    )
                except Exception:
                    pass
            return original(*args, **kwargs)

        return wrapped

    QMessageBox.warning = _wrap(QMessageBox.warning)
    QMessageBox.critical = _wrap(QMessageBox.critical)
    _box_hooked = True
