# -*- coding: utf-8 -*-
"""模拟测试：功率分析仪「宏 / SCPI」模式接入（无真机）。"""
from __future__ import annotations

import os
import sys
import time

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5 import QtWidgets

from components.wt_config_content import (
    build_wt1800_content,
    build_wt1806e_content,
    build_wt3000_content,
    build_wt5000_content,
)
from devices.wt_data_collector import WtScpiCollector
from utils.Open_Save_ThaiWT3000_Config import WT3000E_params_config
from utils.Open_Save_ThaiXieBoDianLiu import _PageWidgetFinder
from utils.wt_acquire_mode import (
    MODE_MACRO,
    MODE_SCPI,
    is_scpi_mode,
    rate_text_from_config,
    resolve_csv_path,
)
from utils import wt_scpi_session


@pytest.fixture(scope="module")
def qapp():
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    return app


class _FakeHandle:
    def __init__(self):
        self.writes = []
        self._rate = "100MS"
        self._items = {}
        self._number = 0

    def write(self, cmd):
        self.writes.append(cmd)
        u = cmd.upper()
        if u.startswith(":RATE"):
            self._rate = cmd.split(None, 1)[1]
        elif ":NUMERIC:NORMAL:NUMBER" in u or ":NUMERIC:NORMAL:NUM" in u:
            try:
                self._number = int(cmd.rsplit(None, 1)[-1])
            except ValueError:
                pass
        elif ":NUMERIC:NORMAL:ITEM" in u and "?" not in cmd:
            # :NUMERIC:NORMAL:ITEM3 URMS,1
            parts = cmd.split(None, 1)
            key = parts[0]
            self._items[key.upper()] = parts[1] if len(parts) > 1 else ""

    def query(self, cmd):
        u = cmd.upper().strip()
        if u.startswith(":RATE?"):
            return f":RATE {self._rate}"
        if u.startswith(":NUMERIC:NORMAL:ITEM") and u.endswith("?"):
            key = u[:-1]
            for k, v in self._items.items():
                if k.upper() == key or key.endswith(k.split("ITEM")[-1] if "ITEM" in k else ""):
                    pass
            # Match ITEM{n}?
            for k, v in self._items.items():
                if k.upper().rstrip() == u[:-1] or k.upper() == cmd.split("?")[0].upper():
                    return v
            # fallback: find by suffix
            for k, v in self._items.items():
                if k.upper().endswith(u.replace("?", "").split("ITEM")[-1].upper() if "ITEM" in u else "XX"):
                    return v
            # Direct: ITEM3?
            token = u.replace("?", "")
            for k, v in self._items.items():
                if token in k.upper() or k.upper().endswith(token.split("NORMAL:")[-1]):
                    return v
            return list(self._items.values())[0] if self._items else ""
        if "VALUE?" in u:
            n = max(self._number, len(self._items), 1)
            return ",".join(str(100 + i) for i in range(n))
        return ""


class _FakeCtrl:
    def __init__(self):
        self.handle = _FakeHandle()
        self.connected = True
        self.resource = "TCPIP0::127.0.0.1::10001::SOCKET"


def test_acquire_mode_default_macro_on_all_wt_pages(qapp):
    host = QtWidgets.QWidget()
    pages = [
        build_wt3000_content(host),
        build_wt1800_content(host),
        build_wt1806e_content(host),
        build_wt5000_content(host),
    ]
    for page in pages:
        finder = _PageWidgetFinder(page)
        combo = finder.comboBox_wt_acquire_mode
        assert combo.currentData() == MODE_MACRO
        combo.setCurrentIndex(1)
        assert combo.currentData() == MODE_SCPI


def test_params_config_injects_scpi_mode(qapp, tmp_path):
    host = QtWidgets.QWidget()
    page = build_wt3000_content(host)
    finder = _PageWidgetFinder(page)
    finder.comboBox_wt_acquire_mode.setCurrentIndex(1)
    finder.comboBox_ReplaceRate.setCurrentIndex(0)  # 50ms
    finder.textEdit_StopTime.setPlainText("00:00:02")
    finder.textEdit_SavePath.setPlainText(str(tmp_path))
    finder.textEdit_FileNameList.setPlainText("SimSCPI")
    # Minimal checkboxes used by params_config — already created by builder
    params = WT3000E_params_config(finder)
    assert params["wt_acquire_mode"] == MODE_SCPI
    assert is_scpi_mode(params)
    assert rate_text_from_config(params) == "50ms"
    assert resolve_csv_path(params).endswith("SimSCPI.csv")


