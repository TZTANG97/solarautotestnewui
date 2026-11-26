# -*- coding: utf-8 -*-
"""Headless tests for the shared DEWETRON AutoTest foundation."""

import os
from pathlib import Path

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


@pytest.fixture(autouse=True)
def _isolate_dew_presets(tmp_path, monkeypatch):
    """Avoid cross-test contamination from export-field preset files."""
    preset_dir = tmp_path / "dew_presets"
    preset_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("SOLARAUTOTEST_DEW_PRESET_DIR", str(preset_dir))


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
          <Channel Name="F_fund"/>
        </ChannelGroup>
      </ChannelGroup>
      <ChannelGroup Type="Current (I)">
        <ChannelGroup Type="Total RMS">
          <Channel Name="I1_tRMS"/>
        </ChannelGroup>
      </ChannelGroup>
      <ChannelGroup Type="Advanced">
        <Channel Name="noise_adv"/>
        <Channel Name="Freq"/>
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
        "防逆流测试",
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
        "低电压穿越",
        "相角突变",
        "动态MPPT",
        "固定PF=1",
        "静态MPPT测试",
    )
    assert PROJECT_SPECS["固定PF=1"].test_type == "fixed-pf"
    assert PROJECT_SPECS["静态MPPT测试"].test_type == "static-mppt"
    assert PROJECT_SPECS["低电压穿越"].test_type == "lvrt"
    assert PROJECT_SPECS["相角突变"].test_type == "phase-jump"
    assert PROJECT_SPECS["动态MPPT"].test_type == "dynamic-mppt"
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
    assert get_project_spec("fixedpf").project_name == "固定PF=1"
    assert get_project_spec("MPPT").project_name == "静态MPPT测试"


@pytest.mark.parametrize(
    "project_name,test_type",
    (("固定PF=1", "fixed-pf"), ("静态MPPT测试", "static-mppt")),
)
def test_fixed_pf_and_static_mppt_sections_register(qapp, project_name, test_type):
    checkbox = QtWidgets.QCheckBox("分析仪")
    checkbox.setChecked(True)
    section = AnalyzerModeSection(QtWidgets.QWidget(), checkbox)
    coordinator = DewetronAutoTestCoordinator()

    coordinator.register_section(project_name, section)

    assert coordinator.registered_projects() == (project_name,)
    assert coordinator.current_test_type(project_name) == test_type
    assert coordinator.current_mode(project_name) == MODE_WT


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


def test_power_group_tree_sorts_phases_and_categories():
    from components.dewetron_autotest_panel import sort_power_group_tree

    tree = sort_power_group_tree({
        "Energy (W)": {"Total": ["W12_t", "W_t", "W2_t", "W1_t"]},
        "Voltage (U)": {
            "Fundamental": ["U12_fundRMS", "U_fundRMS", "U2_fundRMS", "U1_fundRMS"],
            "Total RMS": ["U3_tRMS", "U1_tRMS", "U12_tRMS"],
        },
    })
    assert list(tree) == ["Voltage (U)", "Energy (W)"]
    assert list(tree["Voltage (U)"]) == ["Total RMS", "Fundamental"]
    assert tree["Voltage (U)"]["Total RMS"] == ["U1_tRMS", "U3_tRMS", "U12_tRMS"]
    assert tree["Voltage (U)"]["Fundamental"] == [
        "U_fundRMS",
        "U1_fundRMS",
        "U2_fundRMS",
        "U12_fundRMS",
    ]
    assert tree["Energy (W)"]["Total"] == ["W_t", "W1_t", "W2_t", "W12_t"]


def _power_channel(short_id, used="True", active="True"):
    return (
        '<Channel id="1"><Property name="Used"><BooleanValue>%s</BooleanValue></Property>'
        '<Property name="ShortId"><StringValue>"%s"</StringValue></Property>'
        '<Property name="Neon/Active"><BooleanValue>%s</BooleanValue></Property></Channel>'
        % (used, short_id, active)
    )


