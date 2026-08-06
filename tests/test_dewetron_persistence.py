# -*- coding: utf-8 -*-
"""Persistence adapter coverage for the eleven approved AutoTest utilities."""

import importlib
import json
from types import SimpleNamespace

import pytest

from components.dewetron_autotest_panel import DewetronUiConfig
from dewetron_autotest import DEWETRON_CONFIG_COLUMN, MODE_DEWETRON, MODE_WT


UTILITY_CASES = (
    ("utils.Open_Save_ThaiChongLian", "reconnection"),
    ("utils.Open_Save_ThaiOverLoads", "overload-capability"),
    ("utils.Open_Save_ThaiZhiLiuFenLiang", "dc-component"),
    ("utils.Open_Save_ThaiStaticQU", "static-qu"),
    ("utils.Open_Save_ThaitestPU", "test-pu"),
    ("utils.Open_Save_ThaiStaticCosPhi", "static-cos-phi"),
    ("utils.Open_Save_ThaiCosPhiBrazil", "cos-phi-brazil"),
    ("utils.Open_Save_ThaiVoltProtect10min", "overvoltage-protection-10min"),
    ("utils.Open_Save_ThaiGuoPinJiangZai", "overfrequency-derating"),
    ("utils.Open_Save_ThaiGuoQianYa_Pin", "voltage-frequency-protection"),
    ("utils.Open_Save_ThaiGuoQianPin_Immun", "brazil-frequency-immunity"),
)


class FakeAnalyzerSection:
    """Small adapter double matching AnalyzerModeSection's persistence API."""

    def __init__(self, mode=MODE_DEWETRON, config=None):
        self.mode = mode
        self.config = config or DewetronUiConfig("20", 4, True, ["P_t"])
        self.restored_mode = None
        self.restored_config = None

    def get_dewetron_config(self):
        return self.config

    def set_dewetron_config(self, config):
        self.restored_config = config

    def set_mode(self, mode):
        self.restored_mode = mode
        self.mode = mode


def _ui(section=True):
    if section:
        return SimpleNamespace(analyzerModeSection=FakeAnalyzerSection())
    return SimpleNamespace()


@pytest.mark.parametrize("module_name, expected_test_type", UTILITY_CASES)
def test_every_utility_imports_and_named_tail_is_idempotent(
    module_name, expected_test_type
):
    module = importlib.import_module(module_name)
    existing_tail_count = module.arrayRow1.count(DEWETRON_CONFIG_COLUMN)
    legacy_header_length = len(module.arrayRow1) - existing_tail_count
    values = [""] * legacy_header_length

    # The immunity utility's stale legacy header had no corresponding value.
    if module_name.endswith("ThaiGuoQianPin_Immun"):
        values.pop(module.arrayRow1.index("pushButton_S2_WT_CONFIG"))

    ui = _ui()
    module._append_dewetron_tail(values, ui)
    module._append_dewetron_tail(values, ui)

    assert module.arrayRow1.count(DEWETRON_CONFIG_COLUMN) == 1
    assert len(module.arrayRow1) == legacy_header_length + 1
    assert len(values) == len(module.arrayRow1)
    payload = json.loads(values[module.arrayRow1.index(DEWETRON_CONFIG_COLUMN)])
    assert payload["mode"] == MODE_DEWETRON
    assert payload["test_type"] == expected_test_type
    assert payload["rate_text"] == "20"


@pytest.mark.parametrize("module_name, _expected_test_type", UTILITY_CASES)
def test_old_rows_restore_wt_defaults_and_older_ui_is_safe(
    module_name, _expected_test_type
):
    module = importlib.import_module(module_name)
    headers = ["Style", "checkBox_S1"]
    values = ["legacy-project", "1"]

    mode, config = module._restore_dewetron_tail(headers, values, _ui(section=False))

    assert mode == MODE_WT
    assert config == DewetronUiConfig()


@pytest.mark.parametrize("module_name, _expected_test_type", UTILITY_CASES)
def test_named_tail_restores_mode_and_config_through_analyzer_section(
    module_name, _expected_test_type
):
    module = importlib.import_module(module_name)
    source_ui = _ui()
    values = [""] * len(module.arrayRow1)
    module._append_dewetron_tail(values, source_ui)

    target = FakeAnalyzerSection(mode=MODE_WT, config=DewetronUiConfig())
    mode, config = module._restore_dewetron_tail(
        module.arrayRow1, values, SimpleNamespace(analyzerModeSection=target)
    )

    assert mode == MODE_DEWETRON
    assert config == source_ui.analyzerModeSection.config
    assert target.restored_mode == MODE_DEWETRON
    assert target.restored_config == source_ui.analyzerModeSection.config


def test_immunity_current_malformed_legacy_row_is_aligned_non_destructively():
    module = importlib.import_module("utils.Open_Save_ThaiGuoQianPin_Immun")
    legacy_headers = [
        header
        for header in module.arrayRow1
        if header != DEWETRON_CONFIG_COLUMN
    ]
    stale_index = legacy_headers.index("pushButton_S2_WT_CONFIG")
    malformed_values = [f"value-{index}" for index in range(len(legacy_headers) - 1)]
    value_after_gap = malformed_values[stale_index]

    module._align_legacy_project_row(legacy_headers, malformed_values)

    assert len(malformed_values) == len(legacy_headers)
    assert malformed_values[stale_index] == ""
    assert malformed_values[stale_index + 1] == value_after_gap
    mode, config = module._restore_dewetron_tail(
        legacy_headers, malformed_values, _ui(section=False)
    )
    assert mode == MODE_WT
    assert config == DewetronUiConfig()


def test_immunity_new_tail_follows_aligned_legacy_placeholder():
    module = importlib.import_module("utils.Open_Save_ThaiGuoQianPin_Immun")
    legacy_header_length = len(module.arrayRow1) - int(
        DEWETRON_CONFIG_COLUMN in module.arrayRow1
    )
    values = [""] * (legacy_header_length - 1)

    module._append_dewetron_tail(values, _ui())

    stale_index = module.arrayRow1.index("pushButton_S2_WT_CONFIG")
    assert values[stale_index] == ""
    assert module.arrayRow1[-1] == DEWETRON_CONFIG_COLUMN
    assert len(values) == len(module.arrayRow1)
