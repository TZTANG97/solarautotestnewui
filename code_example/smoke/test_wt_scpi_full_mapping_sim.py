# -*- coding: utf-8 -*-
"""全量模拟：四机型 UI 勾选 → params → SCPI ITEM 映射 → 假仪器采数。"""
from __future__ import annotations

import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject

from components.wt_config_content import (
    build_wt1800_content,
    build_wt1806e_content,
    build_wt3000_content,
    build_wt5000_content,
)
from utils.Open_Save_ThaiWT1800_Config import WT1800_params_config
from utils.Open_Save_ThaiWT1806E_Config import WT1806E_params_config
from utils.Open_Save_ThaiWT3000_Config import WT3000E_params_config
from utils.Open_Save_ThaiWT5000_Config import WT5000_params_config
from utils.Open_Save_ThaiXieBoDianLiu import _PageWidgetFinder
from utils.wt_acquire_mode import MODE_MACRO, MODE_SCPI, is_scpi_mode
from utils.wt_scpi_items import all_known_checkbox_keys, items_from_wt_config
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
            parts = cmd.split(None, 1)
            self._items[parts[0].upper()] = parts[1] if len(parts) > 1 else ""

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


def _tick_common(finder):
    finder.comboBox_wt_acquire_mode.setCurrentIndex(1)
    finder.comboBox_ReplaceRate.setCurrentIndex(0)
    finder.comboBox_ProjectNum.setCurrentIndex(2)  # 48
    finder.textEdit_StopTime.setPlainText("00:00:01")
    out = os.path.join(ROOT, "code_example", "media")
    os.makedirs(out, exist_ok=True)
    finder.textEdit_SavePath.setPlainText(out)
    finder.textEdit_FileNameList.setPlainText("wt_scpi_full_sim")

    # Tick every checkBox_Set* that exists on this page (except AutoName)
    for cb in finder._page.findChildren(QtWidgets.QCheckBox):
        name = cb.objectName() or ""
        if not name.startswith("checkBox_Set"):
            continue
        if name == "checkBox_AutoName":
            continue
        cb.setChecked(True)


def _run_one(label, build_fn, params_fn):
    host = QtWidgets.QWidget()
    page = build_fn(host)
    finder = _PageWidgetFinder(page)
    assert finder.comboBox_wt_acquire_mode.currentData() == MODE_MACRO
    _tick_common(finder)
    params = params_fn(finder)
    assert is_scpi_mode(params), label
    items = items_from_wt_config(params)
    print(f"[{label}] mapped {len(items)} items; head={items[:6]}")
    assert len(items) >= 5, label
    assert any("URMS" in x or x.startswith("P,") for x in items), label
    return params, items


def main():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    # 1) 分类表覆盖 Open_Save 全部勾选键
    print("known keys:", len(all_known_checkbox_keys()))

    cases = [
        ("WT3000E", build_wt3000_content, WT3000E_params_config),
        ("WT1800", build_wt1800_content, WT1800_params_config),
        ("WT1806E", build_wt1806e_content, WT1806E_params_config),
        ("WT5000", build_wt5000_content, WT5000_params_config),
    ]
    last_params = None
    for label, build_fn, params_fn in cases:
        last_params, _ = _run_one(label, build_fn, params_fn)

    # 2) 假仪器走通 prepare + 采数（用 WT3000 全勾配置）
    ctrl = _C()
    wt_scpi_session.shutdown()
    wt_scpi_session._get_controller = lambda: ctrl  # type: ignore
    ok, err = wt_scpi_session.prepare_from_config(last_params)
    print("prepare:", ok, err)
    assert ok, err
    assert wt_scpi_session.run_measure_blocking(last_params)
    csv_path = wt_scpi_session.last_csv()
    print("csv:", csv_path)
    assert csv_path and os.path.isfile(csv_path)
    with open(csv_path, encoding="utf-8-sig") as f:
        header = f.readline().strip()
    print("csv header cols:", len(header.split(",")))
    wt_scpi_session.shutdown()
    print("PASS: full checkbox mapping + four WT pages + fake SCPI acquire")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