def test_power_screen_stays_on_its_own_page_and_becomes_active():
    from DewetronTestPage import inject_power_group_screen

    other = '<MeasurementScreen><InstrumentGrid type="oxy::analog"></InstrumentGrid></MeasurementScreen>'
    power = (
        '<MeasurementScreen><InstrumentGrid type="oxy::power_group" columns="1">'
        '<InstrumentChannel channel_id="1"/></InstrumentGrid></MeasurementScreen>'
    )
    xml = '<MeasurementScreens active_screen="0">' + other + power + "</MeasurementScreens>"
    updated, changed, _msg = inject_power_group_screen(xml, "77")
    assert changed
    assert 'active_screen="1"' in updated
    assert updated.index("oxy::analog") < updated.index("oxy::power_group")
    assert 'channel_id="77"' in updated
    assert 'channel_id="1"' not in updated


def test_new_power_screen_is_the_screen_oxygen_opens():
    from DewetronTestPage import inject_power_group_screen

    other = '<MeasurementScreen><InstrumentGrid type="oxy::recorder"></InstrumentGrid></MeasurementScreen>'
    xml = '<MeasurementScreens active_screen="0">' + other + "</MeasurementScreens>"
    updated, changed, _msg = inject_power_group_screen(xml, "77")
    assert changed
    assert 'active_screen="0"' in updated
    assert updated.index("oxy::power_group") < updated.index("oxy::recorder")


def test_used_flag_after_the_name_is_the_one_oxygen_reads():
    from DewetronTestPage import activate_analog_channels, clamp_power_channels, enable_power_group_channels

    basic = (
        '<Channel id="2"><Property name="ShortId"><StringValue>"U1_tRMS"</StringValue></Property>'
        '<Property name="Used"><BooleanValue>False</BooleanValue></Property></Channel>'
    )
    enabled, count = enable_power_group_channels(basic, phases={1})
    assert count >= 1
    assert "<BooleanValue>True</BooleanValue>" in enabled

    optional = (
        '<Channel id="3"><Property name="ShortId"><StringValue>"U2_fluc_Pst"</StringValue></Property>'
        '<Property name="Used"><BooleanValue>True</BooleanValue></Property></Channel>'
    )
    clamped, _labels = clamp_power_channels(optional, {1}, {"flicker": False, "harmonics": False, "rolling": False})
    assert "<BooleanValue>True</BooleanValue>" not in clamped

    sleeping = (
        '<Channel id="9"><DataFormat frequency="NEVER" sample_format="sint24"/>'
        '<Property name="ShortId"><StringValue>"AI 1/U1"</StringValue></Property>'
        '<Property name="Used"><BooleanValue>False</BooleanValue></Property></Channel>'
    )
    awake, opened = activate_analog_channels(sleeping, ["AI 1/U1"])
    assert opened == ["AI 1/U1"]
    assert 'frequency="SYNC"' in awake
    assert "<BooleanValue>True</BooleanValue>" in awake


def test_board_mode_pairs_voltage_and_current_when_names_do_not():
    from DewetronTestPage import default_power_inputs, phases_from_xml

    xml = (
        '<Channel id="11">'
        '<Property name="ID:TRION/BoardId"><UnsignedValue>1</UnsignedValue></Property>'
        '<Property name="ID:TRION/ChannelIndex"><UnsignedValue>0</UnsignedValue></Property>'
        '<Property name="ShortId"><StringValue>"AI 1/1"</StringValue></Property>'
        '<Property name="Mode"><StringValue>"Current"</StringValue></Property>'
        "</Channel>"
        '<Channel id="12">'
        '<Property name="ID:TRION/BoardId"><UnsignedValue>1</UnsignedValue></Property>'
        '<Property name="ID:TRION/ChannelIndex"><UnsignedValue>4</UnsignedValue></Property>'
        '<Property name="ShortId"><StringValue>"AI 1/5"</StringValue></Property>'
        '<Property name="Mode"><StringValue>"Voltage"</StringValue></Property>'
        "</Channel>"
        '<Property name="POWER/InputChannels/U1"><ChannelID>11</ChannelID></Property>'
        '<Property name="POWER/InputChannels/I1"><ChannelID>99</ChannelID></Property>'
    )
    assert default_power_inputs(0, {"AI 1/1": "11", "AI 1/5": "12"}, xml) == {
        "U1": "AI 1/5",
        "I1": "AI 1/1",
    }
    assert phases_from_xml(xml, {"11", "12"}) == set()


