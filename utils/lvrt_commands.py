# -*- coding: utf-8 -*-
"""LVRT plan generation using direct, documented VOLT steps only."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from utils.timing_profile import LVRT_SCHEMA, TimingProfileValidationError, time_to_ticks
from utils.timing_profile_adapters import (
    ac_write_row,
    append_ac_voltage,
    append_acquisition_end,
    append_acquisition_start,
    baseline_ac_voltages,
    build_plan_context,
    ensure_ten_column_rows,
    finalize_plan,
    format_number,
    read_ui_profile,
    wait_row,
)


def _scaled_voltages(nominal: Sequence[float], u_pu: float) -> List[float]:
    return [float(value) * float(u_pu) for value in nominal]


def append_lvrt_profile(
    out_rows: List[List[Any]],
    profile: Iterable[Mapping[str, Any]],
    *,
    phase_mode: str,
    nominal_voltages: Sequence[float],
) -> List[Dict[str, Any]]:
    """Append nominal→dip→nominal events.

    This adapter intentionally has no LIST path.  Every disturbance is a direct
    ``VOLT`` write plus executor waits; three-phase channel-selection writes are
    emitted only when individual nominal phase values require them.
    """

    metas: List[Dict[str, Any]] = []
    for index, point in enumerate(profile, 1):
        if not point.get("enabled", True):
            continue
        u_pu = float(point["u_pu"])
        pre = time_to_ticks(point["t_pre"], point["t_pre_unit"])
        dwell = time_to_ticks(point["t_dwell"], point["t_dwell_unit"])
        post = time_to_ticks(point["t_post"], point["t_post_unit"])
        repeats = int(point.get("repeats", 1))
        label = str(point.get("label") or "LVRT_%d" % index)
        for _repeat in range(repeats):
            if pre:
                out_rows.append(wait_row(pre))
            append_ac_voltage(
                out_rows, phase_mode, _scaled_voltages(nominal_voltages, u_pu)
            )
            if dwell:
                out_rows.append(wait_row(dwell))
            append_ac_voltage(out_rows, phase_mode, nominal_voltages)
            if post:
                out_rows.append(wait_row(post))
        metas.append(
            {
                "name": label,
                "index": index,
                "u_pu": u_pu,
                "repeats": repeats,
                "duration_01s": (pre + dwell + post) * repeats,
            }
        )
    if any("LIST" in str(row[2]).upper() for row in out_rows):
        raise TimingProfileValidationError("LVRT 禁止生成 LIST 命令")
    return metas


def _error_result(message: str, existing_commands: Optional[Iterable[Sequence[Any]]]) -> Dict[str, Any]:
    try:
        commands = ensure_ten_column_rows(existing_commands or [])
    except Exception:
        commands = []
    return {
        "ok": False,
        "error": message,
        "dc_errors": [],
        "commands": commands,
        "steps": [],
        "test_program": [],
        "wt_is_checked": "0",
        "wt_type": None,
        "analyzer_mode": "wt3000",
        "profile_metas": [],
        "band_metas": [],
        "file_names": [],
        "wt_rounds": 0,
        "wt_continuous": False,
        "band_duration_01s": 0,
        "max_band_duration_01s": 0,
    }


def build_lvrt_plan(
    ui: Any,
    *,
    wt_config_dict: Optional[Mapping[str, Any]] = None,
    str_add_flag: str = "0",
    project_change: str = "0",
    existing_commands: Optional[Iterable[Sequence[Any]]] = None,
    dc_iv_resolver: Any = None,
) -> Dict[str, Any]:
    """Build a ten-column LVRT command plan."""

    try:
        context = build_plan_context(
            ui,
            wt_config_dict=wt_config_dict,
            str_add_flag=str_add_flag,
            project_change=project_change,
            existing_commands=existing_commands,
            dc_iv_resolver=dc_iv_resolver,
        )
        profile_rows: List[List[Any]] = []
        metas: List[Dict[str, Any]] = []
        if getattr(ui, "checkBox_S3").isChecked():
            profile = read_ui_profile(ui, LVRT_SCHEMA)
            phase_mode, nominal = baseline_ac_voltages(ui)
            started = append_acquisition_start(context, profile_rows)
            metas = append_lvrt_profile(
                profile_rows,
                profile,
                phase_mode=phase_mode,
                nominal_voltages=nominal,
            )
            append_acquisition_end(started, profile_rows)
        if any("LIST" in str(row[2]).upper() for row in profile_rows):
            raise TimingProfileValidationError("LVRT 禁止生成 LIST 命令")
        names = ["LVRT_%s" % format_number(meta["u_pu"]) for meta in metas]
        return finalize_plan(
            context,
            profile_rows,
            profile_metas=metas,
            file_names=names or ["LVRT"],
        )
    except (AttributeError, TypeError, ValueError, TimingProfileValidationError) as exc:
        return _error_result("LVRT 计划生成失败: %s" % exc, existing_commands)


# Integration branches have used both spellings.
build_thai_lvrt_plan = build_lvrt_plan


__all__ = [
    "append_lvrt_profile",
    "build_lvrt_plan",
    "build_thai_lvrt_plan",
]
