# -*- coding: utf-8 -*-
"""无仪器时模拟实时测量页：WT Soft Panel 数字块 + 量纲分栏曲线；德威创通道同理。"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from PyQt5 import QtCore, QtWidgets

from components.live_measure_page import LiveMeasurePage

OUT = ROOT / "code_example" / "media" / "live_measure_sim"
OUT.mkdir(parents=True, exist_ok=True)


def _fake_wt(step: int) -> dict:
    t = step * 0.5
    return {
        "U,1,TOTAL": 230.0 + 1.2 * math.sin(t / 3.0),
        "U,SIGMA,TOTAL": 230.2 + 0.8 * math.sin(t / 3.2 + 0.2),
        "I,1,TOTAL": 8.5 + 0.35 * math.sin(t / 2.5 + 0.4),
        "I,SIGMA,TOTAL": 8.6 + 0.3 * math.sin(t / 2.7 + 0.5),
        "P,1,TOTAL": 1950.0 + 40.0 * math.sin(t / 4.0),
        "P,SIGMA,TOTAL": 1965.0 + 35.0 * math.sin(t / 4.2 + 0.3),
        "LAMBDA,1,TOTAL": 0.98 + 0.01 * math.sin(t / 5.0),
        "LAMBDA,SIGMA,TOTAL": 0.979 + 0.008 * math.sin(t / 5.2),
        "FU,1": 50.0 + 0.04 * math.sin(t / 6.0),
        "FU,SIGMA": 50.0 + 0.03 * math.sin(t / 6.2),
    }


def _fake_dew(step: int) -> dict:
    t = step * 0.5
    return {
        "AI 1/U1": 230.0 + 1.5 * math.sin(t / 2.8),
        "AI 1/U2": 229.5 + 1.3 * math.sin(t / 2.9 + 0.4),
        "AI 1/U3": 230.4 + 1.1 * math.sin(t / 3.0 + 0.8),
        "AI 1/I1": 8.2 + 0.4 * math.sin(t / 2.4),
        "AI 1/I2": 8.1 + 0.35 * math.sin(t / 2.5 + 0.3),
        "AI 1/I3": 8.3 + 0.38 * math.sin(t / 2.6 + 0.6),
        "P_t@POWER/0": 5600.0 + 80.0 * math.sin(t / 3.5),
        "Q_fund@POWER/0": 120.0 + 15.0 * math.sin(t / 4.0),
        "PF@POWER/0": 0.975 + 0.01 * math.sin(t / 5.0),
        "F@POWER/0": 50.0 + 0.05 * math.sin(t / 6.0),
    }


def main() -> int:
    app = QtWidgets.QApplication(sys.argv)
    page = LiveMeasurePage()
    page.setWindowTitle("实时测量 · 模拟（无仪器）")
    page.resize(1320, 860)
    page.show()

    state = {"n": 0, "mode": "wt"}

    def feed() -> None:
        state["n"] += 1
        n = state["n"]
        page._polling = True
        page.btn_start.setText("停止查看")
        if state["mode"] == "wt":
            page.radio_wt.setChecked(True)
            page._kind = "wt"
            sample = _fake_wt(n)
            page._apply_sample(sample, f"模拟 WT Soft Panel · 第 {n} 帧（无真机）")
            if n == 40:
                path = OUT / "live_measure_sim_wt.png"
                page.grab().save(str(path), "PNG")
                print(f"saved {path}")
                state["mode"] = "dew"
                state["n"] = 0
                page._history.clear()
                page._color_of.clear()
                page._clear_values()
                page.radio_dew.setChecked(True)
                page._kind = "dew"
        else:
            if n == 1:
                page._clear_checks()
                for name in _fake_dew(1):
                    page._add_check(name, name, True)
            sample = _fake_dew(n)
            page._apply_sample(sample, f"模拟 德威创 Oxygen 通道 · 第 {n} 帧（无真机）")
            if n == 40:
                path = OUT / "live_measure_sim_dew.png"
                page.grab().save(str(path), "PNG")
                print(f"saved {path}")
                timer.stop()
                app.quit()

    page._kick = lambda: None  # type: ignore[method-assign]
    page._timer.stop()

    timer = QtCore.QTimer()
    timer.setInterval(80)
    timer.timeout.connect(feed)
    QtCore.QTimer.singleShot(200, timer.start)
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
