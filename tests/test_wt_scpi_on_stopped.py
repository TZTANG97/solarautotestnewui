# -*- coding: utf-8 -*-
"""SCPI 停采后先回调 on_stopped，再导出。"""
from utils import wt_scpi_session as sess


def test_run_measure_blocking_calls_on_stopped_before_export(monkeypatch):
    order = []

    class FakeCollector:
        def start_gathering(self):
            return True

        def stop_gathering(self):
            order.append("stop")

        def total_rows(self):
            return 2

        def sample_once(self):
            return None

        def export_to_csv(self, path=None):
            order.append("export")
            return path or "x.csv"

        def sample_interval_stats(self):
            return {}

        def last_error(self):
            return ""

    monkeypatch.setattr(sess, "prepare_from_config", lambda *a, **k: (True, ""))
    monkeypatch.setattr(sess, "ensure_collector", lambda logger=None: FakeCollector())
    monkeypatch.setattr(sess, "resolve_csv_path", lambda *a, **k: "out.csv")
    monkeypatch.setattr(sess, "rate_text_from_config", lambda *a, **k: "50ms")
    monkeypatch.setattr(sess, "_stoptime_seconds", lambda *a, **k: 0.01)
    sess.request_stop("test")

    def _on_stopped():
        order.append("on_stopped")

    ok = sess.run_measure_blocking({"textEdit_StopTime": "1"}, on_stopped=_on_stopped)
    assert ok is True
    assert order.index("stop") < order.index("on_stopped") < order.index("export")


def test_run_measure_blocking_clears_stop_request_for_next_round(monkeypatch):
    """第一轮 WAIT_END 置 _stop_requested=True，第二轮不能在 0.00s 秒退采到 0 行。"""
    import time as _time

    durations = []

    class FakeCollector:
        def __init__(self):
            self._t0 = 0.0
            self._rows = 0

        def start_gathering(self):
            self._t0 = _time.time()
            self._rows = 0
            return True

        def stop_gathering(self):
            dt = _time.time() - self._t0
            durations.append(dt)
            self._rows = 5 if dt >= 0.08 else 0

        def total_rows(self):
            return self._rows

        def sample_once(self):
            return None

        def export_to_csv(self, path=None):
            return (path or "x.csv") if self._rows > 0 else ""

        def sample_interval_stats(self):
            return {}

        def last_error(self):
            return ""

    monkeypatch.setattr(sess, "prepare_from_config", lambda *a, **k: (True, ""))
    monkeypatch.setattr(sess, "ensure_collector", lambda logger=None: FakeCollector())
    monkeypatch.setattr(sess, "resolve_csv_path", lambda *a, **k: "out.csv")
    monkeypatch.setattr(sess, "rate_text_from_config", lambda *a, **k: "50ms")
    monkeypatch.setattr(sess, "_stoptime_seconds", lambda *a, **k: 0.12)

    sess.reset_session_state()
    sess.request_stop("WAIT_END_round1")
    sess.run_measure_blocking({"textEdit_StopTime": "1"})

    # 第二项/第二轮：必须跑满时间，而不是被第一轮残留的 _stop_requested 秒退
    ok2 = sess.run_measure_blocking({"textEdit_StopTime": "1"})
    assert ok2 is True
    assert len(durations) == 2
    assert durations[1] >= 0.08


def test_analysis_root_accepts_bundled_cei_layout(tmp_path):
    from utils.iot_data_analysis_bridge import _looks_like_analysis_root

    bundled = tmp_path / "bundled_analysis"
    (bundled / "src" / "mypkg").mkdir(parents=True)
    (bundled / "run_headless.py").write_text("# headless\n", encoding="utf-8")
    assert _looks_like_analysis_root(bundled)