def _mode_channel(cid, name, mode, index, board):
    return (
        '<Channel id="%s">'
        '<Property name="ID:TRION/BoardId"><UnsignedValue>%s</UnsignedValue></Property>'
        '<Property name="ID:TRION/ChannelIndex"><UnsignedValue>%s</UnsignedValue></Property>'
        '<Property name="ShortId"><StringValue>"%s"</StringValue></Property>'
        '<Property name="Mode"><StringValue>"%s"</StringValue></Property>'
        "</Channel>" % (cid, board, index, name, mode)
    )


def test_named_channels_keep_their_phase_when_board_index_differs():
    from DewetronTestPage import default_power_inputs

    xml = "".join((
        _mode_channel("1", "AI 1/U1", "Voltage", 9, 1),
        _mode_channel("2", "AI 1/U2", "Voltage", 1, 1),
        _mode_channel("3", "AI 1/U3", "Voltage", 2, 1),
        _mode_channel("4", "AI 1/I1", "Current", 8, 1),
        _mode_channel("5", "AI 1/I2", "Current", 3, 1),
        _mode_channel("6", "AI 1/I3", "Current", 4, 1),
    ))
    slots = default_power_inputs(3, {
        "AI 1/U1": "1", "AI 1/U2": "2", "AI 1/U3": "3",
        "AI 1/I1": "4", "AI 1/I2": "5", "AI 1/I3": "6",
    }, xml)
    assert slots["U1"] == "AI 1/U1"
    assert slots["U2"] == "AI 1/U2"
    assert slots["I1"] == "AI 1/I1"


def test_voltage_and_current_are_not_paired_across_boards():
    from DewetronTestPage import discover_from_modes

    xml = (
        _mode_channel("1", "AI 1/1", "Voltage", 1, 1)
        + _mode_channel("2", "AI 2/1", "Current", 1, 2)
        + _mode_channel("3", "AI 2/2", "Voltage", 2, 2)
        + _mode_channel("4", "AI 2/3", "Current", 3, 2)
    )
    found = discover_from_modes(xml)
    assert found == {"U1": "AI 2/2", "I1": "AI 2/1"}
    assert "AI 1/1" not in found.values()


def test_totals_stay_off_until_every_required_phase_is_wired():
    from DewetronTestPage import clamp_power_channels, totals_ready

    assert totals_ready({1}, 3) is False
    assert totals_ready({1, 2, 3}, 3) is True
    xml = (
        '<Channel id="2"><Property name="Used"><BooleanValue>True</BooleanValue></Property>'
        '<Property name="ShortId"><StringValue>"U1_tRMS"</StringValue></Property></Channel>'
        '<Channel id="3"><Property name="Used"><BooleanValue>True</BooleanValue></Property>'
        '<Property name="ShortId"><StringValue>"U_tRMS"</StringValue></Property></Channel>'
    )
    clamped, _labels = clamp_power_channels(
        xml, {1}, {"flicker": False, "harmonics": False, "rolling": False}, totals=False
    )
    assert 'StringValue>"U1_tRMS"' in clamped
    total = clamped[clamped.index('StringValue>"U_tRMS"') - 80:clamped.index('StringValue>"U_tRMS"')]
    assert "True" not in total
    phase = clamped[clamped.index('StringValue>"U1_tRMS"') - 80:clamped.index('StringValue>"U1_tRMS"')]
    assert "True" in phase


def test_numbered_analog_channels_pair_voltage_then_current():
    from DewetronTestPage import default_power_inputs

    slots = default_power_inputs(0, {"AI 1/1": "1", "AI 1/2": "2"})
    assert slots == {"U1": "AI 1/1", "I1": "AI 1/2"}


