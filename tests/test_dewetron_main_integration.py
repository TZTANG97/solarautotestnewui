# -*- coding: utf-8 -*-
"""Focused contracts for the DEWETRON wiring in ``SCPITestWave.py``.

``SCPITestWave`` creates Qt windows, timers, and device-facing state at import
 time, so this module deliberately never imports it.  Main-file coverage below
is structural (AST/source wiring); executable behavior is limited to the
isolated XML retry helper with fakes and the dependency-light normalization
API from :mod:`dewetron_autotest`.
"""

from __future__ import annotations

import ast
import copy
from pathlib import Path
from types import SimpleNamespace

import pytest

from dewetron_autotest import (
    COMMAND_BRANCH_WAIT_COLUMNS,
    COMMAND_ROW_LENGTH,
    COMMAND_WT_TRIGGER_COLUMNS,
    DEWETRON_START_COMMAND,
    DEWETRON_STOP_COMMAND,
    ELIGIBLE_PROJECT_NAMES,
    WAIT_ACTION,
    WAIT_DEVICE,
    make_wait_row,
    normalize_dewetron_command_segment,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAIN_PATH = PROJECT_ROOT / "SCPITestWave.py"
MAIN_SOURCE = MAIN_PATH.read_text(encoding="utf-8-sig")
MAIN_TREE = ast.parse(MAIN_SOURCE, filename=str(MAIN_PATH))
MAIN_FUNCTIONS = {
    node.name: node
    for node in MAIN_TREE.body
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
}

APPROVED_APPEND_WRAPPERS = (
    ("thaichonglianAppend", "thaichonglianSend", "重连"),
    ("thaioverloadsAppend", "thaioverloadsSend", "过载能力测试"),
    ("thaizhiliufenliangAppend", "thaizhiliufenliangSend", "直流分量"),
    ("thaistaticQUAppend", "thaistaticQUSend", "静态QU"),
    ("thaireactiveQcapAppend", "thaireactiveQcapSend", "无功能力范围"),
    ("thaifixedQAppend", "thaifixedQSend", "定无功"),
    ("thaireactiveQinAppend", "thaireactiveQinSend", "无功注入"),
    ("thaireactiveQaccAppend", "thaireactiveQaccSend", "无功精度"),
    ("thaiactivePAppend", "thaiactivePSend", "有功调度"),
    ("thaitestPUAppend", "thaitestPUSend", "Test_PU"),
    ("thaistaticcosPhiAppend", "thaistaticcosPhiSend", "静态Cos(φ)"),
    ("thaidynamiccosPhiAppend", "thaidynamiccosPhiSend", "动态Cos(φ)"),
    ("thaidynamicQUAppend", "thaidynamicQUSend", "动态QU"),
    ("thaicosPhiBrazilAppend", "thaicosPhiBrazilSend", "Cos(φ)_Brazil"),
    ("thaivoltprotect10minAppend", "thaivoltprotect10minSend", "10min过压保护"),
    ("thaiguopinjiangzaiAppend", "thaiguopinjiangzaiSend", "过频降载"),
    ("thaiqianpinshengzaiAppend", "thaiqianpinshengzaiSend", "欠频升载"),
    ("thaiguoqianya_pinAppend", "thaiguoqianya_pinSend", "过欠压_过欠频"),
    ("thaiguoqianpin_immunAppend", "thaiguoqianpin_immunSend", "巴西过欠频稳定性"),
    ("thaifrequencyadaptabilityAppend", "thaifrequencyadaptabilitySend", "频率适应性"),
    ("thaivoltageadaptabilityAppend", "thaivoltageadaptabilitySend", "电压适应性"),
    ("thairocofAppend", "thairocofSend", "ROCOF保护"),
    ("thairapidvoltAppend", "thairapidvoltSend", "快速电压变化"),
)

EXCLUDED_APPEND_WRAPPERS = (
    "thaidianyashanbianAppend",
    "thaifixedpfAppend",
    "thaistaticMPPTtestAppend",
)


def _function(name: str) -> ast.FunctionDef:
    """Return one top-level main function without importing the application."""
    try:
        return MAIN_FUNCTIONS[name]
    except KeyError as exc:  # pragma: no cover - failure message for source drift
        raise AssertionError(f"SCPITestWave.py is missing function {name}") from exc


def _call_path(callable_node: ast.AST) -> str:
    """Return a dotted name for a simple Name/Attribute call target."""
    if isinstance(callable_node, ast.Name):
        return callable_node.id
    if isinstance(callable_node, ast.Attribute):
        prefix = _call_path(callable_node.value)
        return f"{prefix}.{callable_node.attr}" if prefix else callable_node.attr
    return ""


def _calls(node: ast.AST, path: str | None = None) -> list[ast.Call]:
    calls = [item for item in ast.walk(node) if isinstance(item, ast.Call)]
    if path is not None:
        calls = [item for item in calls if _call_path(item.func) == path]
    return calls


def _literal_first_arg(call: ast.Call):
    assert call.args, f"{_call_path(call.func)} must receive a positional project name"
    return ast.literal_eval(call.args[0])


def _negated_call_paths(node: ast.AST) -> set[str]:
    """Collect direct ``if not object.method()`` call paths."""
    paths = set()
    for item in ast.walk(node):
        if not isinstance(item, ast.If):
            continue
        test = item.test
        if (
            isinstance(test, ast.UnaryOp)
            and isinstance(test.op, ast.Not)
            and isinstance(test.operand, ast.Call)
        ):
            paths.add(_call_path(test.operand.func))
    return paths


def _negated_name_lines(node: ast.AST, name: str) -> list[int]:
    lines = []
    for item in ast.walk(node):
        if not isinstance(item, ast.If):
            continue
        test = item.test
        if (
            isinstance(test, ast.UnaryOp)
            and isinstance(test.op, ast.Not)
            and isinstance(test.operand, ast.Name)
            and test.operand.id == name
        ):
            lines.append(item.lineno)
    return sorted(lines)


def _assigned_calls(node: ast.AST, path: str) -> list[ast.Assign]:
    return [
        item
        for item in ast.walk(node)
        if isinstance(item, ast.Assign)
        and isinstance(item.value, ast.Call)
        and _call_path(item.value.func) == path
    ]


def _compares_to(node: ast.AST, value: str) -> bool:
    return any(
        isinstance(item, ast.Constant) and item.value == value
        for item in ast.walk(node)
    )


def _compile_extracted_function(name: str, globals_dict: dict):
    """Compile one source function in a fake-only namespace."""
    function_node = copy.deepcopy(_function(name))
    module = ast.Module(body=[function_node], type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"__builtins__": __builtins__, **globals_dict}
    exec(compile(module, str(MAIN_PATH), "exec"), namespace)
    return namespace[name]


@pytest.mark.parametrize(
    "wrapper_name,send_name,project_name", APPROVED_APPEND_WRAPPERS
)
def test_approved_append_wrappers_snapshot_send_then_normalize(
    wrapper_name, send_name, project_name
):
    """Every approved wrapper brackets its Send call with the same project key."""
    wrapper = _function(wrapper_name)
    snapshots = _calls(wrapper, "_snapshot_dewetron_append")
    normalizers = _calls(wrapper, "_normalize_generated_dewetron_rows")
    sends = _calls(wrapper, send_name)

    assert len(snapshots) == len(normalizers) == len(sends) == 1
    assert _literal_first_arg(snapshots[0]) == project_name
    assert _literal_first_arg(normalizers[0]) == project_name
    assert snapshots[0].lineno < sends[0].lineno < normalizers[0].lineno


def test_approved_wrapper_projects_match_the_eligible_registry_exactly():
    assert tuple(item[2] for item in APPROVED_APPEND_WRAPPERS) == ELIGIBLE_PROJECT_NAMES


@pytest.mark.parametrize("wrapper_name", EXCLUDED_APPEND_WRAPPERS)
def test_excluded_append_wrappers_do_not_use_shared_dewetron_hooks(wrapper_name):
    call_paths = {_call_path(call.func) for call in _calls(_function(wrapper_name))}
    assert "_snapshot_dewetron_append" not in call_paths
    assert "_normalize_generated_dewetron_rows" not in call_paths


def test_run_project_push_prepares_dewetron_before_setting_start_flag():
    """Preparation failure must return before the executor start latch is set."""
    function = _function("RunProjectPush")
    prepare_calls = _calls(function, "_prepare_dewetron_collector")
    start_assignments = [
        item
        for item in ast.walk(function)
        if isinstance(item, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "strTestFlag"
            for target in item.targets
        )
    ]

    assert len(prepare_calls) == 1
    assert len(start_assignments) == 1
    assert ast.literal_eval(start_assignments[0].value) == "1"
    assert prepare_calls[0].lineno < start_assignments[0].lineno

    prepare_guards = [
        item
        for item in ast.walk(function)
        if isinstance(item, ast.If)
        and isinstance(item.test, ast.UnaryOp)
        and isinstance(item.test.op, ast.Not)
        and isinstance(item.test.operand, ast.Call)
        and _call_path(item.test.operand.func) == "_prepare_dewetron_collector"
    ]
    assert len(prepare_guards) == 1
    assert any(isinstance(statement, ast.Return) for statement in prepare_guards[0].body)


def test_run_project_uses_boolean_checked_public_dewetron_lifecycle_apis():
    function = _function("RunProject")
    call_paths = {_call_path(call.func) for call in _calls(function)}
    assert {
        "dewetron_collector.start_gathering",
        "dewetron_controller.start_acquisition",
        "dewetron_collector.on_acquisition_started",
        "dewetron_collector.stop_gathering",
        "dewetron_controller.stop_acquisition",
    } <= call_paths

    # Collector preparation/state confirmation are both explicit boolean gates.
    assert {
        "dewetron_collector.start_gathering",
        "dewetron_collector.on_acquisition_started",
    } <= _negated_call_paths(function)

    # Controller START and STOP results are assigned and checked before/after the
    # corresponding command paths continue.
    start_assignments = _assigned_calls(
        function, "dewetron_controller.start_acquisition"
    )
    stop_assignments = _assigned_calls(function, "dewetron_controller.stop_acquisition")
    assert len(start_assignments) == len(stop_assignments) == 1
    assert [target.id for target in start_assignments[0].targets if isinstance(target, ast.Name)] == ["sent"]
    assert [target.id for target in stop_assignments[0].targets if isinstance(target, ast.Name)] == ["sent"]
    sent_guard_lines = _negated_name_lines(function, "sent")
    assert any(
        start_assignments[0].lineno < line < stop_assignments[0].lineno
        for line in sent_guard_lines
    )
    assert any(line > stop_assignments[0].lineno for line in sent_guard_lines)

    finish_calls = _calls(function, "_finish_dewetron_session")
    finish_reasons = {_literal_first_arg(call) for call in finish_calls}
    assert {"error", "completed"} <= finish_reasons
    error_handlers = [
        handler
        for handler in ast.walk(function)
        if isinstance(handler, ast.ExceptHandler)
        and any(
            _call_path(call.func) == "_finish_dewetron_session"
            and _literal_first_arg(call) == "error"
            for call in _calls(handler)
        )
    ]
    assert error_handlers, "DEWETRON command errors must finish the active session"

    finish_function = _function("_finish_dewetron_session")
    finish_paths = {_call_path(call.func) for call in _calls(finish_function)}
    assert {
        "dewetron_collector.get_state",
        "dewetron_collector.stop_gathering",
        "dewetron_controller.stop_acquisition",
        "dewetron_collector.export_to_csv",
        "dewetron_collector.finish_batch",
    } <= finish_paths


def test_normalization_clears_triggers_and_preserves_only_policy_owned_waits():
    """Exercise only the pure normalizer, not the application command builder."""
    rows = [
        ["AC", "write", "VOLT 230", "", "", "", 11, 7, 3, 4],
        ["Upper_WT_Config", "", "", "config_dict", {"range": "auto"}],
        ["WT", "macro.json", "", "", "", "", 9, 17, "", ""],
        make_wait_row(23),
        ["DC1", "write", "OUTP ON", "", "", "", "", "", 8, 9],
    ]
    policy_visits = []

    def preserve_known_wt_macro_dwell(removed):
        policy_visits.append(removed.device)
        if removed.device.upper() != "WT":
            return None
        waits = [
            int(removed.row[column])
            for column in COMMAND_WT_TRIGGER_COLUMNS
            if removed.row[column] not in ("", None)
        ]
        return make_wait_row(max(waits)) if waits else None

    result = normalize_dewetron_command_segment(
        rows,
        start_index=1,
        stop_index=4,
        wt_row_policy=preserve_known_wt_macro_dwell,
        return_metadata=True,
    )

    assert policy_visits == ["Upper_WT_Config", "WT"]
    assert all(len(row) == COMMAND_ROW_LENGTH for row in result.rows)
    assert all(
        [row[column] for column in COMMAND_WT_TRIGGER_COLUMNS] == ["", ""]
        for row in result.rows
    )
    retained_ac = next(row for row in result.rows if row[2] == "VOLT 230")
    assert [retained_ac[column] for column in COMMAND_BRANCH_WAIT_COLUMNS] == [3, 4]

    waits = [
        row
        for row in result.rows
        if row[0] == WAIT_DEVICE and row[1] == WAIT_ACTION
    ]
    assert WAIT_DEVICE == "AC" and WAIT_ACTION == "wait"
    assert [row[9] for row in waits] == [17, 23]
    assert [row[2] for row in result.rows if row[0] == "DEWETRON"] == [
        DEWETRON_START_COMMAND,
        DEWETRON_STOP_COMMAND,
    ]

    # The concrete executor has a nested AC + wait branch for this neutral row.
    run_project = _function("RunProject")
    ac_branches = [
        item
        for item in ast.walk(run_project)
        if isinstance(item, ast.If) and _compares_to(item.test, "AC")
    ]
    assert any(
        any(
            isinstance(descendant, ast.If)
            and _compares_to(descendant.test, "wait")
            for statement in branch.body
            for descendant in ast.walk(statement)
        )
        for branch in ac_branches
    )


def test_shared_apply_passes_export_options_and_uses_live_xml_retry():
    apply_function = _function("_apply_shared_dewetron_config")
    retry_calls = _calls(apply_function, "_read_dewetron_xml_with_retry")
    modify_calls = _calls(apply_function, "dewetron_controller.modify_xml")
    assert len(retry_calls) == len(modify_calls) == 1
    assert not _calls(apply_function, "dewetron_controller.read_channel_id_map")

    keywords = {keyword.arg: keyword.value for keyword in modify_calls[0].keywords}
    assert _call_path(keywords["export_fields"]) == "config.export_fields"
    assert _call_path(keywords["decimal_places"]) == "config.decimal_places"
    assert _call_path(keywords["realtime_waveform"]) == "config.realtime_waveform"

    responses = iter(
        [
            ({}, "<xml version='first'/ >"),
            ({"U1": "stale-id"}, None),
            ({"U1": "live-id"}, "<xml version='live'/>")
        ]
    )

    class FakeController:
        def __init__(self):
            self.read_count = 0

        def read_channel_id_map(self):
            self.read_count += 1
            return next(responses)

    controller = FakeController()
    sleeps = []
    retry = _compile_extracted_function(
        "_read_dewetron_xml_with_retry",
        {
            "dewetron_controller": controller,
            "time": SimpleNamespace(sleep=sleeps.append),
        },
    )

    assert retry() == ({"U1": "live-id"}, "<xml version='live'/>")
    assert controller.read_count == 3
    assert sleeps == [2, 2]

    bind_function = _function("_bind_shared_dewetron_actions")
    assert any(
        isinstance(item, ast.For)
        and isinstance(item.iter, ast.Name)
        and item.iter.id == "ELIGIBLE_PROJECT_NAMES"
        for item in ast.walk(bind_function)
    )
    assert {
        "固定PF=1",
        "MPPT",
        "静态MPPT测试",
    }.isdisjoint(ELIGIBLE_PROJECT_NAMES)
