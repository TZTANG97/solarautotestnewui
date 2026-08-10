# -*- coding: utf-8 -*-
"""Headless tests for the shared DEWETRON AutoTest foundation."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5 import QtWidgets
import pytest

from app.context import AppContext
from components import (
    AnalyzerModeSection,
    DewetronAutoTestPanel,
    DewetronUiConfig,
    parse_power_group_tree,
)
from dewetron_autotest import (
    COMMAND_ROW_LENGTH,
    DEWETRON_CONFIG_COLUMN,
    DEWETRON_START_COMMAND,
    DEWETRON_STOP_COMMAND,
    ELIGIBLE_PROJECT_NAMES,
    MODE_DEWETRON,
    MODE_WT,
    PROFILE_HARMONIC,
    PROJECT_SPECS,
    WAIT_DEVICE,
    DewetronAutoTestCoordinator,
    append_dewetron_tail_columns,
    coerce_command_row,
    config_fingerprint,
    make_wait_row,
    get_project_spec,
    normalize_dewetron_command_segment,
    parse_dewetron_config,
    read_dewetron_tail_columns,
    serialize_dewetron_config,
)


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


POWER_GROUP_XML = """
noise-before-xml
<MeasurementConfig>
  <ChannelGroup Type="Power Groups">
    <Channel id="1" Name="POWER/0">
      <ChannelGroup Type="Voltage (U)">
        <ChannelGroup Type="Total RMS">
          <Channel Name="U1_tRMS"/>
          <Channel Name="U2_tRMS"/>
        </ChannelGroup>
        <Channel Name="F_fund"/>
        <ChannelGroup Type="Advanced">
          <Channel Name="hidden"/>
        </ChannelGroup>
      </ChannelGroup>
      <ChannelGroup Type="Current (I)">
        <ChannelGroup Type="Total RMS">
          <Channel Name="I1_tRMS"/>
        </ChannelGroup>
      </ChannelGroup>
    </Channel>
  </ChannelGroup>
