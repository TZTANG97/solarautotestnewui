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
            return 1

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


def test_analysis_root_accepts_bundled_cei_layout(tmp_path):
    from utils.iot_data_analysis_bridge import _looks_like_analysis_root

    bundled = tmp_path / "bundled_analysis"
    (bundled / "src" / "mypkg").mkdir(parents=True)
    (bundled / "run_headless.py").write_text("# headless\n", encoding="utf-8")
    assert _looks_like_analysis_root(bundled)
