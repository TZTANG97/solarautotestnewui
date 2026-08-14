# -*- coding: utf-8 -*-
"""Fail-closed Chroma 61830 three-phase angle-difference disturbances."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from utils.timing_profile import (
    PHASE_JUMP_SCHEMA,
    TimingProfileValidationError,
    time_to_ticks,
)
from utils.timing_profile_adapters import (
    ac_write_row,
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


# Repository evidence: scripts/pdf_network_pages.txt, extracted manual pages
# 8-18/8-19 (lines 1345-1376).  ON/OFF mean waveform start/end angles;
# P12/P13 mean Φ1→Φ2 and Φ1→Φ3 phase differences.  They are not Itech
# registers and must never be translated into guessed Modbus addresses.
CHROMA_61830_PHASE_EVIDENCE = (
    "scripts/pdf_network_pages.txt:1345-1376 "
    "(PHASe:ON/OFF start/end angle; PHASe:P12/P13 phase differences)"
)
SUPPORTED_AC_BRANDS = ("chroma", "chroma_ip")


def normalize_ac_brand(brand: Any) -> str:
    value = str(brand or "").strip().casefold().replace("-", "_")
    if value in SUPPORTED_AC_BRANDS:
        return "Chroma"
    if value in {"itech", "爱科"}:
        raise TimingProfileValidationError(
            "爱科 AC 缺少已证实的相角突变寄存器，已 fail closed"
        )
    if not value:
        raise TimingProfileValidationError(
            "AC 品牌未识别；相角突变仅允许已确认的 Chroma 61830"
        )
    raise TimingProfileValidationError(
        "AC 品牌 %r 缺少相角突变命令证据，已 fail closed" % brand
    )


def _angle(value: float) -> float:
    result = float(value) % 360.0
    if abs(result - 360.0) < 1e-9:
        result = 0.0
    return result


def chroma_phase_difference_commands(delta_deg: Any) -> Tuple[str, str]:
    """Shift Φ2 and Φ3 by one documented relative-angle delta."""

    delta = float(delta_deg)
    if not -180.0 <= delta <= 180.0:
        raise TimingProfileValidationError("phase_deg 必须在 -180..180°")
    return (
        "PHASe:P12 " + format_number(_angle(120.0 + delta)),
        "PHASe:P13 " + format_number(_angle(240.0 + delta)),
    )


def append_phase_jump_profile(
    out_rows: List[List[Any]],
    profile: Iterable[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    metas: List[Dict[str, Any]] = []
    for index, point in enumerate(profile, 1):
        if not point.get("enabled", True):
            continue
        delta = float(point["phase_deg"])
        pre = time_to_ticks(point["t_pre"], point["t_pre_unit"])
        dwell = time_to_ticks(point["t_dwell"], point["t_dwell_unit"])
        post = time_to_ticks(point["t_post"], point["t_post_unit"])
        repeats = int(point.get("repeats", 1))
        label = str(point.get("label") or "PhaseJump_%d" % index)
        event_commands = chroma_phase_difference_commands(delta)
        for _repeat in range(repeats):
            if pre:
                out_rows.append(wait_row(pre))
            for command in event_commands:
                out_rows.append(ac_write_row(command))
            if dwell:
                out_rows.append(wait_row(dwell))
            # Restore the documented balanced phase differences.
            out_rows.append(ac_write_row("PHASe:P12 120"))
            out_rows.append(ac_write_row("PHASe:P13 240"))
            if post:
                out_rows.append(wait_row(post))
        metas.append(
            {
                "name": label,
                "index": index,
                "phase_deg": delta,
                "repeats": repeats,
                "duration_01s": (pre + dwell + post) * repeats,
                "evidence": CHROMA_61830_PHASE_EVIDENCE,
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


def build_phase_jump_plan(
    ui: Any,
    *,
    ac_brand: Any = None,
    wt_config_dict: Optional[Mapping[str, Any]] = None,
    str_add_flag: str = "0",
    project_change: str = "0",
    existing_commands: Optional[Iterable[Sequence[Any]]] = None,
    dc_iv_resolver: Any = None,
) -> Dict[str, Any]:
    """Build a Chroma-only, ten-column phase-jump plan."""

    try:
        normalize_ac_brand(ac_brand)
        phase_mode, _nominal = baseline_ac_voltages(ui)
        if phase_mode != "三相":
            raise TimingProfileValidationError(
                "61830 P12/P13 是三相相位差命令；单相相角突变证据不足，已拒绝"
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
            profile = read_ui_profile(ui, PHASE_JUMP_SCHEMA)
            # These configure only the meanings documented in the local manual:
            # 0° next start angle and immediate next stop angle.  The live
            # disturbance itself uses P12/P13 below.
            profile_rows.append(ac_write_row("PHASe:ON 0"))
            profile_rows.append(ac_write_row("PHASe:OFF 360"))
            profile_rows.append(ac_write_row("PHASe:THREE SAMEFREQ"))
            started = append_acquisition_start(context, profile_rows)
            metas = append_phase_jump_profile(profile_rows, profile)
            append_acquisition_end(started, profile_rows)
        names = [
            "PhaseJump_%sdeg" % format_number(meta["phase_deg"]) for meta in metas
        ]
        return finalize_plan(
            context,
            profile_rows,
            profile_metas=metas,
            file_names=names or ["PhaseJump"],
        )
    except (AttributeError, TypeError, ValueError, TimingProfileValidationError) as exc:
        return _error_result("相角突变计划生成失败: %s" % exc, existing_commands)


build_thai_phase_jump_plan = build_phase_jump_plan


__all__ = [
    "CHROMA_61830_PHASE_EVIDENCE",
    "SUPPORTED_AC_BRANDS",
    "append_phase_jump_profile",
    "build_phase_jump_plan",
    "build_thai_phase_jump_plan",
    "chroma_phase_difference_commands",
    "normalize_ac_brand",
]
