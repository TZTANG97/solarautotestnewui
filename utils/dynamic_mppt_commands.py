# -*- coding: utf-8 -*-
"""Brand-guarded dynamic-MPPT plan generation."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from utils.timing_profile import (
    DYNAMIC_MPPT_SCHEMA,
    TimingProfileValidationError,
    time_to_ticks,
)
from utils.timing_profile_adapters import (
    append_acquisition_end,
    append_acquisition_start,
    baseline_dc_values,
    build_plan_context,
    device_write_row,
    ensure_ten_column_rows,
    finalize_plan,
    format_number,
    make_guarded_dc_iv_resolver,
    read_ui_profile,
    resolve_dynamic_dc_commands,
    selected_profile_dc_channels,
    wait_row,
)


SUPPORTED_DYNAMIC_MPPT_BRANDS = ("Chroma", "Itech", "Bluesight")


def append_dynamic_mppt_profile(
    out_rows: List[List[Any]],
    profile: Iterable[Mapping[str, Any]],
    *,
    ui: Any,
    channels: Sequence[int],
    get_iv_fn: Any,
    per_dc_factor: Mapping[str, str],
    command_list_dc: Mapping[str, Sequence[str]],
) -> List[Dict[str, Any]]:
    """Append guarded curve changes for each selected DC channel."""

    if not channels:
        raise TimingProfileValidationError(
            "动态 MPPT 至少需要一个同时被 S1 与 step3 启用的 DC 通道"
        )
    baselines = {channel: baseline_dc_values(ui, channel) for channel in channels}
    metas: List[Dict[str, Any]] = []
    for index, point in enumerate(profile, 1):
        if not point.get("enabled", True):
            continue
        pre = time_to_ticks(point["t_pre"], point["t_pre_unit"])
        dwell = time_to_ticks(point["t_dwell"], point["t_dwell_unit"])
        post = time_to_ticks(point["t_post"], point["t_post_unit"])
        repeats = int(point.get("repeats", 1))
        label = str(point.get("label") or "DynamicMPPT_%d" % index)
        for _repeat in range(repeats):
            if pre:
                out_rows.append(wait_row(pre))
            for channel in channels:
                code, commands, message = resolve_dynamic_dc_commands(
                    point,
                    baselines[channel],
                    channel - 1,
                    get_iv_fn=get_iv_fn,
                    per_dc_factor=per_dc_factor,
                    command_list_dc=command_list_dc,
                )
                if code != "ok" or not commands:
                    raise TimingProfileValidationError(
                        message or "DC%d 动态 MPPT 命令生成失败" % channel
                    )
                for command in commands:
                    out_rows.append(device_write_row("DC%d" % channel, command))
            if dwell:
                out_rows.append(wait_row(dwell))
            if post:
                out_rows.append(wait_row(post))
        metas.append(
            {
                "name": label,
                "index": index,
                "p_pct": point.get("p_pct"),
                "irr_wm2": point.get("irr_wm2"),
                "temp_c": point.get("temp_c"),
                "pmpp": point.get("pmpp"),
                "umpp": point.get("umpp"),
                "ff": point.get("ff"),
                "repeats": repeats,
                "channels": list(channels),
                "duration_01s": (pre + dwell + post) * repeats,
            }
        )
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


def build_dynamic_mppt_plan(
    ui: Any,
    *,
    get_iv_fn: Any = None,
    per_dc_factor: Optional[Mapping[str, str]] = None,
    command_list_dc: Optional[Mapping[str, Sequence[str]]] = None,
    wt_config_dict: Optional[Mapping[str, Any]] = None,
    str_add_flag: str = "0",
    project_change: str = "0",
    existing_commands: Optional[Iterable[Sequence[Any]]] = None,
    dc_iv_resolver: Any = None,
) -> Dict[str, Any]:
    """Build a ten-column plan, refusing unknown/unsupported DC brands."""

    factors = dict(per_dc_factor or {})
    command_modes = dict(command_list_dc or {})
    try:
        if dc_iv_resolver is None and get_iv_fn is not None:
            dc_iv_resolver = make_guarded_dc_iv_resolver(
                get_iv_fn, factors, command_modes
            )
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
            profile = read_ui_profile(ui, DYNAMIC_MPPT_SCHEMA)
            channels = selected_profile_dc_channels(ui)
            started = append_acquisition_start(context, profile_rows)
            metas = append_dynamic_mppt_profile(
                profile_rows,
                profile,
                ui=ui,
                channels=channels,
                get_iv_fn=get_iv_fn,
                per_dc_factor=factors,
                command_list_dc=command_modes,
            )
            append_acquisition_end(started, profile_rows)
        names = []
        for meta in metas:
            suffix = meta.get("p_pct")
            if suffix is None:
                suffix = meta.get("pmpp")
            names.append("DynamicMPPT_%s" % format_number(suffix))
        return finalize_plan(
            context,
            profile_rows,
            profile_metas=metas,
            file_names=names or ["DynamicMPPT"],
        )
    except (AttributeError, TypeError, ValueError, TimingProfileValidationError) as exc:
        return _error_result("动态 MPPT 计划生成失败: %s" % exc, existing_commands)


build_thai_dynamic_mppt_plan = build_dynamic_mppt_plan


__all__ = [
    "SUPPORTED_DYNAMIC_MPPT_BRANDS",
    "append_dynamic_mppt_profile",
    "build_dynamic_mppt_plan",
    "build_thai_dynamic_mppt_plan",
]