def test_voltage_alone_is_not_a_power_phase():
    from DewetronTestPage import default_power_inputs, phases_from_slots

    assert phases_from_slots({"U1": "AI 1/U1"}) == set()
    assert phases_from_slots({"U1": "AI 1/U1", "I1": "AI 1/I1"}) == {1}
    assert default_power_inputs(0, {"AI 1/U1": "11"}) == {}
    assert default_power_inputs(0, {"AI 1/U1": "11", "AI 1/I1": "12"}) == {
        "U1": "AI 1/U1",
        "I1": "AI 1/I1",
    }


def test_empty_power_group_gets_phase_one_and_drops_unwired_channels():
    from DewetronTestPage import apply_power_input_channels, clamp_power_channels, map_short_ids

    xml = (
        '<Property name="POWER/InputChannels/U1"><ChannelID>18446744073709551615</ChannelID></Property>'
        '<Property name="POWER/InputChannels/I1"><ChannelID>18446744073709551615</ChannelID></Property>'
        '<Channel id="11"><Property name="Used"><BooleanValue>False</BooleanValue></Property>'
        '<Property name="ShortId"><StringValue>"AI 1/U1"</StringValue></Property></Channel>'
        '<Channel id="12"><Property name="Used"><BooleanValue>False</BooleanValue></Property>'
        '<Property name="ShortId"><StringValue>"AI 1/I1"</StringValue></Property></Channel>'
        + _power_channel("U1_tRMS", "False", "False")
        + _power_channel("U2_tRMS", "True", "True")
        + _power_channel("U2_fluc_Pst", "True", "True")
        + _power_channel("U2_hPHI", "True", "True")
    )
    ids = map_short_ids(xml)
    updated, notes = apply_power_input_channels(xml, {"U1": "AI 1/U1", "I1": "AI 1/I1"}, ids)
    assert "U1 <- AI 1/U1" in notes
    assert "<ChannelID>11</ChannelID>" in updated
    assert "<ChannelID>12</ChannelID>" in updated
    clamped, _labels = clamp_power_channels(updated, {1}, {"flicker": False, "harmonics": False, "rolling": False})

    def _body(text, short_id):
        token = 'StringValue>"%s"' % short_id
        start = text.index(token)
        channel = text.rfind("<Channel id=", 0, start)
        end = text.index("</Channel>", start)
        return text[channel:end]

    assert _body(clamped, "U1_tRMS").count("True") == 2
    assert "True" not in _body(clamped, "U2_tRMS")
    assert "True" not in _body(clamped, "U2_fluc_Pst")
    assert "True" not in _body(clamped, "U2_hPHI")


def test_power_group_id_is_the_outer_channel_when_the_body_is_long():
    from DewetronTestPage import find_power_group_channel_id

    inner = '<Channel id="99">' + ("x" * 20000) + "</Channel>"
    xml = (
        '<Channel id="7">'
        + inner
        + '<Property name="ShortId"><StringValue>"PowerGroup"</StringValue></Property>'
        + "</Channel>"
    )
    assert find_power_group_channel_id(xml) == "7"


def test_enable_does_not_flip_the_previous_channel_across_a_long_gap():
    from DewetronTestPage import enable_power_group_channels

    far = "y" * 8000
    xml = (
        '<Channel id="1"><Property name="Used"><BooleanValue>False</BooleanValue></Property>'
        '<Property name="ShortId"><StringValue>"Other"</StringValue></Property></Channel>'
        '<Channel id="2"><Property name="Used"><BooleanValue>False</BooleanValue></Property>'
        + far
        + '<Property name="ShortId"><StringValue>"U1_tRMS"</StringValue></Property>'
        '<Property name="Neon/Active"><BooleanValue>False</BooleanValue></Property></Channel>'
    )
    updated, count = enable_power_group_channels(xml)
    first, second = updated.split("</Channel>", 1)
    assert "False" in first
    assert "True" in second
    assert count >= 1


