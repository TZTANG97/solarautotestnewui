# -*- coding: utf-8 -*-
"""LVRT plan generation using direct, documented VOLT steps only."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from utils.timing_profile import LVRT_SCHEMA, TimingProfileValidationError, time_to_ticks
from utils.timing_profile_adapters import (
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


def _phase_flags_from_row(row: Mapping[str, Any]) -> List[str]:
    return [
        "T" if row.get("l1", True) else "",
        "T" if row.get("l2", True) else "",
        "T" if row.get("l3", True) else "",
    ]


def _phase_tag(flags: Sequence[str]) -> str:
    letters = []
    for i, ch in enumerate(("1", "2", "3")):
        if i < len(flags) and flags[i] == "T":
            letters.append(ch)
    return ("L" + "".join(letters)) if letters else "L123"


def read_lvrt_phase_condition_rows(ui: Any) -> List[dict]:
    """Read enabled voltage rows from LVRT PEA condition list; empty → []."""
    widget = getattr(ui, "lvrtConditionList", None)
    if widget is None:
        return []
    try:
        rows = widget.get_rows(include_disabled=False)
    except Exception:
        return []
    out: List[dict] = []
    for row in rows or []:
        kind = str(row.get("kind", "V")).strip().upper()
        if kind == "F":
            continue
        out.append(dict(row))
    return out


def append_lvrt_phase_conditions(
    out_rows: List[List[Any]],
    rows: Iterable[Mapping[str, Any]],
    *,
    phase_mode: str,
    nominal_voltages: Sequence[float],
    chroma_61800: Optional[bool] = None,
) -> List[Dict[str, Any]]:
    """Append PEA-style per-phase voltage faults: set → dwell → recover to nominal.

    Reuses OVUF phase-target / sweep helpers for Chroma INDEPEND and Aitech EACH.
    """
    from utils.ac_scpi_commands import resolve_chroma_61800
    from utils.ovuf_recording import append_ovuf_sweep_volt

    if chroma_61800 is None:
        chroma_61800 = resolve_chroma_61800()

    rated_str = tuple(format_number(v) for v in nominal_voltages)
    while len(rated_str) < 3:
        rated_str = rated_str + (rated_str[0] if rated_str else "230",)
    rated_str = rated_str[:3]

    enabled = [
        r
        for r in rows
        if r.get("enabled", True) and str(r.get("kind", "V")).strip().upper() != "F"
    ]
    metas: List[Dict[str, Any]] = []
    for index, row in enumerate(enabled, 1):
        value = str(row.get("value", "")).strip() or rated_str[0]
        flags = _phase_flags_from_row(row)
        try:
            dwell_raw = float(str(row.get("dwell", "3")).strip() or "3")
        except (TypeError, ValueError):
            dwell_raw = 3.0
        unit = str(row.get("unit", "秒")).strip() or "秒"
        dwell = time_to_ticks(dwell_raw, unit)
        if dwell <= 0:
            dwell = 1

        append_ovuf_sweep_volt(
            out_rows,
            phase_mode,
            value,
            flags,
            rated_str,
            chroma_61800=chroma_61800,
        )
        out_rows.append(wait_row(dwell))
        # Always recover to S1 nominal (LVRT-style), including last row.
        append_ac_voltage(
            out_rows, phase_mode, nominal_voltages, chroma_61800=chroma_61800
        )

        tag = _phase_tag(flags)
        metas.append(
            {
                "name": "LVRT_R%02d_V%s_%s" % (index, format_number(value), tag),
                "index": index,
                "value": value,
                "phase_tag": tag,
                "repeats": 1,
                "duration_01s": dwell,
                "u_pu": value,
            }
        )

    if any("LIST" in str(row[2]).upper() for row in out_rows):
        raise TimingProfileValidationError("LVRT 禁止生成 LIST 命令")
    return metas


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
    chroma_61800: Optional[bool] = None,
) -> Dict[str, Any]:
    """Build a ten-column LVRT command plan.

    If the PEA phase-condition list has enabled voltage rows, those take
    priority over the symmetric ``u_pu`` timing profile.
    """

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
        names: List[str] = []
        if getattr(ui, "checkBox_S3").isChecked():
            phase_mode, nominal = baseline_ac_voltages(ui)
            cond_rows = read_lvrt_phase_condition_rows(ui)
            started = append_acquisition_start(context, profile_rows)
            if cond_rows:
                metas = append_lvrt_phase_conditions(
                    profile_rows,
                    cond_rows,
                    phase_mode=phase_mode,
                    nominal_voltages=nominal,
                    chroma_61800=chroma_61800,
                )
                names = [str(meta.get("name") or "LVRT") for meta in metas]
            else:
                profile = read_ui_profile(ui, LVRT_SCHEMA)
                metas = append_lvrt_profile(
                    profile_rows,
                    profile,
                    phase_mode=phase_mode,
                    nominal_voltages=nominal,
                )
                names = ["LVRT_%s" % format_number(meta["u_pu"]) for meta in metas]
            append_acquisition_end(started, profile_rows)
        if any("LIST" in str(row[2]).upper() for row in profile_rows):
            raise TimingProfileValidationError("LVRT 禁止生成 LIST 命令")
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
    "append_lvrt_phase_conditions",
    "append_lvrt_profile",
    "build_lvrt_plan",
    "build_thai_lvrt_plan",
    "read_lvrt_phase_condition_rows",
]
