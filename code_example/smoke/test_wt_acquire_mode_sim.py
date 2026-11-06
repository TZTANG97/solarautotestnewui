# -*- coding: utf-8 -*-
"""一次性模拟：UI 模式选择 → params → SCPI 假仪器采集全程。"""
from __future__ import annotations

import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5 import QtWidgets

from components.wt_config_content import build_wt3000_content
from utils.Open_Save_ThaiWT3000_Config import WT3000E_params_config
from utils.Open_Save_ThaiXieBoDianLiu import _PageWidgetFinder
from utils.wt_acquire_mode import MODE_MACRO, MODE_SCPI, is_scpi_mode
from utils import wt_scpi_session


class _H:
    def __init__(self):
        self.writes = []
        self._rate = "50MS"
        self._items = {}
        self._number = 0

    def write(self, cmd):
        self.writes.append(cmd)
        u = cmd.upper()
        if u.startswith(":RATE"):
            self._rate = cmd.split(None, 1)[1]
        elif "NUMBER" in u and "?" not in cmd:
            try:
                self._number = int(cmd.rsplit(None, 1)[-1])
            except ValueError:
                pass
        elif "ITEM" in u and "?" not in cmd:
            self._items[cmd.split(None, 1)[0].upper()] = cmd.split(None, 1)[1]

    def query(self, cmd):
        u = cmd.upper()
        if u.startswith(":RATE?"):
            return f":RATE {self._rate}"
        if "VALUE?" in u:
            n = max(self._number, 3)
            return ",".join(f"{i+1}.0" for i in range(n))
        if "ITEM" in u and u.endswith("?"):
            key = cmd.split("?")[0].upper()
            for k, v in self._items.items():
                if k == key:
                    return v
            return next(iter(self._items.values()), "URMS,1")
        return ""


class _C:
    def __init__(self):
        self.handle = _H()
        self.connected = True
        self.resource = "TCPIP0::192.168.1.10::10001::SOCKET"


def main():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    host = QtWidgets.QWidget()
    page = build_wt3000_content(host)
    finder = _PageWidgetFinder(page)

    print("1) 默认模式:", finder.comboBox_wt_acquire_mode.currentText())
    assert finder.comboBox_wt_acquire_mode.currentData() == MODE_MACRO

    finder.comboBox_wt_acquire_mode.setCurrentIndex(1)
    finder.comboBox_ReplaceRate.setCurrentIndex(0)
    finder.comboBox_ProjectNum.setCurrentIndex(2)  # 48，避免勾选过多被截断
    finder.textEdit_StopTime.setPlainText("00:00:01")
    out_dir = os.path.join(ROOT, "code_example", "media")
    os.makedirs(out_dir, exist_ok=True)
    finder.textEdit_SavePath.setPlainText(out_dir)
    finder.textEdit_FileNameList.setPlainText("wt_scpi_sim")
    # 勾选 Element1-3 + U/I/P/Q/FreqU，验证映射进 NUMERIC
    for name in (
        "checkBox_SetElement1",
        "checkBox_SetElement2",
        "checkBox_SetElement3",
        "checkBox_SetSigma",
        "checkBox_SetU",
        "checkBox_SetI",
        "checkBox_SetP",
        "checkBox_SetQ",
        "checkBox_SetFreqU",
    ):
        getattr(finder, name).setChecked(True)

    params = WT3000E_params_config(finder)
    print("2) params wt_acquire_mode:", params.get("wt_acquire_mode"))
    assert is_scpi_mode(params)
    from utils.wt_scpi_items import items_from_wt_config

    mapped = items_from_wt_config(params)
    print("2b) mapped items:", mapped[:8], "... total", len(mapped))
    assert "URMS,1" in mapped and "P,SIGMA" in mapped and "FU,1" in mapped

    # 模拟 Upper_WT_Config 分流：SCPI 不应需要 WTViewer
    print("3) Upper_WT_Config 将跳过宏:", is_scpi_mode(params))

    ctrl = _C()
    wt_scpi_session.shutdown()
    wt_scpi_session._get_controller = lambda: ctrl  # type: ignore
    ok, err = wt_scpi_session.prepare_from_config(params)
    print("4) prepare:", ok, err)
    assert ok, err
    t0 = time.time()
    assert wt_scpi_session.run_measure_blocking(params)
    print("5) measure elapsed:", round(time.time() - t0, 2), "s")
    csv_path = wt_scpi_session.last_csv()
    print("6) csv:", csv_path)
    assert csv_path and os.path.isfile(csv_path)
    with open(csv_path, encoding="utf-8-sig") as f:
        n = len(f.read().strip().splitlines())
    print("7) csv lines:", n)
    assert n >= 2
    wt_scpi_session.shutdown()
    print("PASS: 宏默认保留 + SCPI 模式贯通 + 假仪器采数导出")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
