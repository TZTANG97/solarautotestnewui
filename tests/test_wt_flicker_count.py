# -*- coding: utf-8 -*-
"""FLICKER:COUNT 解析 / 回读确认；模拟 WT5000 INITIALIZE 后 COUNT 掉回 1。"""
from __future__ import annotations

from pathlib import Path

from utils.wt_flicker_scpi import _parse_count_reply, ensure_flicker_count, query_flicker_count


def test_parse_count_reply():
    assert _parse_count_reply("12") == 12
    assert _parse_count_reply("+12") == 12
    assert _parse_count_reply(":FLIC:COUN 12") == 12
    assert _parse_count_reply("FLICKER:COUNT 1") == 1


def test_ensure_flicker_count_confirms():
    writes = []

    class _H:
        def write(self, cmd):
            writes.append(cmd)

        def query(self, cmd):
            if "COUNT?" in cmd.upper() or "COUN?" in cmd.upper():
                return "12"
            return '0,"No error"'

    class _C:
        connected = True
        handle = _H()

    ok, msg = ensure_flicker_count(12, ctrl=_C(), retries=1)
    assert ok is True
    assert any("COUNT 12" in w.upper() for w in writes)
    assert "12" in msg


def test_ensure_flicker_count_fails_when_stuck_at_one():
    class _H:
        def write(self, cmd):
            pass

        def query(self, cmd):
            if "COUNT?" in cmd.upper() or "COUN?" in cmd.upper():
                return "1"
            return '0,"No error"'

    class _C:
        connected = True
        handle = _H()

    ok, msg = ensure_flicker_count(12, ctrl=_C(), retries=2)
    assert ok is False
    assert "12" in msg


def test_wt5000_init_wipes_count_then_post_init_rewrite_recovers(monkeypatch):
    """现场：COUNT 12 → INITIALIZE 打回 1 → 补写+回读 → 再确认 12。"""
    monkeypatch.setattr("utils.wt_flicker_scpi.time.sleep", lambda _s: None)

    class _Wt5000:
        def __init__(self):
            self.count = 1
            self.writes = []

        def write(self, cmd: str):
            self.writes.append(str(cmd))
            u = str(cmd or "").strip().upper().replace(" ", "")
            if u.startswith("FLICKER:COUNT") and not u.endswith("?"):
                # FLICKER:COUNT 12
                token = u.split("COUNT", 1)[-1].strip()
                self.count = int(float(token))
            elif u.startswith("FLICKER:INITIALIZE") or u == "FLICKER:INIT":
                self.count = 1  # WT5000 偶发复位

        def query(self, cmd: str):
            u = str(cmd or "").strip().upper().replace(" ", "")
            if "COUNT?" in u or "COUN?" in u:
                return f":FLIC:COUN {self.count}"
            return '0,"No error"'

    class _C:
        def __init__(self, handle):
            self.connected = True
            self.handle = handle

    h = _Wt5000()
    ctrl = _C(h)

    # 与 Soft Panel 队列一致：先 COUNT，再 INIT（会掉回 1），再 ensure 补写
    h.write("FLICKER:COUNT 12")
    assert h.count == 12
    h.write("FLICKER:INITIALIZE")
    assert h.count == 1  # 复现屏上 Count 1/1

    ok, msg = ensure_flicker_count(12, ctrl=ctrl, retries=3)
    assert ok is True, msg
    assert h.count == 12
    assert "已确认" in msg
    # 至少有一次 INIT 后的 COUNT 写入
    assert sum(1 for w in h.writes if "COUNT 12" in w.upper()) >= 2


def test_scpi_queue_rewrites_count_after_initialize():
    """生成侧：INITIALIZE 之后必须再有一条 FLICKER:COUNT（防 WT5000 掉回 1）。"""
    text = Path(__file__).resolve().parents[1].joinpath("SCPITestWave.py").read_text(
        encoding="utf-8", errors="ignore"
    )
    # 只看闪变 Send 附近一段，避免误命中别处
    marker = 'strArraySingle[2] = "FLICKER:INITIALIZE"'
    idx = text.find(marker)
    assert idx > 0
    window = text[idx : idx + 800]
    assert 'FLICKER:COUNT " + S2_FLICKER_COUNT' in window