</MeasurementConfig>
"""


def test_project_specs_are_stable_and_exclude_ineligible_projects():
    assert ELIGIBLE_PROJECT_NAMES == (
        "重连",
        "过载能力测试",
        "直流分量",
        "静态QU",
        "无功能力范围",
        "定无功",
        "无功注入",
        "无功精度",
        "有功调度",
        "Test_PU",
        "静态Cos(φ)",
        "动态Cos(φ)",
        "动态QU",
        "Cos(φ)_Brazil",
        "10min过压保护",
        "过频降载",
        "欠频升载",
        "过欠压_过欠频",
        "巴西过欠频稳定性",
        "频率适应性",
        "电压适应性",
        "ROCOF保护",
        "快速电压变化",
    )
    assert "固定PF=1" not in PROJECT_SPECS
    assert "MPPT" not in PROJECT_SPECS
    assert "频率适应性" in PROJECT_SPECS
    assert PROJECT_SPECS["频率适应性"].test_type == "frequency-adaptability"
    assert PROJECT_SPECS["电压适应性"].test_type == "voltage-adaptability"
    assert PROJECT_SPECS["ROCOF保护"].test_type == "rocof-protection"
    assert PROJECT_SPECS["快速电压变化"].test_type == "rapid-voltage-change"
    assert PROJECT_SPECS["谐波电流"].profile == PROFILE_HARMONIC
    assert PROJECT_SPECS["电压闪变"].test_type == "flicker"
    assert get_project_spec("overloads").project_name == "过载能力测试"
    assert get_project_spec("cos-phi-brazil").project_name == "Cos(φ)_Brazil"


def test_config_json_legacy_parsing_and_fingerprint():
    config = DewetronUiConfig("50", 4, True, ["U1_tRMS", "I1_tRMS"])
    encoded = serialize_dewetron_config(
        config, test_type="reconnection", profile="generic"
    )
    assert parse_dewetron_config(encoded) == config
    assert parse_dewetron_config("dewetron|20|2|1|P_t|U1_tRMS") == DewetronUiConfig(
        "20", 2, True, ["P_t", "U1_tRMS"]
    )
    assert parse_dewetron_config(
        {
            "comboBox_DEW_MaxRefreshRate": "100",
            "spinBox_DEW_DecimalPlaces": "3",
            "checkBox_DEW_RealtimeWaveform": "0",
            "DEW_ExportFields": "U1_tRMS|I1_tRMS",
        }
    ) == DewetronUiConfig("100", 3, False, ["U1_tRMS", "I1_tRMS"])

    # Selection order does not change append semantics.
    assert config_fingerprint(config, test_type="reconnection") == config_fingerprint(
        DewetronUiConfig("50", 4, True, ["I1_tRMS", "U1_tRMS"]),
        test_type="reconnection",
    )


def test_named_tail_column_helpers_are_backward_compatible():
    headers = ["Style", "checkBox_S1"]
    values = ["ThaiChonglian", "1"]
    config = DewetronUiConfig("20", 5, True, ["P_t"])
    append_dewetron_tail_columns(
        headers, values, config, mode=MODE_DEWETRON, test_type="reconnection"
    )
    assert headers[-1] == DEWETRON_CONFIG_COLUMN
    mode, restored = read_dewetron_tail_columns(headers, values)
    assert mode == MODE_DEWETRON
    assert restored == config

    # Unequal legacy header/value rows retain their unlabelled tail values.
    short_headers = ["Style"]
    long_values = ["ThaiLegacy", "unlabelled-a", "unlabelled-b"]
    append_dewetron_tail_columns(short_headers, long_values, config)
    assert short_headers == ["Style", DEWETRON_CONFIG_COLUMN]
    assert long_values[2:] == ["unlabelled-a", "unlabelled-b"]
    assert parse_dewetron_config(long_values[1]) == config

    # Existing legacy files with no named tail stay valid and receive defaults.
    legacy_mode, legacy_config = read_dewetron_tail_columns(
        ["Style"], ["ThaiChonglian"]
    )
    assert legacy_mode == MODE_WT
    assert legacy_config == DewetronUiConfig()


def test_command_normalization_uses_explicit_boundaries_and_policy():
    rows = [
        ["AC", "write", "VOLT 230", "", "", "", 99, 98, 5, 6],
        ["Upper_WT_Config", "", "", "config_dict", {"x": 1}],
        ["DC1", "write", "OUTP ON", "", "", "", 77, 76, 8, 9],
        ["WT", "macro.json", "", "", "", "", "", 7],
        ["AC", "wait", "", "", "", "", "", "", "", 10],
    ]

    def replace_known_wt_dwell(removed):
        # Only the WT macro row's column 7 is known by this project to be a
        # 0.1-second dwell. Upper_WT_Config has no replacement.
        if removed.device.upper() == "WT" and removed.row[7] != "":
            return make_wait_row(removed.row[7])
        return None

    result = normalize_dewetron_command_segment(
        rows,
        start_index=1,
        stop_index=3,
        wt_row_policy=replace_known_wt_dwell,
        return_metadata=True,
    )

    assert all(len(row) == COMMAND_ROW_LENGTH for row in result.rows)
    assert [row[0] for row in result.rows] == [
        "AC",
        "DEWETRON",
        "DC1",
        WAIT_DEVICE,
        "DEWETRON",
        "AC",
    ]
    assert result.rows[1][2] == DEWETRON_START_COMMAND
    assert result.rows[4][2] == DEWETRON_STOP_COMMAND
    assert result.rows[3][:3] == ["AC", "wait", ""]
    assert result.rows[3][9] == 7
    assert [item.device for item in result.removed_wt_rows] == [
        "Upper_WT_Config",
        "WT",
    ]
    # WT trigger columns are cleared, while branch-specific columns 8/9 on
    # retained rows remain untouched.
    assert result.rows[0][6:10] == ["", "", 5, 6]
    assert result.rows[2][6:10] == ["", "", 8, 9]


def test_command_normalization_rejects_ambiguous_or_combined_input():
    with pytest.raises(ValueError, match="start_index"):
        normalize_dewetron_command_segment([["AC", "query", "*IDN?"]])
    with pytest.raises(ValueError, match="already contains"):
        normalize_dewetron_command_segment(
            [["DEWETRON", "write", DEWETRON_START_COMMAND]],
            start_index=0,
            stop_index=0,
        )
    with pytest.raises(ValueError, match="11 columns"):
        coerce_command_row([""] * 11)

    # Disabled/WT mode only pads rows and does not require acquisition markers.
    assert normalize_dewetron_command_segment(
        [["AC", "query", "*IDN?"]], enabled=False
    )[0][:3] == ["AC", "query", "*IDN?"]


def test_power_group_parser_does_not_depend_on_flicker_dialog():
    tree = parse_power_group_tree(POWER_GROUP_XML)
    assert tree == {
        "Voltage (U)": {
            "Total RMS": ["U1_tRMS", "U2_tRMS"],
            "_default_": ["F_fund"],
        },
        "Current (I)": {"Total RMS": ["I1_tRMS"]},
    }
    assert parse_power_group_tree("<MeasurementConfig/>") is None
    assert parse_power_group_tree("not xml") is None


def test_panel_pending_field_restoration_and_signals(qapp):
    panel = DewetronAutoTestPanel()
    panel.set_config(DewetronUiConfig("20", 2, True, ["U2_tRMS", "I1_tRMS"]))
    assert panel.get_checked_export_fields() == ["U2_tRMS", "I1_tRMS"]

    panel.refresh_power_groups(POWER_GROUP_XML)
    assert panel.get_checked_export_fields() == ["U2_tRMS", "I1_tRMS"]
    assert panel.unavailable_export_fields() == []
    assert panel.get_config() == DewetronUiConfig(
        "20", 2, True, ["U2_tRMS", "I1_tRMS"]
    )
    assert panel.validate_config() == []

    calls = {"apply": 0, "refresh": 0, "viewer": 0}
    panel.apply_requested.connect(lambda: calls.__setitem__("apply", calls["apply"] + 1))
    panel.refresh_requested.connect(
        lambda: calls.__setitem__("refresh", calls["refresh"] + 1)
    )
    panel.viewer_requested.connect(
        lambda: calls.__setitem__("viewer", calls["viewer"] + 1)
    )
    panel.apply_button.click()
    panel.refresh_button.click()
    panel.viewer_button.click()
    assert calls == {"apply": 1, "refresh": 1, "viewer": 1}

    panel.set_checked_export_fields(["U1_tRMS", "missing_saved_field"])
    panel.refresh_power_groups(POWER_GROUP_XML)
    assert panel.get_checked_export_fields() == ["U1_tRMS"]
    assert panel.unavailable_export_fields() == ["missing_saved_field"]

    # A genuinely fresh panel has no saved selection and follows the legacy
    # convention of selecting every available leaf.
    fresh = DewetronAutoTestPanel()
    fresh.refresh_power_groups(POWER_GROUP_XML)
    assert fresh.get_checked_export_fields() == [
        "U1_tRMS",
        "U2_tRMS",
        "F_fund",
        "I1_tRMS",
    ]


def test_analyzer_mode_section_moves_checkbox_stacks_pages_and_links_enabled(qapp):
    old_parent = QtWidgets.QWidget()
    old_layout = QtWidgets.QVBoxLayout(old_parent)
    step_checkbox = QtWidgets.QCheckBox("step2")
    step_checkbox.setChecked(True)
    wt_widget = QtWidgets.QWidget()
    old_layout.addWidget(step_checkbox)
    old_layout.addWidget(wt_widget)

    section = AnalyzerModeSection(wt_widget, step_checkbox)
    assert section.mode == MODE_WT
    assert section.analyzer_stack.currentWidget() is wt_widget
    assert step_checkbox.parentWidget() is section.mode_row

    section.set_mode(MODE_DEWETRON)
    assert section._mode == MODE_DEWETRON
    assert section.analyzer_stack.currentWidget() is section.dewetron_panel
    step_checkbox.setChecked(False)
    assert not section.analyzer_stack.isEnabled()
    assert step_checkbox.isEnabled()
    step_checkbox.setChecked(True)
    assert section.analyzer_stack.isEnabled()


def test_coordinator_registry_snapshot_restore_validate_and_append_fingerprint(qapp):
    checkbox = QtWidgets.QCheckBox("step2")
    checkbox.setChecked(True)
    section = AnalyzerModeSection(QtWidgets.QWidget(), checkbox)
    section.set_mode(MODE_DEWETRON)
    section.dewetron_panel.refresh_power_groups(POWER_GROUP_XML)
    section.set_config(DewetronUiConfig("50", 3, False, ["U1_tRMS"]))

    coordinator = DewetronAutoTestCoordinator(collector=object())
    coordinator.register_section("重连", section)
    assert coordinator.current_project() == "重连"
    assert coordinator.current_mode() == MODE_DEWETRON
    assert coordinator.current_test_type() == "reconnection"
    assert coordinator.snapshot_config().export_fields == ["U1_tRMS"]

    first = coordinator.validate_append_config(remember=True)
    assert first.valid and not first.changed
    section.dewetron_panel.rate_combo.setCurrentText("20")
    second = coordinator.validate_append_config()
    assert second.valid and second.changed
    assert second.previous_fingerprint == first.fingerprint

    coordinator.restore_config(DewetronUiConfig("100", 1, True, ["I1_tRMS"]))
    assert coordinator.snapshot_config() == DewetronUiConfig(
        "100", 1, True, ["I1_tRMS"]
    )
    normalized = coordinator.normalize_segment(
        [["Upper_WT_Config"], ["AC", "query", "*IDN?"]],
        start_index=0,
        stop_index=1,
    )
    assert normalized[0][2] == DEWETRON_START_COMMAND
    assert normalized[-1][2] == DEWETRON_STOP_COMMAND

    harmonic_checkbox = QtWidgets.QCheckBox("step2")
    harmonic_checkbox.setChecked(True)
    harmonic = AnalyzerModeSection(QtWidgets.QWidget(), harmonic_checkbox)
    assert harmonic.get_config().rate_text == "Default"
    coordinator.register_section("谐波电流", harmonic)
    assert harmonic.get_config().rate_text == "SYNC to HARMONIC"


def test_app_context_exposes_shared_references():
    context = AppContext()
    assert context.dewetron_collector is None
    assert context.dewetron_coordinator is None