def test_optional_channels_hide_when_features_are_off():
    from DewetronTestPage import apply_optional_feature_channels, optional_power_feature

    assert optional_power_feature("U1_tRMS") is None
    assert optional_power_feature("U1_fundRMS") is None
    assert optional_power_feature("U1_fluc_Pst") == "flicker"
    assert optional_power_feature("U1_h1RMS") == "harmonics"
    assert optional_power_feature("U2_hPHI") == "harmonics"
    assert optional_power_feature("I_fundUNBAL0") == "harmonics"
    assert optional_power_feature("U1_THD") == "harmonics"
    assert optional_power_feature("U1_tRMS_rc") == "rolling"

    xml = "".join(
        _power_channel(name)
        for name in ("U1_tRMS", "U1_fluc_Pst", "U1_h1RMS", "U1_THD", "P1_t_rc")
    )
    updated, changed = apply_optional_feature_channels(
        xml, flicker=False, harmonics=False, rolling=False
    )
    assert "U1_tRMS" in updated
    assert updated.count("<BooleanValue>False</BooleanValue>") == 8
    assert any("U1_fluc_Pst" in label for label in changed)
    assert 'StringValue>"U1_tRMS"' in updated
    # 基本量仍是 True；四个可选通道的 Used 和 Neon 都关掉
    basic = updated.split("</Channel>", 1)[0]
    assert basic.count("<BooleanValue>True</BooleanValue>") == 2
    assert "<BooleanValue>True</BooleanValue>" not in updated.split("</Channel>", 1)[1]


def test_checked_feature_keeps_its_channels():
    from DewetronTestPage import apply_optional_feature_channels

    xml = _power_channel("U1_h1RMS", used="False", active="False") + _power_channel(
        "U1_fluc_Pst"
    )
    updated, _changed = apply_optional_feature_channels(
        xml, flicker=False, harmonics=True, rolling=False
    )
    harmonic, flicker = updated.split("</Channel>", 1)
    assert harmonic.count("<BooleanValue>True</BooleanValue>") == 2
    assert flicker.count("<BooleanValue>False</BooleanValue>") == 2


def test_set_power_features_follows_checkboxes():
    from DewetronTestPage import set_power_features

    xml = (
        '<Property name="POWER/Features/Flicker"><BooleanValue>False</BooleanValue></Property>'
        '<Property name="POWER/Features/Harmonics"><BooleanValue>True</BooleanValue></Property>'
        '<Property name="POWER/Features/Rolling"><BooleanValue>False</BooleanValue></Property>'
    )
    updated, changed = set_power_features(xml, flicker=True, harmonics=False, rolling=False)
    assert changed == ["POWER/Features/Flicker", "POWER/Features/Harmonics"]
    assert "Flicker\"><BooleanValue>True" in updated
    assert "Harmonics\"><BooleanValue>False" in updated
    assert "Rolling\"><BooleanValue>False" in updated


def test_build_page_turns_off_flicker_harmonics_and_rolling():
    from DewetronTestPage import disable_heavy_power_features

    xml = (
        '<Property name="POWER/Features/Flicker"><BooleanValue>True</BooleanValue></Property>'
        '<Property name="POWER/Features/Harmonics"><BooleanValue>True</BooleanValue></Property>'
        '<Property name="POWER/Features/Rolling"><BooleanValue>True</BooleanValue></Property>'
        '<Property name="POWER/Features/MechanicalPower"><BooleanValue>True</BooleanValue></Property>'
    )
    updated, turned_off = disable_heavy_power_features(xml)
    assert turned_off == [
        "POWER/Features/Flicker",
        "POWER/Features/Harmonics",
        "POWER/Features/Rolling",
    ]
    assert "Flicker\"><BooleanValue>False" in updated
    assert "Harmonics\"><BooleanValue>False" in updated
    assert "Rolling\"><BooleanValue>False" in updated
    assert "MechanicalPower\"><BooleanValue>True" in updated
    again, still = disable_heavy_power_features(updated)
    assert still == []
    assert "MechanicalPower\"><BooleanValue>True" in again

    doubled = xml.replace(
        'name="POWER/Features/Flicker"><BooleanValue>True',
        'name="POWER/Features/Flicker"><BooleanValue>True',
    ) + '<Property name="POWER/Features/Flicker"><BooleanValue>True</BooleanValue></Property>'
    both, names = disable_heavy_power_features(doubled)
    assert names.count("POWER/Features/Flicker") == 2
    assert "Flicker\"><BooleanValue>True" not in both


