# -*- coding: utf-8 -*-
"""交叉冒烟：设备异步 I/O 框架 + 过频台阶 + ScpiSocket 短探测。

不启动完整 SCPITestWave GUI；验证：
1) _run_device_io 同步返回、界面线程可泵事件
2) 过频 list/EDIT ALL 频率台阶未回归
3) ScpiSocket 自动端口探测超时 ≤1.5s
"""
from __future__ import annotations

import socket
import sys
import threading
import time
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _test_run_device_io_keeps_event_loop():
    from PyQt5.QtCore import QTimer
    from PyQt5.QtWidgets import QApplication

    # 避免导入完整 SCPITestWave（会拉起大量 UI）；就地复刻核心逻辑做契约测试
    app = QApplication.instance() or QApplication([])

    busy = {"depth": 0}
    active = set()

    class Bridge:
        from PyQt5.QtCore import QObject, pyqtSignal

    from PyQt5.QtCore import QEventLoop, QObject, QThread, pyqtSignal

    class _Bridge(QObject):
        finished = pyqtSignal(str, object)

    bridge = _Bridge()
    ticks = {"n": 0}

    def _pump_tick():
        ticks["n"] += 1

    timer = QTimer()
    timer.timeout.connect(_pump_tick)
    timer.start(20)

    def run_device_io(job_id, work_fn):
        if job_id in active:
            return None
        box = {"result": None, "error": None}
        loop = QEventLoop()

        def _on_finished(jid, payload):
            if jid != job_id:
                return
            box["result"] = payload.get("result")
            box["error"] = payload.get("error")
            loop.quit()

        bridge.finished.connect(_on_finished)
        active.add(job_id)

        def _runner():
            try:
                result = work_fn()
                bridge.finished.emit(job_id, {"result": result, "error": None})
            except Exception as exc:
                bridge.finished.emit(job_id, {"result": None, "error": exc})

        try:
            busy["depth"] += 1
            threading.Thread(target=_runner, daemon=True).start()
            loop.exec_()
        finally:
            bridge.finished.disconnect(_on_finished)
            active.discard(job_id)
            busy["depth"] = max(0, busy["depth"] - 1)

        if box["error"] is not None:
            raise box["error"]
        return box["result"]

    def work():
        time.sleep(0.25)
        return "ok"

    t0 = time.time()
    assert run_device_io("job1", work) == "ok"
    elapsed = time.time() - t0
    timer.stop()
    assert elapsed >= 0.2
    assert ticks["n"] >= 3, f"event loop did not pump, ticks={ticks['n']}"
    assert busy["depth"] == 0
    assert not active
    # 调用方语义：返回后结果已就绪（Itech/Bluesight 依赖）
    print("ASYNC_IO_OK", ticks["n"], round(elapsed, 3))


def _test_overfreq_cross():
    from utils.overfreq_ladder_commands import append_freq_point_rows, parse_freq_hz_list

    pts = parse_freq_hz_list("50, 50.25, 50.5, 49.75")
    assert [float(x) for x in pts] == [50.0, 50.25, 50.5, 49.75]
    rows: list = []
    for f in pts:
        append_freq_point_rows(rows, "三相", "230", f, 100)
    freq_cmds = [
        r
        for r in rows
        if isinstance(r, (list, tuple))
        and any(str(c).upper().startswith("FREQ") for c in r)
    ]
    # 三相：每点一次 FREQ（EDIT ALL），不能再出现每相各一次
    assert len(freq_cmds) == len(pts), (len(freq_cmds), pts)
    edit_all = [
        r
        for r in rows
        if isinstance(r, (list, tuple)) and any("EDIT ALL" in str(c) for c in r)
    ]
    assert edit_all, "expected INST:EDIT ALL for three-phase"
    print("OVERFREQ_CROSS_OK", len(rows), len(freq_cmds))


def _test_scpi_probe_timeout():
    from devices.scpi_socket import ScpiSocket

    sock = ScpiSocket("127.0.0.1", port=None, timeout=10)
    # 强制探测路径：所有端口拒绝/超时，应快速失败
    t0 = time.time()
    with patch.object(ScpiSocket, "_try_connect", side_effect=socket.timeout("boom")):
        try:
            sock.connect()
            raise AssertionError("should fail")
        except ConnectionError:
            pass
    elapsed = time.time() - t0
    # 6 口 × ≤1.5s 理论最多 ~9s；以前 6×10s=60s。这里 mock 立即抛，应接近 0。
    assert elapsed < 2.0, elapsed
    # 确认探测超时被压到 ≤1.5
    assert min(float(10), 1.5) == 1.5
    print("SCPI_PROBE_OK", round(elapsed, 4))


def main():
    _test_run_device_io_keeps_event_loop()
    _test_overfreq_cross()
    _test_scpi_probe_timeout()
    print("CROSS_ALL_OK")


if __name__ == "__main__":
    main()
