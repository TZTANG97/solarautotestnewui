# -*- coding: utf-8 -*-
from utils.dc_channels import (
    add_channel,
    channel_numbers,
    extend_setting_headers,
    parse_dc_token,
)


def test_default_channels_are_four(monkeypatch, tmp_path):
    monkeypatch.setattr("utils.dc_channels._CONFIG", tmp_path / "missing.json")
    assert channel_numbers() == [1, 2, 3, 4]


def test_add_channel_appends_next(monkeypatch, tmp_path):
    monkeypatch.setattr("utils.dc_channels._CONFIG", tmp_path / "dc_channels.json")
    assert add_channel() == 5
    assert add_channel() == 6
    assert channel_numbers() == [1, 2, 3, 4, 5, 6]


def test_extra_headers_append_after_existing_columns(monkeypatch, tmp_path):
    monkeypatch.setattr("utils.dc_channels._CONFIG", tmp_path / "dc_channels.json")
    add_channel()
    headers = extend_setting_headers(["Style", "checkBox_S1_DC1", "checkBox_S1_DC4"])
    assert headers[:3] == ["Style", "checkBox_S1_DC1", "checkBox_S1_DC4"]
    assert headers[-1] == "comboBox_S_END_DC5"
    assert "checkBox_S1_DC5" in headers


def test_parse_dc_token():
    assert parse_dc_token("DC5") == 5
    assert parse_dc_token("dc12") == 12
    assert parse_dc_token("AC") == 0
    assert parse_dc_token("DC") == 0
