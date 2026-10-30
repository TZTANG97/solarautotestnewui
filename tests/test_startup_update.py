# -*- coding: utf-8 -*-
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.startup_update import _channel, _digits


def test_version_digits_order():
    assert _digits("20261029.1852") > _digits("20261029.1619")
    assert _digits("0.1.0") < _digits("20261029.1619")


def test_missing_channel_falls_back_to_oss(tmp_path):
    assert _channel(tmp_path).startswith("https://qgongye.oss-cn-shanghai.aliyuncs.com/")


def test_disabled_channel_skips(tmp_path):
    cfg = tmp_path / "config_files"
    cfg.mkdir()
    (cfg / "config.ini").write_text("[update]\nenabled = 0\nchannel = https://example.com\n", encoding="utf-8")
    assert _channel(tmp_path) == ""