def test_params_config_default_macro(qapp):
    host = QtWidgets.QWidget()
    page = build_wt3000_content(host)
    finder = _PageWidgetFinder(page)
    params = WT3000E_params_config(finder)
    assert params.get("wt_acquire_mode") == MODE_MACRO
    assert not is_scpi_mode(params)


def test_scpi_session_with_fake_instrument(qapp, tmp_path, monkeypatch):
    ctrl = _FakeCtrl()
    monkeypatch.setattr(wt_scpi_session, "_get_controller", lambda: ctrl)
    wt_scpi_session.shutdown()

    config = {
        "wt_acquire_mode": MODE_SCPI,
        "comboBox_ReplaceRate": 0,  # 50ms
        "textEdit_StopTime": "00:00:01",
        "textEdit_SavePath": str(tmp_path),
        "textEdit_FileNameList": "BenchFake",
    }
    ok, err = wt_scpi_session.prepare_from_config(config)
    assert ok, err

    # Improve ITEM? matching for fake: make query return stored item text
    handle = ctrl.handle

    def _query(cmd):
        u = cmd.upper().strip()
        if u.startswith(":RATE?"):
            return f":RATE {handle._rate}"
        if "VALUE?" in u:
            n = max(handle._number, 3)
            return ",".join(f"{1.0 + i * 0.1:.3f}" for i in range(n))
        if u.startswith(":NUMERIC:NORMAL:ITEM") and u.endswith("?"):
            key = cmd.split("?")[0]
            for k, v in handle._items.items():
                if k.upper() == key.upper():
                    return v
            # Accept any written item
            return next(iter(handle._items.values()), "URMS,1")
        return ""

    handle.query = _query
    ok2, err2 = wt_scpi_session.prepare_from_config(config)
    assert ok2, err2

    started = time.time()
    assert wt_scpi_session.run_measure_blocking(config, file_index=0)
    elapsed = time.time() - started
    assert elapsed < 5.0
    csv_path = wt_scpi_session.last_csv()
    assert csv_path and os.path.isfile(csv_path)
    with open(csv_path, encoding="utf-8-sig") as f:
        lines = f.read().strip().splitlines()
    assert len(lines) >= 2  # header + ≥1 row
    # RATE command was sent
    assert any(":RATE" in w.upper() and "50" in w.upper() for w in handle.writes)
    wt_scpi_session.shutdown()


def test_scpi_session_uses_checkbox_items(qapp, tmp_path, monkeypatch):
    ctrl = _FakeCtrl()
    monkeypatch.setattr(wt_scpi_session, "_get_controller", lambda: ctrl)
    wt_scpi_session.shutdown()

    config = {
        "wt_acquire_mode": MODE_SCPI,
        "Style": "Thai_WT3000E_Config",
        "comboBox_ReplaceRate": 0,
        "comboBox_ProjectNum": 1,
        "textEdit_StopTime": "00:00:01",
        "textEdit_SavePath": str(tmp_path),
        "textEdit_FileNameList": "FromChecks",
        "checkBox_SetElement1": "1",
        "checkBox_SetElement2": "1",
        "checkBox_SetU": "1",
        "checkBox_SetP": "1",
    }

    handle = ctrl.handle

    def _query(cmd):
        u = cmd.upper().strip()
        if u.startswith(":RATE?"):
            return f":RATE {handle._rate}"
        if "VALUE?" in u:
            n = max(handle._number, 1)
            return ",".join(f"{1.0 + i}" for i in range(n))
        if u.startswith(":NUMERIC:NORMAL:ITEM") and u.endswith("?"):
            key = cmd.split("?")[0]
            for k, v in handle._items.items():
                if k.upper() == key.upper():
                    return v
            return next(iter(handle._items.values()), "URMS,1")
        return ""

    handle.query = _query
    ok, err = wt_scpi_session.prepare_from_config(config)
    assert ok, err
    written = " | ".join(handle.writes)
    assert "URMS,1" in written
    assert "URMS,2" in written
    assert "P,1" in written
    assert "P,2" in written
    # Should NOT dump full default FU/SIGMA set when user only picked U+P on el1/2
    assert "FU,1" not in written
    wt_scpi_session.shutdown()


def test_upper_wt_config_scpi_skips_macro_flag():
    """配置含 scpi 时，校验逻辑应要求 WT3000 连接（仅测 is_scpi_mode 契约）。"""
    cfg = {"wt_acquire_mode": "scpi", "comboBox_ReplaceRate": 1}
    assert is_scpi_mode(cfg)
    assert not is_scpi_mode({"wt_acquire_mode": "macro"})
    assert not is_scpi_mode({})