def test_power_group_parser_does_not_depend_on_flicker_dialog():
    tree = parse_power_group_tree(POWER_GROUP_XML)
    assert tree == {
        "Voltage (U)": {
            "Total RMS": ["U1_tRMS", "U2_tRMS"],
        },
        "Current (I)": {"Total RMS": ["I1_tRMS"]},
        "Frequency (F)": {
            "Fundamental": ["F_fund", "Freq"],
        },
    }
    assert parse_power_group_tree("<MeasurementConfig/>") is None
    assert parse_power_group_tree("not xml") is None


def test_power_group_parser_picks_ffund_sibling_of_groups():
    """真机：F_fund 与 Voltage/Current 同级，直接挂在 POWER/0 下。"""
    from components.dewetron_autotest_panel import _is_frequency_channel

    xml = """
    <MeasurementConfig>
      <ChannelGroup Type="Power Groups">
        <Channel Name="POWER/0">
          <ChannelGroup Type="Voltage (U)">
            <ChannelGroup Type="Total RMS">
              <Channel Name="U1_tRMS"/>
            </ChannelGroup>
          </ChannelGroup>
          <ChannelGroup Type="Current (I)">
            <ChannelGroup Type="Total RMS">
              <Channel Name="I1_tRMS"/>
            </ChannelGroup>
          </ChannelGroup>
          <Channel Name="F_fund"/>
          <Channel Name="f__fund"/>
        </Channel>
      </ChannelGroup>
    </MeasurementConfig>
    """
    tree = parse_power_group_tree(xml)
    assert tree is not None
    assert "Frequency (F)" in tree
    fund = tree["Frequency (F)"]["Fundamental"]
    assert "F_fund" in fund
    assert "f__fund" in fund
    assert _is_frequency_channel("f__fund")
    assert _is_frequency_channel("F_fund [Hz]")
    assert not _is_frequency_channel("PF_fund")


def test_panel_pending_field_restoration_and_signals(qapp, tmp_path, monkeypatch):
    panel = DewetronAutoTestPanel()
    panel.set_config(DewetronUiConfig("20", 2, True, ["U2_tRMS", "I1_tRMS"]))
    assert panel.get_checked_export_fields() == ["U2_tRMS", "I1_tRMS"]

    panel.refresh_power_groups(POWER_GROUP_XML)
    assert panel.get_checked_export_fields() == ["U2_tRMS", "I1_tRMS"]
    assert panel.unavailable_export_fields() == []
    assert panel.get_config() == DewetronUiConfig(
        "20",
        2,
        True,
        ["U2_tRMS", "I1_tRMS"],
        save_dir=panel.lineEdit_DEW_SaveDir.text().strip(),
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

    # Apply auto-saves preset into the shared test dir; use a clean dir for
    # the "no preset → all unchecked" default.
    empty_dir = tmp_path / "empty_presets"
    empty_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("SOLARAUTOTEST_DEW_PRESET_DIR", str(empty_dir))
    fresh = DewetronAutoTestPanel()
    fresh.refresh_power_groups(POWER_GROUP_XML)
    assert fresh.get_checked_export_fields() == []


def test_export_preset_save_and_autoload(qapp, tmp_path, monkeypatch):
    """第一次勾选并保存后，下次打开自动恢复勾选。"""
    monkeypatch.setenv("SOLARAUTOTEST_DEW_PRESET_DIR", str(tmp_path / "presets"))
    panel = DewetronAutoTestPanel()
    panel.refresh_power_groups(POWER_GROUP_XML)
    panel.set_checked_export_fields(["U1_tRMS", "F_fund"])
    panel.rate_combo.setCurrentText("20")
    path = panel.save_export_preset(silent=True)
    assert path and Path(path).is_file()

    again = DewetronAutoTestPanel()
    again.refresh_power_groups(POWER_GROUP_XML)
    assert again.get_checked_export_fields() == ["U1_tRMS", "F_fund"]
    assert again.get_config().rate_text == "20"


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
    snap = coordinator.snapshot_config()
    assert snap.rate_text == "100"
    assert snap.decimal_places == 1
    assert snap.realtime_waveform is True
    assert snap.export_fields == ["I1_tRMS"]
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
